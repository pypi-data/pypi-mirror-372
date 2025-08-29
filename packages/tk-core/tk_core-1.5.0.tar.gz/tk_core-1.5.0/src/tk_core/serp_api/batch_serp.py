"""
Class for batch SERP API requests
"""

import datetime
from collections import ChainMap
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from dotenv import load_dotenv
from rich import print

from tk_core.common.dates import datecode
from tk_core.common.de_service import DeService
from tk_core.common.dictionary import subset_dict
from tk_core.common.hasher import hash_from_dict, uri_string_from_dict
from tk_core.core.batch_request import BatchRequest
from tk_core.core.tk_redis import TKRedis
from tk_core.serp_api.models import SERPAPISearchParameters
from tk_core.serp_api.serp import get_serp_client
from tk_core.serp_api.util import extract_serpapi_params
from tk_core.snowkeet import Snowkeet

load_dotenv()


class BatchSERPAPISerps(BatchRequest):
    SOURCE_NAME_AND_VERSION = "tk_core_serp_api_batch_initiator"

    def __init__(
        self, queries: list, params: SERPAPISearchParameters, metadata: dict, setup_sub_objects: bool = True, **kwargs
    ) -> None:
        self.input_objects: list = queries
        self.job_params: SERPAPISearchParameters = params
        # create a dictionary version of the parameters
        # remove freshness_days as it isn't a variable we want to consider
        # when checking if we have cached results we can serve within the window provided
        self.memoized_params = self.job_params.model_dump()
        del self.memoized_params["freshness_days"]
        self.metadata: dict = metadata
        self.freshness_days = params.freshness_days
        self.input_objects_name = "queries"
        # validate freshness_days
        if self.freshness_days not in [0, 1, 30]:
            raise ValueError("freshness_days (days) must be 0, 1, or 30")

        self.run_date = int(datecode())
        self.executed_at = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
        self.indv_request_hash = None
        self.execution_id = None
        self.uri = None
        self.requests = []
        self.additional_requests = []
        self.results = []
        self.batch_execution_uuid = None
        self.created_by = "tk_core_serpapi_executor"
        self.minimum_date = self.run_date - self.freshness_days
        if setup_sub_objects:
            self.setup_special_sub_objects()

    def setup_special_sub_objects(self) -> None:
        self.de = DeService("serpapi")
        self.redis = TKRedis()

    def prepare_hash(self, params: dict | None = None) -> None:
        """
        Prepares more hashing information and metadata for later use
        """
        if params is not None:
            to_hash = subset_dict(params, ["tk_metadata"])
        else:
            to_hash = subset_dict(self.memoized_params, ["tk_metadata"])

        self.uri = uri_string_from_dict(to_hash)
        self.indv_request_hash = hash_from_dict(to_hash)

    def get_execution_id(self, request_hash: str | None = None) -> None:
        """
        Returns the execution ID based on the provided request hash.

        If a request hash is provided, the execution ID will be in the format
        "{request_hash}/{run_date}". If no request hash is provided, the execution ID
        will be in the format "{indv_request_hash}/{run_date}".

        Args:
            request_hash (str | None, optional): The request hash. Defaults to None.

        Returns:
            str: The execution ID.
        """
        if request_hash is not None:
            return f"{request_hash}/{self.run_date}"
        else:
            return f"{self.indv_request_hash}/{self.run_date}"

    def prepare_hash_and_metadata(self, params: dict | None = None) -> None:
        """
        Prepares more hashing information and metadata for later use
        """
        self.prepare_hash(params)
        return self.get_execution_id()

    def get_serps_new(self) -> dict:
        """ """
        # Step 1
        # this will prepare hashes for each set of parameters
        # as well as check which hashes are already cached in Redis
        # we get back 2 lists of hashes
        # TODO: does this need to be 2 lists of dictionaries? So we can make API requests from the hash?
        cached, needed = self.process_cache_checks()

        # Sub-step 1a - write to the audit log
        self.define_audit_table_output()
        self.write_audit_table()

        # TODO: step 2a and 2b could/should be concurrent
        # Step 2a - for cached, we need to updated snowflake with the new tags
        if cached:
            self.batch_update_snowflake(cached, "NEW_SEARCH_RESULTS", "EXECUTION_ID")

        # Step 2b - for needed, we need to run the requests
        if needed:
            self.batch_run_requests(needed)

        # Step 3 - return the formatted output for the end user
        return self.end_user_formatted_output_metadata("success", "NEW_SEARCH_RESULTS")

    def batch_run_requests(self, needed_hashes: list) -> None:
        """
        Main method to get SERP results for our list of queries
        Loops through queries and creates requests for each

        This is probably the method we want to remove from the class,
        and have the dask task call it process it concurrently

        I think we want to get this out of the class not not cause issues for a parallel run

        TODO: Solve the parallel run issue
        TODO: Better updating snowflake in batches

        Returns:
            dict: The results of the batch request


        120-128
        chunks into that many chunks
        1000 of requests at once (ish)
        """
        needed_queries = {h: q for h, q in self.hash_to_query.items() if h in needed_hashes}
        query_chunks = [list(needed_queries.items())[i : i + 10000] for i in range(0, len(needed_queries), 10000)]
        self.parallel_run_batch_request(query_chunks)

    def parallel_run_batch_request(self, query_chunks: list[list[tuple[str]]]) -> None:
        """
        Run the batch request in parallel using ThreadPoolExecutor
        """
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(self.process_one_chunk, query_chunks)

    def process_one_chunk(self, queries: list[tuple[str]]) -> None:
        current_data = pd.DataFrame()
        # Loop through queries and get results
        for hash_, query in queries:
            one_query_data = self.process_one_query(hash_, query)
            # Step 6 - write formatted data to snowflake
            current_data = pd.concat([current_data, pd.DataFrame(one_query_data)])
        self.write_to_snowflake(current_data)

    def process_one_query(self, hash_: str, query: str) -> None:
        # Step 1 - build the hash and metadata
        execution_id = self.get_execution_id(hash_)
        # Step 2 prep - reset the requests
        self.requests = []
        # Step 2 - create requests
        request_list = self.create_requests(query)
        # Step 3 - run the requests for that query
        results = self.run_jobs(request_list)
        # Step 4 - prepare the response for that query
        response = self.prepare_response(hash_, execution_id, results)
        # Step 5 - Update redis
        # Step 5a - update the cache location in redis
        self.redis.set_hash_from_dict(f"{type(self).__name__}_cache", {hash_: self.run_date})
        # Step 5b - send raw response to redis
        response["request_hash"] = hash_
        response["metadata"] = self.metadata
        self.redis.set_hash_from_nested_dict(f"{type(self).__name__}_raw", execution_id, response)

        return self.format_response_for_snowflake(query, hash_, response)

    def create_requests(self, query: str) -> None:
        """
        Step B1
        Determines the number of requests to create and sets up params for each one.

        Args:
            query (str): The search query.

        Returns:
            List[Dict[str, Union[Dict[str, Any], Dict[str, int]]]]: A list of request parameters.
        """
        my_requests = []
        page_count = self.job_params.page_count
        per_page = self.job_params.per_page
        for page_num in range(page_count):
            # convert params to serpapi proper params
            loaded_params = extract_serpapi_params(query, self.memoized_params, per_page, per_page * page_num, self.metadata)
            # build the request JSON
            request_params = {
                "query_params": loaded_params.model_dump(),
                "request_metadata": {
                    "page_number": page_num + 1,
                },
            }
            my_requests.append(request_params)
        return my_requests

    def run_jobs(self, request_list: list | None = None) -> None:
        """
        Step B2

        Loop through request parameters and run requests
        Assigns results to self.results

        Args:
            requests (list[dict]): List of prepared requests for execution

        Returns:
            None
        """

        request_list = request_list if request_list is not None else self.requests

        return [self.run_request(x) for x in request_list]

    def run_request(self, request_params: dict, metadata: dict | None = None) -> dict:
        """
        Run a single SERPAPI request

        Args:
            params (dict): The translates params for the executor

        Returns:
            str: The UTF-8 decoded request from the executor
        """
        if metadata is None:
            metadata = self.metadata

        s = get_serp_client(
            params=request_params["query_params"],
            request_metadata=metadata,
        )
        response = s._make_request()
        response["request_metadata"] = request_params["request_metadata"]

        # check for a bad response
        if response.get("serpapi_pagination") is None:
            print("Issue in initiator.run_request")
            raise ValueError(f"Bad response from SERP Api: {response}")

        formatted_response = {"response": response, "request_metadata": request_params["request_metadata"]}
        return formatted_response

    def prepare_response(self, request_hash: str, execution_id: str, results: list) -> dict:
        """
        Step B4

        Prepare the response for the user
        """
        pages = self.sort_and_renumber_pages(results)
        return {
            "execution_id": execution_id,
            "request_hash": request_hash,
            "request_metadata": results[0]["request_metadata"],
            "page_count": len(pages),
            "pages": pages,
            "errors": self.extract_errors(results),
        }

    def sort_and_renumber_pages(self, results: list) -> list:
        """
        Helper Function to prepare the response
        """
        sorted = self.sort_pages(results)
        # renumber the results (only the results, not request_metadata)
        return self.renumber_results(sorted)

    @staticmethod
    def sort_pages(results: list) -> list:
        """
        Request execution is asynchronous, so we need to sort the results
        """
        to_sort = [x for x in results if x["response"].get("serpapi_pagination") is not None]
        return sorted(to_sort, key=lambda x: x["request_metadata"]["page_number"])

    @staticmethod
    def renumber_results(sorted: list) -> list:
        """
        Helper Function
        Renumber the results to reflect the correct position
        """
        offset = 0
        for i, page in enumerate(sorted):
            raw_results = page["response"]
            if i > 0:
                for r, result in enumerate(raw_results["organic_results"]):
                    result["calculated_position"] = result["position"] + offset
                    raw_results["organic_results"][r] = result
                sorted[i] = raw_results
            else:
                for r, result in enumerate(raw_results["organic_results"]):
                    result["calculated_position"] = result["position"]
                    raw_results["organic_results"][r] = result
                sorted[i] = raw_results
            offset = offset + raw_results["organic_results"][-1]["position"]

        return sorted

    @staticmethod
    def extract_errors(results: list) -> list:
        """
        Pull errors from SERP API Executor
        """
        # todo - need to get metadata for the page that failed from the executor.
        return [x for x in results if x["response"].get("serpapi_pagination") is None]

    def format_response_for_snowflake(
        self, query: str, hash_: str, response: dict, metadata: dict | None = None, run_date: str | None = None
    ) -> list:
        """
        Format the response for snowflake
        """
        defaults = self.serpapi_default_dict()
        search_results_rows = []
        metadata = metadata if metadata is not None else self.metadata
        run_date = run_date if run_date is not None else self.run_date

        # loop through each page of results
        for p in response.get("pages", []):
            # loop through all organic positions
            for org_res in p.get("organic_results", []):
                # create a new result
                # add tags from metadata
                # add in page number from request_metadata
                # add in the query
                # add in the hash
                # add in the request_id (global ID from the batch request)
                result = {
                    "METADATA": metadata,
                    "PAGE_NUM": p.get("request_metadata", {}).get("page_number", -1),
                    "QUERY": query,
                    "REQUEST_HASH": hash_,
                    "EXECUTION_ID": f"{hash_}/{run_date}",
                    "REQUEST_RUN_DATE": f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
                }
                # add in all the other fields we need
                for k in defaults:
                    result[k.upper()] = org_res.get(k, defaults[k])
                # save everything to a list
                search_results_rows.append(result)

        return search_results_rows

    @staticmethod
    def write_to_snowflake(data: pd.DataFrame) -> None:
        """
        write pandas to snowflake using snowkeet

        We use .reset_index(drop=True) to avoid the pandas error of a non standard index
        """
        right_now = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
        data["CREATED_AT"] = right_now
        data["UPDATED_AT"] = right_now
        with Snowkeet() as snow:
            snow.write_to_snowflake(data.reset_index(drop=True), "NEW_SEARCH_RESULTS")

    @staticmethod
    def serpapi_default_dict() -> dict:
        VARCHAR_COLUMNS = [
            "about_page_link",
            "about_page_serpapi_link",
            "cached_page_link",
            "calculated_position",
            "date",
            "displayed_link",
            "link",
            "position",
            "related_pages_link",
            "snippet",
            "thumbnail",
            "title",
            "video_link",
        ]
        VARIANT_COLUMNS = [
            "about_this_result",
            "carousel",
            "displayed_results",
            "images",
            "must_include",
            "related_results",
            "rich_snippet",
            "rich_snippet_list",
            "rich_snippet_table",
            "sitelinks",
        ]
        BOOL_COLUMNS = ["sitelinks_search_box"]
        LIST_COLUMNS = [
            "snippet_highlighted_words",
            "key_moments",
            "missing",
            "related_questions",
        ]
        varchar_cols = {d: "" for d in VARCHAR_COLUMNS}
        variant_cols = {d: None for d in VARIANT_COLUMNS}
        bool_cols = {d: False for d in BOOL_COLUMNS}
        list_cols = {d: [] for d in LIST_COLUMNS}
        return dict(ChainMap(*reversed([varchar_cols, variant_cols, bool_cols, list_cols])))

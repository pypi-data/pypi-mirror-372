import logging
from urllib.parse import urlparse

import ujson as json
from pydantic import BaseModel
from tk_core.common.dates import datecode
from tk_core.core.async_module.models import GenericAsyncRequest
from tk_core.core.base_request import TerakeetRequest
from tk_core.core.memory import print_memory_usage
from tk_core.core.tk_redis import TKRedis
from tk_core.snowkeet import Snowkeet
from tk_core.urls import InvalidUrlException, URLNormalizer

logger = logging.getLogger(__name__)

INVALID_EXTENSIONS = [
    ".jpg",  # JPEG image files
    ".jpeg",  # JPEG image files
    ".png",  # Portable Network Graphics image files
    ".gif",  # Graphics Interchange Format image files
    ".ico",  # Icon files
    ".pdf",  # Portable Document Format files
    ".svg",  # Scalable Vector Graphics files (often treated as binary)
    ".mp4",  # MPEG-4 video files
    ".webm",  # WebM video files
    ".mp3",  # MPEG-3 audio files
    ".woff",  # Web Open Font Format files
    ".woff2",  # Web Open Font Format files
    ".ttf",  # TrueType Font files
    ".otf",  # OpenType Font files
    ".eot",  # Embedded OpenType Font files
    ".bmp",  # Bitmap image files
    ".tiff",  # Tagged Image File Format
    ".tif",  # Tagged Image File Format
    ".avi",  # Audio Video Interleave files
    ".mov",  # QuickTime Movie files
    ".flv",  # Flash Video files
    ".mkv",  # Matroska Video files
    ".ogg",  # Ogg Vorbis audio files
    ".wav",  # Waveform Audio files
    ".zip",  # Compressed archive files
    ".rar",  # RAR archive files
    ".7z",  # 7-Zip archive files
    ".tar.gz",  # Compressed archive files
    ".tgz",  # Compressed archive files
    ".exe",  # Executable files
    ".dll",  # Dynamic Link Library files
    ".bin",  # Binary files
    ".dmg",  # Apple Disk Image files
    ".iso",  # ISO disk image files
    ".css",  # Cascading Style Sheets files
    ".js",  # JavaScript files
]


class BatchRequest(TerakeetRequest):
    """
    Base class for batch requests
    Diagram: https://lucid.app/lucidchart/48d77f3c-6aa4-401f-9e08-dfa9fc679d55/edit
    """

    def __init__(self, params: GenericAsyncRequest, input_objects_name: str) -> None:
        # extract params and metadata
        self.job_params = params.job_params
        self.metadata = params.metadata
        self.input_objects = params.input_objects
        self.input_objects_name = input_objects_name
        # Convert the parameters into a dictionary representation.
        # We exclude 'freshness_days' from this process because it's not a factor in determining
        # if we have cached results that can be served within the given window.
        # Essentially, we want two identical requests with different 'freshness_days' values
        # to produce the same hash.
        if isinstance(self.job_params, BaseModel):
            self.memoized_params = self.job_params.model_dump().copy()
        else:
            self.memoized_params = self.job_params.copy()

        del self.memoized_params["freshness_days"]
        # validate freshness_days which would be in the tk_metadata
        freshness_days = self.job_params.get("freshness_days")
        if freshness_days not in [0, 1, 30]:
            raise ValueError("freshness_days (days) must be 0, 1, or 30")
        else:
            self.freshness_days = freshness_days

        # set the minimum date (today - freshness_days)
        self.minimum_date = int(datecode()) - self.freshness_days

        # create redis object
        self.redis = TKRedis()

        # create a dictionary of hashes
        self.hash_to_parameters: dict | None = None

        self.invalid_urls = []

    def get_execution_id(self, request_hash: str | None = None) -> None:
        if request_hash is not None:
            return f"{request_hash}/{self.run_date}"
        else:
            return f"{self.indv_request_hash}/{self.run_date}"

    def generate_hashes_for_parameters(self) -> tuple[list]:
        """
        Step 1
        separate hash lists into cached/needed
        """
        print_memory_usage("Before Hash Generation")
        # TODO: make this quicker? less variables maybe?
        combined_params = self.combine_inputs_and_params()
        # make a dictionary of all hashes to their parameters
        # we will need the actual params later if we need to make a request
        self._generate_request_hashes(combined_params)
        return list(self.hash_to_query.keys())

    def combine_inputs_and_params(self) -> list:
        """
        Step 1-a
        Combines an item (initially `query`) from the input_objects + job_params into a list of dictionaries
        """
        print_memory_usage("Combine Inputs and Parameters")
        request_parameters = []
        job_params = self.memoized_params
        logger.info(f"{job_params.keys()=}")
        logger.info(f"{len(self.input_objects)=}")
        for item in self.input_objects:
            temp_params = job_params.copy()
            temp_params[self.input_objects_name] = item
            request_parameters.append(temp_params)

        logger.info(f"{len(request_parameters)=}")
        return request_parameters

    def _generate_request_hashes(self, list_of_parameters: list) -> dict:
        """
        Step 1-b
        given a list of parameters, make their hashes and assign to a dictionary
        mapping the hash to the query
        """
        print_memory_usage("Generating Request Hashes")
        self.hash_to_query = {
            self.make_request_hash(f"tk_core.{type(self).__name__}", params): params[self.input_objects_name]
            for params in list_of_parameters
        }

    def lookup_existence_of_cache(self, list_of_hashes: list, hash_name: str = None) -> tuple[list]:
        """
        Step 2: Lookup Existence of Cache

        This method checks the Redis stack for cached results based on a list of hashes.
        It performs the following steps:
        1. Prints the memory usage before checking the cache.
        2. Calls the `batch_check_redis_for_cache` method to retrieve the keys associated with the given hashes.
        3. Separates the cached keys from the needed keys using the `separate_cached_vs_needed` method.

        Args:
            list_of_hashes (list): A list of hashes to check in the Redis stack.
            hash_name (str): The name of the hash in Redis. Defaults to None.

        Returns:
            tuple[list]: A tuple containing two lists - the cached keys and the needed keys.
        """
        print_memory_usage("Before Cache Check")
        keys = self.batch_check_redis_for_cache(list_of_hashes, hash_name)
        return self.separate_cached_vs_needed(keys, list_of_hashes)

    def batch_check_redis_for_cache(self, list_of_hashes: list, hash_name: str = None) -> list:
        """
        Step 2-a
        Checks the Redis stack for cached results.

        This method takes a list of hashes and checks the Redis stack for cached results corresponding to each hash.
        It returns a list of values retrieved from the Redis stack.

        Args:
            list_of_hashes (list): A list of hashes to check in the Redis stack.
            hash_name (str): The name of the hash in Redis. Defaults to the name of the class current instance
            belongs to (with the "_cache" postfix).

        Returns:
            list: A list of values retrieved from the Redis stack.
        """
        print_memory_usage("Checking Redis for Cache")
        hash_name = hash_name or f"{type(self).__name__}_cache"
        return self.redis.get_hash_values_from_list_with_pipe(data=list_of_hashes, hash_name=hash_name)

    def separate_cached_vs_needed(self, keys: list, list_of_hashes: list) -> tuple[list]:
        """
        Step 2-b
        Separates the cached items from the needed items.

        This method takes in a list of keys and a list of hashes and separates them into two categories:
        cached and needed. The cached items are determined based on the freshness_days and minimum_date
        properties of the object. If a key is not empty, freshness_days is greater than 0, and the key is
        greater than or equal to the minimum_date, the item is considered cached. Otherwise, it is considered
        needed.

        Args:
            keys (list): A list of keys corresponding to the hashes.
            list_of_hashes (list): A list of hashes.

        Returns:
            tuple[list]: A tuple containing two lists: cached and needed.

        TODO: Create a lucid chart diagram to visualize the separation process.
        """
        print_memory_usage("Separating Cached vs Needed")
        cached = []
        needed = []
        for h, k in zip(list_of_hashes, keys):
            if k and self.freshness_days > 0 and int(k) >= self.minimum_date:
                # Append execution IDs to the cached list
                cached.append(f"{h}/{int(k)}")
            else:
                needed.append(h)

        return cached, needed

    def set_cached_results_count(self, count: int) -> None:
        """
        Sets the count of cached results
        """
        self.cached_results_count = count

    def set_needed_results_count(self, count: int) -> None:
        """
        Sets the count of needed results
        """
        self.needed_results_count = count

    def process_cache_checks(self, hash_name: str = None) -> tuple[list, list]:
        """
        Main flow for batch query jobs:
        1. Generates hashes for the parameters of the batch query jobs.
        2. Looks up the existence of these hashes in the cache.
        3. Sets the count of cached results and the count of needed results.

        It's the main method to call when you want to perform a batch of query jobs and check the cache
        before fetching or calculating the results.

        Args:
            hash_name (str): The name of the hash in Redis. Defaults to None.

        Returns:
            tuple: A tuple containing two lists. The first list contains the cached results,
            and the second list contains the results that need to be fetched or calculated.
        """
        print_memory_usage("Before Cache Checks")
        # Step 1
        hashed_requests = self.generate_hashes_for_parameters()
        # Step 2
        cached, needed = self.lookup_existence_of_cache(hashed_requests, hash_name)
        # Step 2-metadata add
        self.set_cached_results_count(len(cached))
        self.set_needed_results_count(len(needed))

        return cached, needed

    def batch_update_snowflake(
        self,
        cached_execution_ids: list[str],
        table_name: str,
        filter_var: str = "EXECUTION_ID",
    ) -> None:
        """
        Batch update the tags in Snowflake for the given execution IDs.

        Args:
            cached_execution_ids (list[str]): List of execution IDs to update.
            table_name (str): Name of the table in Snowflake to update.
            filter_var (str, optional): Column name to filter the update on. Defaults to "EXECUTION_ID".

        Returns:
            None
        """
        # TODO: Figure out this query to merge on variant data
        # INSTEAD OF MERGE TRY UPDATE
        # query = "MERGE NEW_TAGS N INTO REQUEST_CACHE C ON C.REQUEST_HASH = N.REQUEST_HASH"
        # TODO: move it into snowflake entirely
        # chunk the execution ids into groups of 16,000
        cached_execution_id_chunks = [
            tuple(cached_execution_ids[i : i + 16000]) for i in range(0, len(cached_execution_ids), 16000)
        ]
        with Snowkeet() as snow:
            for execution_id_chunk in cached_execution_id_chunks:
                # update snowflake
                """
                update_tags in snowflake as UDF
                send new_tags as a string
                """
                query = f"""UPDATE IDENTIFIER(?) 
                SET METADATA = update_metadata(METADATA,?), 
                        UPDATED_AT = CURRENT_TIMESTAMP()
                    WHERE IDENTIFIER(?) IN {execution_id_chunk}
                    """  # noqa S068
                update_results = snow.session.sql(
                    query, params=(table_name, str(json.dumps(self.metadata)), filter_var, str(execution_id_chunk))
                ).collect()
                logger.info(update_results[0].as_dict())

    def send_raw_response_to_redis(self, request_hash: str, service_name: str, response: dict) -> None:
        """
        Send the raw response to redis
        """
        self.redis.set_hash_from_dict(service_name, {request_hash: response})

    def canonicalize_and_validate(self) -> None:
        """
        cannonicalize and validate a URL

        This method resets the input_objects to only contain valid URLs and their components
        It also populates the invalid_urls list with any URLs that were invalid
        """
        self.raw_inputs = self.input_objects.copy()
        self.input_objects = []
        for url in self.raw_inputs:
            try:
                # attempt to canonicalize the URL
                # if it fails, add it to the invalid_urls list
                url_obj = self.canonicalize_url(url)
                if self.is_valid_url(url_obj["normalized_url"]):
                    # any good canonicalized URL is tested against the invalid extensions
                    self.input_objects.append(url_obj)
                else:
                    self.invalid_urls.append(url_obj["normalized_url"])
            except InvalidUrlException:
                # canonicalization raised and exception
                self.invalid_urls.append(url)
        logger.info(f"Canonicalization performed on {len(self.raw_inputs)} URLs.")
        logger.info(f"Valid URLs: {len(self.input_objects)}")
        logger.info(f"Invalid URLs: {len(self.invalid_urls)}")

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Returns True if the URL has a valid subdomain, False otherwise
        """
        if not url.startswith("http"):
            url = f"https://{url}"
        return not any(
            urlparse(url).netloc.endswith(invalid_extension) or url.endswith(invalid_extension)
            for invalid_extension in INVALID_EXTENSIONS
        )

    @staticmethod
    def canonicalize_url(url: str) -> dict:
        """
        canonicalize a url and pass multiple components back
        """
        # TODO: IMPLEMENT THIS
        # remove any duplicates after canonicalizing the URLS
        normalizer = URLNormalizer(url)
        urls = normalizer.to_dict()
        data = {
            "original_url": normalizer.original_url,
            "normalized_url": urls["normalized_url"],
            "unique_params": normalizer.unique_params,
        }
        return data

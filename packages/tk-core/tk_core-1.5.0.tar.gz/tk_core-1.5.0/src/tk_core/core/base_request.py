from os import environ

import pandas as pd
from tk_core.common.dictionary import subset_dict
from tk_core.common.hasher import hash_from_dict
from tk_core.core.async_module.models import GenericAsyncRequest
from tk_core.core.models import AuditTableOutput
from tk_core.core.request_id import PostInitMetaclass
from tk_core.snowkeet import Snowkeet


class TerakeetRequest(metaclass=PostInitMetaclass):
    def __init__(self, params: GenericAsyncRequest) -> None:
        # set the parameters
        self.job_params = params.job_params
        # extract metadata
        self.metadata = params.metadata
        # build request hash from params
        self.request_hash = self.make_request_hash(f"tk_core.{type(self).__name__}", self.job_params.model_dump())

    def __post_init__(self) -> None:
        """
        because of the metaclass, this is called after __init__
        This is used incase a future class needs to override the __init__ method
        We still need these things to take place
        """
        # extract request_id
        self.request_id = self.metadata["request_id"]
        # extract request_time
        self.request_time = self.metadata["request_timestamp"]
        # extract consumer
        self.consumer = self.metadata["consumer"]
        # set results for cached/needed to None
        self.cached_results_count = None
        self.needed_results_count = None
        # clean up the tags in metadata making sure they are lists
        self.clean_up_metadata_tags()
        # define the output for audit table as Pydantic model
        self.define_audit_table_output()

    @staticmethod
    def make_request_hash(request_service: str, request_parameters: dict) -> str:
        """
        Generates a hash from the request parameters
        Does not consider the metadata an important parameter
        """
        if "metadata" in request_parameters:
            important_parameters = subset_dict(request_parameters, ["metadata"])
        else:
            important_parameters = request_parameters
        # add the service as an element to cache (we don't want to match on different services)
        request_parameters["request_service"] = request_service
        return hash_from_dict(important_parameters)

    def clean_up_metadata_tags(self) -> None:
        """
        Makes all request tags (from metadata) as lists
        """
        self.metadata = {k: v if isinstance(v, list) else [v] for k, v in self.metadata.items()}

    def write_audit_table(self) -> None:
        with Snowkeet() as snow:
            snow.write_to_snowflake(self.output_audit_table_dataframe(), "request_audit")

    def define_audit_table_output(self) -> None:
        """
        Creates an instance of the AuditTableOutput class, populates and returns it.

        Returns:
            AuditTableOutput: The audit table output object containing the request information.
        """
        params = self.job_params
        if not isinstance(self.job_params, dict):
            params = self.job_params.model_dump()
        self.audit_table_output = AuditTableOutput(
            consumer_application=self.metadata["consumer"][0],
            request_metadata=self.metadata,
            request_id=self.request_id,
            client_code=self.metadata.get("client_code", ["DEFAULT_CLIENT"])[0],
            processing_application=f"tk_core.{type(self).__name__}",
            request_time=self.request_time,
            cached_results=self.cached_results_count,
            needed_results=self.needed_results_count,
            errors=False,
            job_params=params,
        )
        return self.audit_table_output

    def end_user_formatted_output_metadata(self, status: str, table_name: str) -> dict:
        """
        Format the output metadata for end users.

        This method is designed to format the output metadata in a way that provides
        information to the end users about the location of their data once the request
        is complete.

        Args:
            status (str): The status of the job.
            table_name (str): The name of the table where the data can be found.

        Returns:
            dict: A dictionary containing the formatted output metadata. The dictionary
            has the following structure:

            {
                "job_status": <status>,
                "job_info": {
                    "cached_results": <cached_results>,
                    "pulled_results": <needed_results>
                },
                "request_location": <location>
            }
        """
        md = self.audit_table_output
        return {
            "job_status": status,
            "job_info": {
                "cached_results": md.cached_results,
                "pulled_results": md.needed_results,
            },
            "request_location": f"{environ['SNOWFLAKE_DB']}.{environ['SNOWFLAKE_SCHEMA']}.{table_name}",
        }

    def output_audit_table_dataframe(self) -> pd.DataFrame:
        """
        Returns a pandas DataFrame containing the dict representation of the audit_table_output.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the model dump of the audit table output.
        """
        return pd.DataFrame([self.audit_table_output.model_dump()])

    def get_tags_as_lists(self) -> None:
        """
        Makes all request tags (from metadata) as lists
        """
        return {k: v if isinstance(v, list) else [v] for k, v in self.audit_table_output.request_metadata.items()}

import logging
import uuid
from datetime import datetime

from botocore.exceptions import BotoCoreError
from pydantic import BaseModel

from tk_core.common.s3 import S3Util
from tk_core.core.async_module.models import GenericAsyncRequest, TamParameters
from tk_core.gp.models import GrowthProjectionsParameters
from tk_core.page_restructuring.models import PageRestructuringParameters
from tk_core.page_scrape.models import ScrapingBeeParameters
from tk_core.prefect.prefect_api import Prefect
from tk_core.serp_api.models import SERPAPISearchParameters

REQUEST_DIRECTORY = {
    "serp": "batch_serp",
    "serp_dev": "batch_serp_dev",
    "tam": "tam",
    "tam_dev": "tam_dev",
}


class DeploymentNotFoundError(Exception):
    pass


class InputObjectsNotFoundError(Exception):
    pass


class GenericRequestProcessor:
    """
    Initialize the GenericRequestProcessor responsible for routing the GenericAsyncRequest to the Prefect API.

    Args:
        payload (GenericAsyncRequest): The payload for the request.
        batch_limit (int, optional): The limit for batching requests. Defaults to 1000.
    """

    def __init__(self, payload: GenericAsyncRequest, batch_limit: int = 1000):
        if isinstance(payload, dict):
            payload = GenericAsyncRequest.model_validate(payload)
        self.payload = payload
        self.input_objects_count = len(self.payload.input_objects) if self.payload.input_objects else 0
        self.batch_limit = batch_limit
        self.prefect = Prefect()
        self.s3 = S3Util()
        logging.info(
            f"""
            GenericRequestProcessor initialized with payload: {payload.model_dump().keys()};
            batch_limit: {self.batch_limit};
            """
        )

    def process_request(self) -> GenericAsyncRequest:
        """
        High-level method that orchestrates routing the GenericAsyncRequest to the Prefect API.

        Returns:
            GenericAsyncRequest: The processed request.
        """
        self._validate_job_params()
        self._enrich_metadata()
        # convert the input_objects to S3 if it exceeds the batch_limit
        if self.payload.job_name.startswith("batch"):
            self._batch_request()
        self._trigger_prefect_flow(tags=self._define_any_tags())

        # update the input_objects to be a count in the payload
        self.payload.input_objects = str(self.input_objects_count)

        return self.payload

    def _check_input_objects(self) -> None:
        """
        Check if the input_objects are present in the payload.
        """
        if self.input_objects_count == 0:
            raise InputObjectsNotFoundError("No input_objects found in the payload")

    def _validate_job_params(self) -> None:
        """
        Validate the job_params of the payload depending on the job_name.
        """
        job_params = self.payload.job_params
        # BATCH SERP VALIDATION
        if "batch_serp" in self.payload.job_name:
            self.payload.job_params = SERPAPISearchParameters.model_validate(job_params)
            self._check_input_objects()
        # TAM VALIDATION
        elif "tam" in self.payload.job_name:
            self.payload.job_params = TamParameters.model_validate(job_params)
        # PAGE RESTRUCTURING VALIDATION
        elif "batch_page_restructuring" in self.payload.job_name:
            self.payload.job_params = PageRestructuringParameters.model_validate(job_params)
            self._check_input_objects()
        # PAGE SCRAPE VALIDATION
        elif "batch_page_scrape" in self.payload.job_name:
            self.payload.job_params = ScrapingBeeParameters.model_validate(job_params)
            self._check_input_objects()
        # GP VALIDATION
        elif "gp_phase" in self.payload.job_name:
            self.payload.job_params = GrowthProjectionsParameters.model_validate(job_params)
        else:
            logging.warning(f"Skipping job_params validation, unknown job_name: {self.payload.job_name}")
            return
        logging.info(f"Validated job_params for job_name: {self.payload.job_name}")

    def _batch_request(self) -> None:
        """
        Batch the request if the count of input_objects exceeds the batch_limit.
        """
        if self.payload.input_objects and len(self.payload.input_objects) > self.batch_limit:
            logging.info(f"Converting input_objects to S3 due to size: {self.input_objects_count}")
            s3_key = f"submitted_job/input_objects/{self.payload.metadata.get('request_id')}.json"
            try:
                self.s3.write_json(s3_key, self.payload.input_objects)
                self.payload.input_objects = f"s3://{self.s3.bucket_name}/{s3_key}"
                logging.info(f"Saved input_objects to S3: {self.payload.input_objects}")
            except BotoCoreError as e:
                logging.error(str(e))

    def _enrich_metadata(self) -> None:
        """
        Enrich the metadata of the payload with the request_timestamp and request_id.
        """
        # If our input request JSON already has a request_id, we assign the parent_request_id
        # field and then will create a new request_id for this run
        parent_request_id = self.payload.metadata.get("request_id")
        if parent_request_id:
            self.payload.metadata["parent_request_id"] = parent_request_id

        self.payload.metadata["request_timestamp"] = datetime.now().isoformat()
        self.payload.metadata["request_id"] = str(uuid.uuid4())

    def _define_any_tags(self) -> list[str]:
        """
        Define the tags for the Prefect flow run.

        Returns:
            list[str]: The tags for the flow run.
        """
        tags = []
        # TAM ID Tag
        if self.payload.metadata.get("tam_id"):
            tags.append(self.payload.metadata["tam_id"])
        # Any other tag found in metadata
        if self.payload.metadata.get("prefect_tags"):
            tags.extend(self.payload.metadata.get("prefect_tags"))

        return tags

    def _get_deployment_from_job_name(self, job_name: str | None = None) -> str:
        """
        Maps the job_name to the corresponding deployment name.

        Args:
            job_name (str): The name of the job.

        Returns:
            str: The name of the deployment from directory.
        """
        if not self.payload.job_name:
            return REQUEST_DIRECTORY.get(job_name, job_name)
        # # get the deployment name for batch_serp_small if we have a list of input_objects instead of a string
        # if "batch_serp" in self.payload.job_name and isinstance(self.payload.input_objects, list):
        #     if "dev" in self.payload.job_name:
        #         self.payload.job_name = "batch_serp_small_dev"
        #         return "batch_serp_small_dev"
        #     self.payload.job_name = "batch_serp_small"
        #     return "batch_serp_small"
        return REQUEST_DIRECTORY.get(self.payload.job_name, self.payload.job_name)

    def _map_deployment(self) -> tuple[str] | tuple[None]:
        """
        Map the deployment based on the job_name in the request payload.

        Returns:
            str | None: The id of the matching deployment if found, else None.
        """
        deployments = self.prefect.get_deployments()

        # Iterate over the deployments to find the one with the matching flow_name
        for deployment in deployments:
            if deployment["name"] == self._get_deployment_from_job_name():
                # Return the id of the matching deployment
                return deployment["id"], deployment["required_params"]

        # If no matching deployment is found, log an error and return None
        logging.error(f"Deployment not found for job_name: {self.payload.job_name}")
        raise DeploymentNotFoundError(f"Deployment not found for job_name: {self.payload.job_name}")

    def _trigger_prefect_flow(self, tags: list[str] = None) -> dict:
        """
        Trigger the Prefect flow run from the deployment.

        Args:
            tags (list[str], optional): A list of tags to associate with the flow run. Defaults to None.

        Returns:
            dict: Info about the flow run submitted to Prefect.
        """
        # get the id and required params of the deployment
        deployment_id, deployment_params = self._map_deployment()

        # if we need to embed the params inside generic_request do so here
        if "generic_request" in deployment_params:
            flow_params = {"generic_request": self.payload.model_dump()}
        elif isinstance(self.payload.job_params, BaseModel):
            flow_params = self.payload.job_params.model_dump()
        elif isinstance(self.payload.job_params, dict):
            flow_params = self.payload.job_params

        logging.info(f"Triggering flow run for deployment_id: {deployment_id}")
        logging.info(f"Flow params: {flow_params}")
        flow_run = self.prefect.create_flow_run_from_deployment(
            deployment_id=deployment_id,
            parameters=flow_params,
            tags=tags,
            idempotency_key=self.payload.metadata.get("request_id"),
        )
        # simplify the information that end users need
        # only giving them the flow_run id and name
        self.payload.metadata["flow_run_id"] = flow_run["id"]
        self.payload.metadata["flow_run_name"] = flow_run["name"]
        return flow_run

import datetime as dt
import logging
import os

import requests
from dotenv import load_dotenv
from requests.exceptions import HTTPError, Timeout
from retry import retry

load_dotenv()
logger = logging.getLogger(__name__)


class Prefect:
    def __init__(
        self,
        account_id: str = None,
        workspace_id: str = None,
        api_version: str = None,
    ) -> None:
        self.raw_deployments = None
        self.account_id = account_id or os.environ["PREFECT_ACCOUNT_ID"]
        self.workspace_id = workspace_id or os.environ["PREFECT_WORKSPACE_ID"]
        self.api_version = api_version or "0.8.4"
        self._request_timeout = 20

        if self.account_id and self.workspace_id:
            self.base_url = f"https://api.prefect.cloud/api/accounts/{self.account_id}/workspaces/{self.workspace_id}"
        else:
            raise ValueError(
                f"account_id ({self.account_id}) and workspace_id ({self.workspace_id}) must be passed in, "
                "or set as environment variables. "
                "If set as environment variables use 'PREFECT_ACCOUNT_ID' and 'PREFECT_WORKSPACE_ID'"
            )

    def _url(self, endpoint: str) -> str:
        return f"{self.base_url}/{endpoint}"

    def set_api_version(self, version: str) -> None:
        self.api_version = version

    def build_request_header(self) -> dict:
        return {
            "Authorization": f"Bearer {os.environ['PREFECT_API_KEY']}",
            "x-prefect-api-version": self.api_version,
            "content-type": "application/json",
        }

    @retry(exceptions=(HTTPError, Timeout), tries=3, delay=2, backoff=2)
    def make_request(
        self,
        method: str,
        endpoint: str,
        header: dict = None,
        request_body: dict = None,
    ) -> dict:
        """
        Makes a request to the specified endpoint with the provided header and request body.

        Args:
            method (str): The HTTP method for the request.
            endpoint (str): The endpoint to which the request is made.
            header (dict, optional): The headers for the request. Defaults to None.
            request_body (dict, optional): The body of the request. Defaults to None.

        Returns:
            dict: The response from the request if successful, otherwise raises an exception.
        """
        if header is None:
            header = self.build_request_header()
        logging.info(f"Calling: {self._url(endpoint)}")
        try:
            if method.lower() == "post":
                response = requests.post(
                    self._url(endpoint),
                    headers=header,
                    json=request_body,
                    timeout=self._request_timeout,
                )
            elif method.lower() == "get":
                response = requests.get(
                    self._url(endpoint),
                    headers=header,
                    timeout=self._request_timeout,
                )
            else:
                raise ValueError(f"Unsupported method: {method}")
            response.raise_for_status()  # This will raise HTTPError for 400 status code
            return response.json()
        except Timeout:
            logging.error("Request timed out, retrying...")
            raise
        except HTTPError as http_err:
            if str(response.status_code)[0] == "4":  # 4xx codes
                logging.error(f"Received {response.status_code} status code, retrying...")
                raise
            else:
                logging.error(f"An HTTP error occurred: {http_err}")
                raise

    def create_flow_run_from_deployment(
        self,
        deployment_id: str,
        message: str = None,
        data: dict = None,
        schedule_time: dt.datetime = None,
        flow_run_name: str = None,
        parameters: dict = None,
        idempotency_key: str = None,
        tags: list[str] = None,
    ) -> dict:
        """
        Creates a flow run from a deployment.

        Args:
            deployment_id (str): The ID of the deployment.
            message (str, optional): The message for the flow run. Defaults to None.
            data (dict, optional): The data for the flow run. Defaults to None.
            schedule_time (dt.datetime, optional): The scheduled time for the flow run. Defaults to None.
            flow_run_name (str, optional): The name of the flow run. Defaults to None.
            parameters (dict, optional): The parameters for the flow run. Defaults to None.
            idempotency_key (str, optional): The idempotency key for the flow run. Defaults to None.
            tags (list[str], optional): The tags for the flow run. Defaults to None.

        Returns:
            dict: The response from the request to create the flow run.
        """
        # If tags is None, set it to the default value
        if not tags:
            tags = ["from_prefect_cloud_api"]
        else:
            tags.append("from_prefect_cloud_api")

        body = {
            "state": {
                "type": "SCHEDULED",
                "name": "Scheduled",
                "message": message,
                "data": data,
                "state_details": {
                    "scheduled_time": schedule_time,
                    "cache_key": "string",
                    "cache_expiration": schedule_time,
                    "untrackable_result": False,
                    "pause_timeout": schedule_time,
                    "pause_reschedule": False,
                    "pause_key": "string",
                    "refresh_cache": True,
                },
                "timestamp": schedule_time,
            },
            "name": flow_run_name,  # will default to random name if left blank
            "parameters": parameters,
            "context": {},
            "empirical_policy": {
                "retries": 0,
                "retry_delay": 0,
            },
            "tags": tags,
            "idempotency_key": idempotency_key,
            "work_queue_name": "default",
        }

        endpoint = f"deployments/{deployment_id}/create_flow_run"
        _method = "post"
        return self.make_request(method=_method, endpoint=endpoint, request_body=body)

    def work_queue_status(self, work_queue_id: str) -> dict:
        """
        Retrieves the status of a work queue.

        Args:
            work_queue_id (str): The ID of the work queue.

        Returns:
            dict: The status of the work queue.
        """
        endpoint = f"work_queues/{work_queue_id}/status"
        _method = "post"
        return self.make_request(method=_method, endpoint=endpoint)

    def parse_deployments(self) -> list:
        """
        Parses the raw deployments' data.

        Returns:
            list: A list of parsed deployments.
        """
        return [
            {
                "name": x["name"],
                "flow_name": x["entrypoint"].split(":")[1],
                "id": x["id"],
                "required_params": x["parameter_openapi_schema"].get("required", []),
                "work_pool": x["work_pool_name"],
                "work_queue": x["work_queue_name"],
            }
            for x in self.raw_deployments
        ]

    def get_deployments(self, parse: bool = True) -> list:
        """
        Retrieves deployments.

        Args:
            parse (bool, optional): Whether to parse the deployments' data. Defaults to True.

        Returns:
            list: A list of deployments. If parse is True, the deployments are parsed.
        """
        endpoint = "deployments/filter"
        _method = "post"
        self.raw_deployments = self.make_request(method=_method, endpoint=endpoint)
        return self.parse_deployments() if parse else self.raw_deployments

    def read_flow_runs(self, flow_name: str) -> dict:
        """
        Retrieves flow runs based on the provided flow name.

        Args:
            flow_name (str): The name of the flow for which to retrieve runs.

        Returns:
            dict: A dictionary containing the flow runs that match the provided flow name.
        """
        endpoint = "flow_runs/filter"
        request_body = {
            "flows": {
                "name": {
                    "like_": flow_name,
                },
            },
        }
        _method = "post"
        return self.make_request(method=_method, endpoint=endpoint, request_body=request_body)

    def read_flow_run(self, flow_id: str) -> dict:
        """
        Retrieves a specific flow run based on the provided flow id.

        Args:
            flow_id (str): The id of the flow run to retrieve.

        Returns:
            dict: A dictionary containing the details of the flow run.
        """
        endpoint = f"flow_runs/{flow_id}"
        _method = "get"
        return self.make_request(method=_method, endpoint=endpoint)

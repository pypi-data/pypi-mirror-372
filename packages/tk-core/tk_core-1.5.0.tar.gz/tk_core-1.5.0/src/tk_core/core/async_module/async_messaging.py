import logging
import os
import time
from urllib.parse import urlparse

import requests
import ujson as json
from boto3 import client as boto3_client
from pydantic import BaseModel
from requests.exceptions import HTTPError, Timeout
from retry import retry

from tk_core.aws.secrets import SecretManager
from tk_core.common.s3 import S3Util
from tk_core.core.async_module.models import GenericAsyncResponse
from tk_core.prefect.prefect_api import Prefect

logger = logging.getLogger(__name__)


RUNTIME_ENV = os.getenv("ENV", "dev")


class SNS:
    def __init__(self, topic_arn: str, run_time_env: str = "dev", region_name: str = "us-east-1"):
        self.sns = boto3_client("sns", region_name=region_name)
        self.topic_arn = self.get_topic_arns(topic_arn, run_time_env)
        print(f"SQS init with ARN: {self.topic_arn}")

    def publish(self, message: str, subject: str = "") -> dict:
        return self.sns.publish(
            TopicArn=self.topic_arn,
            Message=message,
            Subject=subject,
        )

    def subscribe(self, endpoint: str, protocol: str = "email") -> dict:
        return self.sns.subscribe(
            TopicArn=self.topic_arn,
            Protocol=protocol,
            Endpoint=endpoint,
        )

    @staticmethod
    def get_topic_arns(topic_name: str, run_time_env: str) -> dict:
        topic_arns: dict = SecretManager().get_secret("de-responses-sns-topic-arns", load_dict=True).get(topic_name)
        if topic_arns:
            return topic_arns.get(run_time_env)
        raise NameError(f"SNS Topic not found. {topic_name=} {run_time_env=}")


class SQS:
    def __init__(self, queue_name: str, run_time_env: str = "dev", region_name: str = "us-east-1"):
        self.sqs = boto3_client("sqs", region_name=region_name)
        self.queue_url = self.get_sqs_url(queue_name, run_time_env)
        print(f"SQS init with URL: {self.queue_url}")

    def send_message(self, message_body: str | dict, message_attributes: dict = None) -> dict:
        if not isinstance(message_body, str):
            message_body = str(message_body)
        message_attributes = message_attributes if message_attributes else {}
        return self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=message_body,
            MessageAttributes=message_attributes,
        )

    def listen_to_messages(
        self,
        request_id: str = None,
        max_number: int = 1,
        wait_time: int = 1,
        delete_on_receive: bool = False,
    ) -> str | list:
        """
        Receive a batch of messages in a single request from an SQS queue.

        Params:
        :param max_number: The maximum number of messages to receive. The actual number of messages received might be less.
        :param wait_time: The maximum time to wait (in seconds) before returning. When
            this number is greater than zero, long polling is used. This
            can result in reduced costs and fewer false empty responses.
        :param delete_on_receive: Whether to delete the message when received.

        Return:
        List of message objects received.
        """
        response = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            AttributeNames=["All"],
            MaxNumberOfMessages=max_number,
            WaitTimeSeconds=wait_time,
        )
        messages = response.get("Messages", [])
        if messages:
            if not request_id:  # if we don't wait for certain request_id - return all
                return messages
            for message in messages:  # else, start searching for speicfied request_id
                if delete_on_receive:
                    self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=message["ReceiptHandle"])
                body = json.loads(message["Body"])
                if "Message" in body:
                    sns_message = json.loads(body["Message"])
                    # Check if this is the message we're looking for
                    # print(f"{request_id=} | SNS Request_ID: {sns_message.get('metadata', {}).get('request_id')}")
                    if sns_message.get("metadata", {}).get("request_id") == request_id:
                        return sns_message
        logger.debug(f"No appropriate messages found in the queue: {self.queue_url}")

    @staticmethod
    def get_sqs_url(queue_name: str, run_time_env: str) -> str:
        sqs_url: dict = SecretManager().get_secret("de-responses-sqs-queue-urls", load_dict=True).get(queue_name)
        if sqs_url:
            return sqs_url.get(run_time_env)
        raise NameError(f"SQS URL not found. {sqs_url=} {run_time_env=}")


def get_sns_subject(job_name: str, job_status: str) -> str:
    """
    returns string title for SNS message
    """
    if job_status == "Success":
        return f"Job Completed Successfully for {job_name}"
    elif job_status == "Error":
        return f"Job Failed for {job_name}"


def report_to_sns(flow_output: dict, env: str = "dev") -> dict:
    """
    sends an SNS message after validating flow_output
    """
    sns = SNS("de-responses", run_time_env=env)
    logging.info(f"Flow output received: {flow_output}")
    flow_report = GenericAsyncResponse(**flow_output)
    logging.info(f"SNS message will be sent:\n{flow_report}")
    response = sns.publish(flow_report.model_dump_json(), get_sns_subject(flow_report.job_name, flow_report.job_status))
    return response


def report_to_sqs(flow_output: dict) -> dict:
    sqs = SQS("de-responses")
    logging.info(f"Flow output received: {flow_output}")
    flow_report = GenericAsyncResponse(**flow_output)
    logging.info(f"SQS message will be sent:\n{flow_report}")
    response = sqs.send_message(message_body=flow_report.model_dump())
    return response


def extract_input_objects(payload: dict | BaseModel) -> list | dict | None:
    if not isinstance(payload, dict) and isinstance(payload, BaseModel):
        payload = payload.model_dump()
    input_objects = payload.get("input_objects", {})

    if isinstance(input_objects, str) and input_objects.startswith("s3://"):
        s3_link = input_objects
        parsed_link = urlparse(s3_link)
        bucket_name = parsed_link.netloc
        s3_key = parsed_link.path.lstrip("/")
        try:
            extracted_objects = S3Util(bucket_name).read_json(s3_key)
            logger.info(f"input_objects extracted. type: {type(extracted_objects)} size: {len(extracted_objects)}")
        except Exception as e:
            logger.error(f"Error reading from s3: {e}")
            raise e
    else:
        extracted_objects = input_objects

    return extracted_objects


def form_response_on_success(generic_response: dict) -> dict:
    successful_result = {
        "job_name": generic_response.get("job_name"),
        "metadata": generic_response.get("metadata"),
        "job_info": generic_response.get("job_info"),
        "job_status": "Success",
        "traceback": None,
    }
    return successful_result


def form_response_on_error(generic_response: dict, e: Exception) -> dict:
    error_result = {
        "job_name": generic_response.get("job_name"),
        "metadata": generic_response.get("metadata"),
        "job_info": None,
        "job_status": "Error",
        "traceback": str(e),
    }
    return error_result


@retry(exceptions=(HTTPError, Timeout), tries=3, delay=2, backoff=2)
def call_fastapi(payload: dict, endpoint: str, dev: bool) -> dict:
    try:
        TERAKEET_API_ENDPOINT = os.environ.get("TERAKEET_API_ENDPOINT")
        url = f"{TERAKEET_API_ENDPOINT}/{endpoint}"
        url += "/dev" if dev else ""
        logger.info(f"CALLING API ENDPOINT: {url}")
        logger.info(f"PARAMS Keys: {payload.keys()}")
        response = requests.post(url, json=payload, timeout=60, headers={"API-Key": os.environ["FAST_API_KEY"]})
        response.raise_for_status()
        return response.json()
    except Timeout:
        logger.warning("Request timed out, retrying...")
        raise
    except HTTPError as http_err:
        if str(response.status_code)[0] == "4":  # 4xx codes
            logger.warning(f"Received {response.status_code} status code, retrying...")
            raise
        else:
            logger.error(f"An HTTP error occurred: {http_err}")
            raise


def trigger_and_await_flow(
    generic_request: dict,
    timeout: int = 600,
    dev: bool = False,
    poll_freq: int = 5,
    return_sns_report: bool = False,
) -> None | dict:
    """
    Triggers an Prefect flow asynchronously and waits for its completion.

    Args:
        generic_request (dict): The generic request to be passed to the flow.
        timeout (int, optional): The maximum time to wait for the flow to complete, in seconds. Defaults to 600.
        dev (bool, optional): Indicates whether to use the development environment. Defaults to False.
        poll_freq (int, optional): The frequency at which to poll for flow completion, in seconds. Defaults to 5.
        return_sns_report (bool, optional): Indicates whether to return the SNS report instead of the flow status only.
            Defaults to False.

    Returns:
        None or dict: If `return_sns_report` is False, returns the status of the flow only.
            If `return_sns_report` is True, returns the full SNS report.

    Raises:
        Exception: If an error occurs during the execution of the flow.

    """
    try:
        fastapi_response = call_fastapi(generic_request, endpoint="async/submit_job", dev=dev)
        # TODO handle failed FastAPI response
        if not fastapi_response:
            raise Exception("FastAPI response is empty")

        logger.info(f"FastAPI response:\n{fastapi_response}")
        flow_id = fastapi_response.get("metadata").get("flow_run_id")
        request_id = fastapi_response.get("metadata").get("request_id")

        if return_sns_report:
            return poll_sns(request_id, timeout, dev)
        else:
            return poll_prefect(flow_id, timeout, poll_freq)
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise e


def poll_sns(request_id: str, timeout: int, is_dev: bool) -> dict:
    """
    Poll SNS for detailed job execution result.

    Args:
        request_id (str): The ID of the request.
        timeout (int): The maximum time to wait for the SNS message, in seconds.

    Returns:
        dict: The SNS message containing the job execution result.

    Raises:
        Exception: If the SNS message is not found or if the job execution failed.
    """
    sqs = SQS("ds-async-responses", run_time_env="dev" if is_dev else "prod")
    start_time = time.time()
    sns_message = None

    while not sns_message:
        sns_message = sqs.listen_to_messages(
            request_id=request_id,
        )
        if time.time() - start_time > timeout:
            raise TimeoutError("Flow run timeout when polling SNS for status")

    logger.info(f"SNS message: {sns_message}")
    state = sns_message.get("job_status")
    logger.info(f"Job state: {state}")
    if state.lower() == "error":
        traceback = sns_message.get("traceback")
        raise Exception(f"Flow run failed: {traceback}")
    elif state.lower() == "success":
        logger.info("Flow run completed successfully")
        return sns_message


def poll_prefect(flow_id: str, timeout: int, poll_freq: int = 5) -> dict:
    """
    Poll Prefect API for flow run status only.

    Args:
        flow_id (str): The ID of the flow run.
        timeout (int): The maximum time to wait for the flow run to complete, in seconds.
        poll_freq (int): The frequency at which to poll for flow run status, in seconds. Default is 5.

    Returns:
        dict: The status of the flow run.

    Raises:
        Exception: If the flow run failed, was cancelled, crashed, or if the timeout was reached.
    """
    prefect = Prefect()
    flow_completed = False
    time_start = time.time()
    while not flow_completed:
        flow_run_instance = prefect.read_flow_run(flow_id)
        state = flow_run_instance.get("state_type")
        if state.lower() == "completed":
            flow_completed = True
        elif state.lower() in ("failed", "cancelled", "crashed"):
            traceback = flow_run_instance.get("state").get("message")
            raise Exception(f"Flow run failed: {traceback}")
        else:
            logger.info(f"Flow run state: {state}, checking again in {poll_freq} seconds...")
        if time.time() - time_start > timeout:
            raise TimeoutError("Flow run timeout when polling Prefect API for status")
        time.sleep(poll_freq)
    logger.info("Flow run completed successfully")
    return {"job_status": "Success"}


def suggest_timeout_for_job(job_name: str, input_objects_n: int, redundancy: float = 1.25) -> int:
    """
    Suggest a timeout duration based on the job name and number of input objects.

    Args:
        job_name (str): The name of the job.
        input_objects_n (int): The number of input objects.

    Returns:
        int: The suggested timeout duration in seconds.
    """
    job_timeouts = {  # x seconds per 1 item in input_objects; empiric data
        "tam": 1,  # TODO add real values
        "batch_serp": 1,  # TODO add real values
        "batch_page_scrape": 0.15,
        "batch_page_restructuring": 0.18,
    }
    absolute_min_timeout = 1 * 3600  # 1h
    if input_objects_n < 1:
        raise ValueError("Cannot suggest timeout for job with zero input_objects.")
    if job_name not in job_timeouts:
        raise ValueError(f"Job name {job_name} is unknown. Connect to DE if this is unexpected.")
    dynamic_evaluation = int(job_timeouts.get(job_name) * input_objects_n * redundancy)
    return max(dynamic_evaluation, absolute_min_timeout)


def run_sync_job(
    job_name: str,
    metadata: dict,
    job_params: dict,
    input_objects: list | str,
    is_dev: bool,
    timeout: int = None,
) -> dict:
    """
    Wrapper for triggering and awaiting DE job.

    Args:
        job_name (str): The name of the job to be triggered.
        metadata (dict): The metadata can contain any fields. Consumer (str) is a mandatory filed.
        job_params (dict): The parameters to be passed to the job. Refer to job-specific docs.
        input_objects (list | str): The input objects for the job. Either a list or an S3 link.
        is_dev (bool): Flag indicating whether the job is running in development mode.
        timeout (int, optional): The timeout duration for triggering and awaiting the job.
            If not provided, it will be suggested based on the job name and the number of input objects.

    Returns:
        dict: The result of the job - a dictionary representation of GenericAsyncResponse.
    """
    if isinstance(input_objects, str) and not timeout:
        raise ValueError("Timeout must be provided when input_objects is not an explicit list.")
    else:
        timeout = timeout or suggest_timeout_for_job(job_name, len(input_objects))
    generic_request = {
        "job_name": job_name,
        "metadata": metadata,
        "job_params": job_params,
        "input_objects": input_objects,
    }
    return trigger_and_await_flow(generic_request=generic_request, timeout=timeout, dev=is_dev, return_sns_report=True)

import logging

import boto3
from botocore.exceptions import ClientError

from tk_core.common.hasher import partitioned_hash
from tk_core.common.s3 import S3Util


class DeService:
    partitioned_hash = staticmethod(partitioned_hash)

    def __init__(self, sub_folder: str) -> None:
        self.s3 = S3Util()
        self.sub_folder = sub_folder

    def store_execution(self, response_dict: dict) -> None:
        """Stores execution response for caching, Airflow processing, and snowpipe ingestion"""
        if response_dict:
            self.store_execution_s3_cache(response_dict)
            self.store_response_for_snowpipe(response_dict)

    def store_execution_s3_cache(self, response_dict: dict) -> None:
        """Caches execution responses. S3 rules clear this out after two days"""
        cache_key = self.execution_cache_location(response_dict["execution_id"])
        if not self.execution_cache_exists(cache_key):
            logging.info(f"storing execution cache: {cache_key}")
            self.s3.write_json(cache_key, response_dict)

    def load_execution_cache(self, execution_id: str) -> dict:
        """Read from the S3 cache. Mark the response as cached."""
        cache_key = self.execution_cache_location(execution_id)
        data = self.s3.read_json(cache_key)
        data["cached"] = True
        return data

    def execution_cache_exists(self, execution_id: str, freshness_days: int = 1) -> bool:
        """
        Check if the cache exists for the given execution_id
        """
        # 0 day cache | return False
        if freshness_days == 0:
            return False
        # 1 day cache | return True if specific .json file exists
        elif freshness_days == 1:
            cache_key = self.execution_cache_location(execution_id)
        # 30 day cache | return True if directory exists
        elif freshness_days == 30:
            cache_key = self.execution_cache_directory(execution_id)

        try:
            client = boto3.client("s3")
            client.head_object(Bucket=self.s3.bucket_name, Key=cache_key)
            return True
        except ClientError:
            return False

    def execution_cache_location(self, execution_id: str) -> str:
        return f"caches/{self.sub_folder}/executions/{execution_id}.json"

    def execution_cache_directory(self, execution_id: str) -> str:
        return f"caches/{self.sub_folder}/executions/{execution_id.split('/')[0]}"

    def store_response_for_snowpipe(self, response_dict: dict) -> None:
        """Write to S3 for automated snowpipe ingestion (execution info only)"""
        sf_key = f"snowpipe/json_ingest/{response_dict['execution_id']}.json"
        response_dict["errors"] = response_dict.get("errors", [])
        self.s3.write_json(sf_key, response_dict)

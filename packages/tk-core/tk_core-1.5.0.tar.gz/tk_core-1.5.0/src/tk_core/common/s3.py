"""A class providing common s3 functions"""

import gzip
import os

import boto3
import ujson as json
from botocore.config import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv  # dev purpose, won't affect prod secrets

load_dotenv()  # dev purpose, won't affect prod secrets


class S3Util:
    """Provides common s3 functions"""

    default_config = Config(
        retries={"max_attempts": 2, "mode": "standard"},
        max_pool_connections=10,
    )

    def __init__(self, bucket: str = None, config: dict | None = None, enable_prints: bool = False) -> None:
        """
        Initialize the S3Util class

        :param bucket: The bucket to use, if not provided, will use the S3_BUCKET environment variable
        :param enable_prints: If True, will print all S3 operations
        """
        if config is None:
            config = self.default_config
        self.s3 = boto3.resource("s3", config=config)
        self.bucket_name = bucket or self.get_bucket()
        self.enable_prints = enable_prints

    def get_bucket(self) -> str:
        """
        Get the bucket name from the environment or raise exception
        """
        if os.environ.get("S3_BUCKET") is None:
            raise ValueError("S3_BUCKET environment variable not set")
        return os.environ.get("S3_BUCKET")

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the bucket

        :param key: The key to check (no leading slash)
        :return: True if the key exists, False otherwise"""
        try:
            client = boto3.client("s3")
            client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False

    def read_json(self, key: str) -> dict:
        return json.loads(self.read_file(key))

    def write_json(self, key: str, data: dict) -> None:
        """
        Writes a dictionary to S3, converting to JSON first

        :param key: The key to write to (do not include a leading slash)
        :param data: The data to write as dictionary
        """
        self.write_file(key, json.dumps(data))

    def read_file(self, key: str) -> str:
        if self.enable_prints:
            print(f"Reading from {self.bucket_name}/{key}")
        obj = self.s3.Object(self.bucket_name, key)
        # for some reason the S3 reading of .gz files stopped working
        # so we need to manually decompress them here
        if key.endswith(".gz"):
            with gzip.GzipFile(fileobj=obj.get()["Body"]) as gzipfile:
                content = gzipfile.read()
        else:
            content = obj.get()["Body"].read()
        return content.decode("utf-8")

    def write_file(self, key: str, data: dict) -> None:
        """
        Writes a file to S3
        :param key: The key to write to (do not include a leading slash)
        :param data: The data to write as dictionary
        """
        if self.enable_prints:
            print(f"Writing to {self.bucket_name}/{key}")
        self.s3.Object(self.bucket_name, key).put(Body=data)

    def delete_file(self, key: str) -> None:
        """Deletes a file from S3"""
        if self.enable_prints:
            print(f"Deleting {self.bucket_name}/{key}")
        self.s3.Object(self.bucket_name, key).delete()

    def list_contents(self, prefix: str = None) -> list:
        """Return list of keys within the bucket/prefix set, 1000 keys max per call"""
        items = []
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)

        try:
            for obj in response["Contents"]:
                if obj["Key"][-1] == "/":
                    continue

                items.append(obj["Key"])
        except KeyError:
            return None

        return items

    def copy_file(self, source_key: str, destination_key: str) -> None:
        """Copies a file from one location to another"""
        if self.enable_prints:
            print(f"Copying {self.bucket_name}/{source_key} to {self.bucket_name}/{destination_key}")
        copy_source = {"Bucket": self.bucket_name, "Key": source_key}
        self.s3.meta.client.copy(copy_source, self.bucket_name, destination_key)

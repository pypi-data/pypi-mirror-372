import os

import redis
import ujson as json
from dotenv import load_dotenv
from redis.backoff import ExponentialBackoff
from redis.client import Pipeline
from redis.retry import Retry
from tk_core.common.dates import datecode
from tk_core.core.memory import print_memory_usage
from tk_core.timing.time import timer

load_dotenv(override=True)


class TKRedis:
    """
    A class to handle the Redis client
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        decode_responses: bool = True,
    ) -> None:
        self.host = host or os.environ.get("REDIS_HOST")
        self.port = port or os.environ.get("REDIS_PORT")
        self.decode_responses = decode_responses
        self.r = self.connect()

    def set_host(self, host: str) -> None:
        """
        Sets (overrides) the host of the Redis config
        """
        self.host = host

    def set_port(self, port: int) -> None:
        """
        Sets (overrides) the port of the Redis config
        """
        self.port = port

    def set_decode_responses(self, decode_responses: bool) -> None:
        """
        Sets (overrides) the decode_responses of the Redis config
        """
        self.decode_responses = decode_responses

    def connect(self, timeout: int = 5) -> redis.Redis:
        """
        Creates a new instance of the Redis class
        """
        print(f"Connecting to Redis at {self.host}:{self.port}")

        retry = Retry(ExponentialBackoff(), 3)

        if self.host is None or self.port is None:
            raise ValueError("Host and port must be set to connect to Redis")
        if self.host == "localhost":
            return redis.Redis(
                host=self.host,
                port=self.port,
                decode_responses=self.decode_responses,
                socket_timeout=timeout,
            )
        return redis.Redis(
            host=self.host,
            port=self.port,
            decode_responses=self.decode_responses,
            ssl=True,
            ssl_cert_reqs="none",
            socket_timeout=timeout,
            retry=retry,
            retry_on_timeout=True,
        )

    def ping(self) -> bool:
        """
        Pings the Redis service to see if it is connected
        """
        return self.r.ping()

    def pipe_set_values_from_dict(self, data: dict) -> None:
        """
        Sets values into the Redis using a pipeline
        """
        pipe = self.get_pipeline()
        for key, value in data.items():
            pipe.set(key, value)
        pipe.execute()

    # @timer()
    def set_hash_from_dict(self, hash_name: str, data: dict, pipeline: bool = False) -> bool:
        """
        Sets a hash in Redis
        Returns:
            bool: True if successful
        """
        return self.r.hset(hash_name, mapping=data)

    def set_hash_from_nested_dict(self, hash_name: str, main_key: str, data: dict, pipeline: bool = False) -> bool:
        """
        Sets a hash in Redis
        Returns
        """
        data = {main_key: json.dumps(data)}
        return self.r.hset(hash_name, mapping=data)

    def get_hash_value(self, hash_name: str, key: str) -> str:
        """
        Gets a value from a hash in redis
        """
        return self.r.hget(hash_name, key)

    def get_hash_from_name(self, hash_name: str) -> dict:
        """
        Gets a hash from redis
        """
        return self.r.hgetall(hash_name)

    def get_pipeline(self) -> Pipeline:
        """
        Returns a pipeline for Redis
        """
        return self.r.pipeline()

    @timer()
    def set_request_hash_into_redis(self, hash_name: str, list_of_hashes: list) -> None:
        """
        Sets a list of hashes into the Redis using a pipeline
        """
        print_memory_usage("Setting Request Hash into Redis")
        # get the current date
        # convert it to an int
        formatted_date = int(datecode())
        # create a pipeline
        pipe = self.r.pipeline()
        # set values into redis from list of hashes
        for hash_ in list_of_hashes:
            pipe.hset(hash_name, hash_, formatted_date)
        pipe.execute()

    def get_hash_values_from_list_with_pipe(self, hash_name: str, data: list) -> list:
        """
        Gets a list of hash values from Redis using a pipeline.

        Args:
            hash_name (str): The name of the hash in Redis.
            data (list): A list of keys to retrieve hash values for.

        Returns:
            list: A list of hash values corresponding to the given keys.
        """
        print_memory_usage("Getting Hash Values from List with Pipe")
        print(f"{hash_name=}")
        print(f"Total checks needed {len(data)}.")
        grouped_data = [data[i : i + 250_000] for i in range(0, len(data), 250_000)]
        print(f"Split into {len(grouped_data)} groups.")
        output_data = []
        for g_idx, group in enumerate(grouped_data):
            print(f"Group {g_idx} | Size {len(group)} | Checking Cache")
            output_data.extend(self.__get_hash_values_from_list_with_pipe(hash_name, group))
        print_memory_usage("Finished Getting Hash Values from List with Pipe")
        return output_data

    def __get_hash_values_from_list_with_pipe(self, hash_name: str, data: list) -> list:
        """
        function that actually creates the pipeline and gets all the values

        Returns:
            list: A list of hash values corresponding to the given keys.
        """
        pipe = self.get_pipeline()
        for key in data:
            pipe.hget(hash_name, key)
        return pipe.execute()

    @timer()
    def get_all_found_hashes(self, hash_name: str, min_date: int) -> list:
        """
        Gets all the hashes from the Redis that are greater than the min_date
        """
        all_hashes = self.r.hgetall(hash_name)
        found_hashes = []
        for hash_, date in all_hashes.items():
            if int(date) > min_date:
                found_hashes.append(hash_)
        return found_hashes


# TODO: AWS?
# https://redis.readthedocs.io/en/stable/examples/connection_examples.html#Connecting-to-a-redis-instance-with-ElastiCache-IAM-credential-provider.

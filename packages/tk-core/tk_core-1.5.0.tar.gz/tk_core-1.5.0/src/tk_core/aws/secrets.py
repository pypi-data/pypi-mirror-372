import boto3
import ujson as json
from botocore.exceptions import ClientError


class SecretManager:
    def __init__(self) -> None:
        self._client = None

    def get_secret(self, secret_name: str, load_dict: bool = False) -> str | dict:
        """
        Get the secret value from AWS Secrets Manager

        Args
            secret_name: name of the secret to retrieve
            load_dict: flag to determine if the secret string should be loaded as a dictionary.
                False by default
        Return
            the secret value as a string or the key/value pair as a dictionary depending on flag
        """
        try:
            get_secret_value_response = self.client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            # For a list of exceptions thrown, see
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            raise e

        # return the json decoded value from the secret string if flagged
        if load_dict:
            return json.loads(get_secret_value_response["SecretString"])
        # else return just the string value
        return get_secret_value_response["SecretString"]

    @property
    def client(self) -> boto3.client:
        """
        Get the boto3 client for SecretsManager
        keeping the client the same throughout the session
        """
        if not self._client:
            self._client = boto3.client("secretsmanager")
        return self._client

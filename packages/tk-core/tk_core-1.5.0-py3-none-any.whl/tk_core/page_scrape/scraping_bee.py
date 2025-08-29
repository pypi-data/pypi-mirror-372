"""
based on: https://github.com/terakeet/de-combined-capture-extract/tree/main
"""

from urllib.parse import urlparse

import boto3
import ujson as json
from botocore.exceptions import ClientError
from scrapingbee import ScrapingBeeClient

BLACKLIST = {"plus.google.com", "linkedin.com"}
PREMIUM = {"facebook.com", "instagram.com", "twitter.com", "tiktok.com"}


def get_api_key() -> str:
    """
    returns the scraping bee api key from AWS Secrets Manager
    """
    aws_secret_name = "scraping_bee_api_key"  # noqa - name of secret not actual secret
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=aws_secret_name)
        str_value = get_secret_value_response["SecretString"]
        return json.loads(str_value)["SCRAPING_BEE_API_KEY"]
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e


class Capture:
    def __init__(self, url: str, parameters: dict, api_key: str = None) -> None:
        self.url = url
        self.params = parameters
        self.hostname = urlparse(self.url).hostname
        self.use_premium_proxy = self.hostname in PREMIUM
        self.params["premium_proxy"] = self.use_premium_proxy
        if api_key is None:
            self.api_key = get_api_key()
        else:
            self.api_key = api_key

    def run(self) -> str:
        if self.hostname in BLACKLIST:
            raise Exception(f"Domain {self.hostname} is blacklisted")
        else:
            return self.retrieve_html()

    def retrieve_html(self) -> str:
        client = ScrapingBeeClient(api_key=self.api_key)
        page = client.get(self.url, params=self.params)
        if page.status_code == 200:
            return page.content.decode("utf-8", errors="replace")
        else:
            print(f"SB HTML ERROR MESSAGE: {page.content}")
            raise Exception(f"Capture for {self.url} failed with {page.status_code}")

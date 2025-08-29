import logging
from datetime import datetime
from typing import Any, Union

from bs4 import Tag

from tk_core.page_restructuring.utils.html_extraction import (
    get_extruct_info,
    get_html_info,
    get_newspaper_info,
    get_trafilatura_info,
)

logger = logging.getLogger(__name__)


def restructure_page(url: str, content: str) -> dict:
    """
    Meta fucntion. Restructures the page content by running extraction methods on the given URL and content.

    Args:
        url (str): The URL of the page.
        content (str): HTML content of the page.

    Returns:
        dict: The restructured page content.
    """
    bs_response, extruct_response, newspaper_response, trafilatura_response = run_extraction(url, content)

    response = reformat_structure(
        html_info=bs_response,
        extruct_info=extruct_response,
        newspaper_info=newspaper_response,
        trafilatura_info=trafilatura_response,
    )
    return response


def run_extraction(url: str, content: str) -> tuple[dict, dict, dict, str]:
    """
    Runs the extraction process on the given URL and content.

    Args:
        url (str): The URL of the webpage to extract information from.
        content (str): The HTML content of the webpage.

    Returns:
        tuple[dict, dict, dict]: A tuple containing the extracted information from the webpage.
            The first element is the response from Beautiful Soup,
            the second element is the response from Extruct,
            and the third element is the response from Newspaper.
    """
    if not isinstance(url, str):
        raise TypeError("URL must be a string")
    elif not isinstance(content, str):
        raise TypeError("Content must be a string")

    logger.debug("Get beautiful soup response")
    try:
        beautiful_soup_response = get_html_info(url, content)
    except Exception as e:
        logger.warning(f"Beautiful Soup processing failed: {e}")
        beautiful_soup_response = {}

    logger.debug("Get extruct response")
    try:
        extruct_response = get_extruct_info(url, content)
    except Exception as e:
        logger.warning(f"Extruct processing failed: {e}")
        extruct_response = {}

    logger.debug("Get newspaper response")
    try:
        newspaper_response = get_newspaper_info(content)
    except Exception as e:
        logger.warning(f"Newspaper processing failed: {e}")
        newspaper_response = {}

    logger.debug("Get Trafilatura response")
    try:
        trafilatura_response = get_trafilatura_info(content)
    except Exception as e:
        logger.warning(f"Trafilatura processing failed: {e}")
        trafilatura_response = ""

    return beautiful_soup_response, extruct_response, newspaper_response, trafilatura_response


def reformat_structure(html_info: dict, extruct_info: dict, newspaper_info: dict, trafilatura_info: str) -> dict:
    """
    Reformat the structure of extracted information from HTML, extruct, and newspaper sources.

    Args:
        html_info (dict): A dictionary containing information extracted from HTML.
        extruct_info (dict): A dictionary containing information extracted using extruct library.
        newspaper_info (dict): A dictionary containing information extracted using newspaper library.

    Returns:
        dict: A dictionary containing the reformatted structure of extracted information.
    """
    response = {
        "version": 1,
        "title_tag": html_info.get("title_tag", ""),
        "title_text": html_info.get("title_text", ""),
        "article_title": newspaper_info.get("title", ""),
        "meta_keywords": html_info.get("meta_keywords", ""),
        "meta_description": html_info.get("meta_description", ""),
        "all_meta_tags": html_info.get("all_meta_tags", ""),
        "all_meta_structured": html_info.get("struct_meta_tags", ""),
        "h1s": html_info.get("h1s", ""),
        "h2s": html_info.get("h2s", ""),
        "h3s": html_info.get("h3s", ""),
        "h4s": html_info.get("h4s", ""),
        "h5s": html_info.get("h5s", ""),
        "h6s": html_info.get("h6s", ""),
        "h1s_raw_html": html_info.get("h1s_raw", ""),
        "h2s_raw_html": html_info.get("h2s_raw", ""),
        "h3s_raw_html": html_info.get("h3s_raw", ""),
        "h4s_raw_html": html_info.get("h4s_raw", ""),
        "h5s_raw_html": html_info.get("h5s_raw", ""),
        "h6s_raw_html": html_info.get("h6s_raw", ""),
        "authors": newspaper_info.get("authors", ""),
        "publish_date": newspaper_info.get("publish_date", ""),
        "meta_published_time": html_info.get("meta_published_time", ""),
        "meta_modified_time": html_info.get("modified_time", ""),
        "meta_updated_time": html_info.get("updated_time", ""),
        "extraction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "canonical": html_info.get("canonical", ""),
        "hreflang": html_info.get("hreflang") or "n/a",
        "robots_tags": html_info.get("robots_tags", ""),
        "alt_text": html_info.get("alt_text", ""),
        "internal_links": html_info.get("internal_links", ""),
        "internal_links_raw_html": html_info.get("raw_internal_links", ""),
        "internal_links_structured_list": html_info.get("internal_links_structured_list", ""),
        "external_links": html_info.get("external_links", ""),
        "external_links_raw_html": html_info.get("raw_external_links", ""),
        "external_links_structured_list": html_info.get("external_links_structured_list", ""),
        "top_image": newspaper_info.get("top_image", ""),
        "images_raw_html": html_info.get("images_raw_html", ""),
        "images_structured_list": html_info.get("images_structured_list", ""),
        "opengraph_title": extruct_info.get("og_title", ""),
        "opengraph_description": extruct_info.get("og_description", ""),
        "opengraph_image": extruct_info.get("og_image", ""),
        "schema_title": extruct_info.get("schema_title", ""),
        "schema_description": extruct_info.get("schema_description", ""),
        "schema_author": extruct_info.get("schema_author", ""),
        "schema_date_published": extruct_info.get("schema_date_published", ""),
        "schema_date_modified": extruct_info.get("date_modified", ""),
        "schema_images": extruct_info.get("list_of_images", ""),
        "trafilatura_content": trafilatura_info,
    }

    response = {key: convert_tag_to_string(value) for key, value in response.items()}
    return response


def convert_tag_to_string(value: Union[Tag, Any]) -> str:
    """
    Converts a BeautifulSoup Tag object to a string representation.

    Args:
        value (Union[Tag, Any]): The value to be converted. Can be a BeautifulSoup Tag object or any other value.

    Returns:
        str: The string representation of the value. If the value is a Tag object,
            it is converted to a string using the str() function.
            If the value is not a Tag object, it is returned as is.
    """
    if isinstance(value, Tag):
        return str(value)
    return value

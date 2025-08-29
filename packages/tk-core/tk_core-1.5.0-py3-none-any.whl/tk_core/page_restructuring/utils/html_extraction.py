import logging
from typing import Dict, List, Tuple, Union

import extruct
import lxml
import trafilatura
from bs4 import BeautifulSoup, Tag
from newspaper import Article
from w3lib.html import get_base_url

from tk_core.page_restructuring.utils import link_extraction

logger = logging.getLogger(__name__)


def get_title_attributes(title_tag_obj: str) -> Tuple[str, str]:
    """
    Extracts the title tag and text from the given title tag object.
    """
    title_tag = str(title_tag_obj)
    title_text = str(title_tag_obj.string) if title_tag_obj else ""

    return title_tag, title_text


def get_meta_attributes(soup: BeautifulSoup) -> Tuple[str, str]:
    """
    Extracts the meta keywords and meta description attributes from the given BeautifulSoup object.
    """

    meta_keywords = soup.find("meta", attrs={"name": "keywords"})
    meta_keywords = meta_keywords.get("content", "") if meta_keywords else ""

    meta_description = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_keywords.get("content", "") if meta_description and isinstance(meta_description, dict) else ""

    return meta_keywords, meta_description


def get_meta_tags(soup: BeautifulSoup) -> Tuple[list[str], list[str], list[dict]]:
    """
    Extracts meta tags from a BeautifulSoup object.

    Returns:
        Tuple[list[str], list[str], list[dict]]: A tuple containing three lists:
            - all_meta: A list of strings representing the meta tags in the format "[property or name] content".
            - all_meta_tags: A list of strings representing the raw HTML of each meta tag.
            - struct_meta_tags: A list of dictionaries representing the attributes of each meta tag.
    """
    all_meta_tags = []
    struct_meta_tags = []
    # REVIEW: list comprehension
    for meta_tag in soup.find_all("meta"):
        all_meta_tags.append(str(meta_tag))
        dict_meta_tag = {}
        # REVIEW: dict comprehension
        for attr in meta_tag.attrs:
            dict_meta_tag[attr] = meta_tag[attr]
        struct_meta_tags.append(dict_meta_tag)

    return all_meta_tags, struct_meta_tags


def get_header_tags(soup: BeautifulSoup) -> Tuple[list[str], list[str]]:
    """
    Extracts header tags from the given BeautifulSoup object.

    Returns:
        Tuple[list[str], list[str]]: A tuple containing two lists:
            - The first list contains the text content of the header tags.
            - The second list contains the raw HTML representation of the header tags.
    """
    h_tags = []
    raw_tags = []
    links = []
    for i in range(1, 7):
        headers = soup.find_all(f"h{i}")
        h_tags.append([h.text for h in headers])
        raw_tags.append([str(h) for h in headers])
        list_of_links = list(filter(None, [h.a.attrs.get("href") if h.a else {} for h in headers]))
        if list_of_links != []:
            flat_list = [item for sublist in list_of_links for item in sublist]
            # REVIEW: flat_map
            filtered_links = list(filter(None, flat_list))
            links.append(filtered_links)

    return h_tags, raw_tags


def get_timestamps(soup: BeautifulSoup) -> Tuple[str, str, str]:
    """
    Extracts timestamps from the given BeautifulSoup object.
    """
    meta_published_time = soup.find("meta", attrs={"property": "article:published_time"})
    meta_published_time = meta_published_time["content"] if meta_published_time else ""

    modified_time = soup.find("meta", attrs={"property": "article:modified_time"})
    modified_time = modified_time["content"] if modified_time else ""

    updated_time = soup.find("meta", attrs={"property": "article:updated_time"})
    updated_time = updated_time["content"] if updated_time else ""

    return meta_published_time, modified_time, updated_time


def get_canonical(soup: BeautifulSoup) -> str:
    """
    Extracts the canonical URL from the given BeautifulSoup object.
    """
    canonical = soup.find("link", attrs={"rel": "canonical"})
    canonical = canonical.get("href", "") if canonical else ""

    return canonical


def get_lang_from_tags(tags: Tag) -> dict:
    """
    Extracts language information from HTML tags.

    Args:
        tags (bs4.element.Tag): A list of HTML tags.

    Returns:
        dict: A dictionary containing language codes as keys and corresponding URLs as values.
    """
    lang_dict = {tag.get("hreflang"): [] for tag in tags if "hreflang" in tag.attrs}
    for tag in tags:
        lang = tag.get("hreflang")
        if lang in lang_dict:
            lang_dict[lang].append(tag.get("href"))

    return lang_dict


def merge_lang_dicts(lang_dict1: dict, lang_dict2: dict) -> dict:
    """
    Merge two language dictionaries into a single dictionary.
    """
    lang_dict = {}
    for key, value in lang_dict1.items():
        lang_dict[key] = value + lang_dict2.get(key, [])
    for key, value in lang_dict2.items():
        if key not in lang_dict:
            lang_dict[key] = value

    return lang_dict


def get_hreflang(soup: BeautifulSoup) -> dict:
    """
    Extracts hreflang values from the given BeautifulSoup object.

    Returns:
        dict: A dictionary containing the hreflang values extracted from the HTML.
    """
    a_tags = soup.find_all("a", attrs={"hreflang": True})
    a_tag_lang = get_lang_from_tags(a_tags)
    link_tags = soup.find_all("link", attrs={"hreflang": True})
    link_tag_lang = get_lang_from_tags(link_tags)

    lang_dict = merge_lang_dicts(a_tag_lang, link_tag_lang)

    return lang_dict


def get_robot_tags(soup: BeautifulSoup) -> list[str]:
    """
    Extracts robot tags from the given BeautifulSoup object.
    """
    robots_tags = []
    for tag in ["robots", "googlebot", "X-Robots-Tag"]:
        rt = soup.find("meta", attrs={"name": tag})
        if rt:
            robots_tags.append(str(rt))

    return robots_tags


def get_alt_text(soup: BeautifulSoup) -> list[str]:
    """
    Extracts the alt text from all img tags in the given BeautifulSoup object.
    """
    alt_text = []
    img_tags = soup.find_all("img")
    for tag in img_tags:
        at = tag.get("alt")
        if at:
            alt_text.append(at)

    return alt_text


def get_html_images(soup: BeautifulSoup) -> Tuple[list[str], list[dict]]:
    """
    Extracts images from the HTML using BeautifulSoup.
    """
    images_raw = []
    images_structured = []
    img_tags = soup.find_all("img")
    for tag in img_tags:
        images_raw.append(str(tag))
        dict_img_tag = {}
        for attr in tag.attrs:
            dict_img_tag[attr] = tag[attr]
        images_structured.append(dict_img_tag)

    return images_raw, images_structured


def get_html_info(url: str, html_content: str) -> dict:
    """
    Extracts various information from HTML content using BeautifulSoup.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    # xmlsoup = BeautifulSoup(html_content, "lxml")
    # hlib = BeautifulSoup(html_content, "html5lib")

    title_tag, title_text = get_title_attributes(soup.title)
    meta_keywords, meta_description = get_meta_attributes(soup)
    all_meta_tags, struct_meta_tags = get_meta_tags(soup)

    h_tags, raw_tags = get_header_tags(soup)

    h1s = h_tags[0]
    h1s_raw = raw_tags[0]
    h2s = h_tags[1]
    h2s_raw = raw_tags[1]
    h3s = h_tags[2]
    h3s_raw = raw_tags[2]
    h4s = h_tags[3]
    h4s_raw = raw_tags[3]
    h5s = h_tags[4]
    h5s_raw = raw_tags[4]
    h6s = h_tags[5]
    h6s_raw = raw_tags[5]

    body_content = soup.get_text()

    meta_published_time, modified_time, updated_time = get_timestamps(soup)

    canonical = get_canonical(soup)
    hreflang = get_hreflang(soup)

    robots_tags = get_robot_tags(soup)
    alt_text = get_alt_text(soup)

    le = link_extraction.LinkExtraction(url, soup)
    int_links, raw_int_links, struct_int_links, ext_links, raw_ext_links, struct_ext_links = le.get_all_links()
    images_raw, images_structured = get_html_images(soup)

    return {
        "title_tag": title_tag,
        "title_text": title_text,
        "meta_keywords": meta_keywords,
        "meta_description": meta_description,
        "all_meta_tags": all_meta_tags,
        "struct_meta_tags": struct_meta_tags,
        "h1s": h1s,
        "h2s": h2s,
        "h3s": h3s,
        "h4s": h4s,
        "h5s": h5s,
        "h6s": h6s,
        "h1s_raw": h1s_raw,
        "h2s_raw": h2s_raw,
        "h3s_raw": h3s_raw,
        "h4s_raw": h4s_raw,
        "h5s_raw": h5s_raw,
        "h6s_raw": h6s_raw,
        "body_content": body_content,
        "meta_published_time": meta_published_time,
        "modified_time": modified_time,
        "updated_time": updated_time,
        "canonical": canonical,
        "hreflang": hreflang,
        "robots_tags": robots_tags,
        "alt_text": alt_text,
        "internal_links": int_links,
        "raw_internal_links": raw_int_links,
        "internal_links_structured_list": struct_int_links,
        "external_links": ext_links,
        "raw_external_links": raw_ext_links,
        "external_links_structured_list": struct_ext_links,
        "images_raw_html": images_raw,
        "images_structured_list": images_structured,
    }


def get_opengraph_properties(data: Dict) -> Tuple[List[Dict], str, str, str]:
    """
    Extracts OpenGraph properties from the given data dictionary.
    Returns:
        A tuple containing:
        - list_of_properties (list[dict]): The list of OpenGraph properties.
        - title (str): The value of the "og:title" property.
        - description (str): The value of the "og:description" property.
        - top_image (str): The value of the "og:image" property.
    """

    if "opengraph" in data and len(data["opengraph"]) > 0:
        list_of_properties = data["opengraph"][0]["properties"]

        properties = {}
        for property in list_of_properties:
            attribute, value = property
            properties[attribute] = value

        title = properties.get("og:title", "")
        description = properties.get("og:description", "")
        top_image = properties.get("og:image", "")
    else:
        list_of_properties = []
        title = ""
        description = ""
        top_image = ""

    return list_of_properties, title, description, top_image


def get_author(author_data: Union[dict, list]) -> str:
    """
    Retrieves the name of the author from the given author data. (schema.org format)
    """
    if isinstance(author_data, dict):
        return author_data.get("name", "")
    if isinstance(author_data, list) and author_data:
        return author_data[0].get("name", "")
    return ""


def get_images(image_data: Union[dict, list]) -> list[str]:
    """
    Extracts the URLs of images from the given image data.
    """
    list_of_images = []
    if not image_data:
        return

    for image in image_data:
        if isinstance(image, dict) and "url" in image:
            list_of_images.append(image["url"])
        else:
            list_of_images.append(image)

    return list_of_images


def get_schema_properties(data: dict) -> Tuple[str, str, str, str, str, str, List[str]]:
    """
    Extracts schema properties from the given data dictionary.

    Returns:
        Tuple[str, str, str, str, str, str, List[str]]: A tuple containing the extracted schema properties.
            - schema_title (str): The title of the schema.
            - schema_date_published (str): The date when the schema was published.
            - schema_description (str): The description of the schema.
            - schema_author (str): The author of the schema.
            - date_modified (str): The date when the schema was last modified.
            - raw_schema_data (str): The raw JSON-LD data of the schema.
            - list_of_images (List[str]): A list of image URLs associated with the schema.
    """

    if "json-ld" not in data or not data["json-ld"]:
        return (None, "", "", "", "", str(data.get("json-ld", "")), [])

    schema_title = None
    schema_date_published = ""
    schema_description = ""
    schema_author = ""
    date_modified = ""
    raw_schema_data = str(data["json-ld"])
    list_of_images = []

    for d in data["json-ld"]:
        row = {k.lower(): v for k, v in d.items()}

        schema_date_published = row.get("datepublished", schema_date_published)
        schema_description = row.get("description", schema_description)
        schema_author = get_author(row.get("author", schema_author))
        date_modified = row.get("datemodified", date_modified) or date_modified
        list_of_images = get_images(row.get("image", list_of_images))
        schema_title = row.get("name", schema_title)

    return (
        schema_title,
        schema_date_published,
        schema_description,
        schema_author,
        date_modified,
        raw_schema_data,
        list_of_images,
    )


def extruct_data(data: dict) -> dict:
    """
    Extracts data from opengraph and "json-ld".

    Args:
        data (dict): The input data dictionary containing the extracted data.

    Returns:
        dict: A dictionary containing the extracted properties including OpenGraph
        properties and schema.org properties.
    """
    list_of_properties, title, description, top_image = get_opengraph_properties(data)
    (
        schema_title,
        schema_date_published,
        schema_description,
        schema_author,
        date_modified,
        raw_schema_data,
        list_of_images,
    ) = get_schema_properties(data)

    return {
        "og_title": title,
        "og_description": description,
        "og_image": top_image,
        "list_of_opengraph_properties": list_of_properties,
        "raw_opengraph_data": str(data.get("opengraph")),
        "schema_title": schema_title,
        "schema_date_published": schema_date_published,
        "schema_description": schema_description,
        "schema_author": schema_author,
        "date_modified": date_modified,
        "list_of_images": list_of_images,
        "raw_schema_data": raw_schema_data,
    }


def get_extruct_info(url: str, html_content: str) -> dict:
    """
    Extracts information using extruct library.
    This tool can pull microdata out of the schema.org
    """
    base_url = get_base_url(html_content, url)
    try:
        data = extruct.extract(html_content, base_url=base_url)
    except ValueError:
        data = extruct.extract(html_content.encode(), base_url=base_url)
    return extruct_data(data)


def get_newspaper_info(html_content: str) -> dict:
    """
    Retrieves information (title, authors, publish date, body content, top image) from an article given its HTML content.

    Args:
        html_content (str): The HTML content of the article.

    Returns:
        dict: A dictionary containing the retrieved information:

        {
            'title' (str): The title of the article,
            'authors' (list): A list of authors of the article,
            'publish_date' (str): The publish date of the article,
            'body_content' (str): The main content of the article,
            'top_image' (str): The URL of the top image associated with the article
        }
    """
    article = Article(url="", fetch_images=False)
    article.set_html(html_content)
    article.parse()

    return {
        "title": article.title,
        "authors": article.authors,
        "publish_date": str(article.publish_date),
        "body_content": article.text,
        "top_image": article.top_image,
    }


def get_trafilatura_info(html_content: str) -> str:
    mytree = lxml.html.fromstring(html_content.encode())
    return trafilatura.extract(mytree)

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup


class LinkExtraction:
    def __init__(self, url: str, soup: BeautifulSoup) -> None:
        self.url = url
        self.soup = soup
        self.all_links = self.default_links()
        self.domain = urlparse(self.append_scheme(self.url)).netloc.lower()

    def default_links(self) -> dict:
        return {
            "internal_links": [],
            "raw_internal_links": [],
            "internal_links_structured_list": [],
            "external_links": [],
            "raw_external_links": [],
            "external_links_structured_list": [],
        }

    def append_scheme(self, url: str) -> str:
        """Appends temp https:// (scheme) to URL to correctly extract domain."""
        is_internal_link = url.startswith("/") and not url.startswith("//")
        if not url.startswith("http") and not is_internal_link:
            return "https://" + url
        else:
            return url

    def extract_links(self) -> None:
        """
        Extracts links from the HTML content using BeautifulSoup.

        This method finds all <a> tags in the HTML content and extracts the href attribute
        value as the link. It then categorizes the links into internal and external links
        based on whether the link contains the domain of the current page. The extracted
        links are stored in different lists based on their types.
        """
        for link_tag in self.soup.find_all("a"):
            full_link = link_tag.get("href")
            if not full_link or full_link.startswith("javascript:") or full_link.startswith("#"):
                continue

            # Exclude full links that are still just fragments
            if full_link == f"{self.url}#":
                continue

            # Get the domain from the link and remove any www prefix
            url_domain = urlparse(self.append_scheme(full_link)).netloc.lower()
            domain_without_www = self.domain.replace("www.", "")

            # Create different possible variations of the domain URL
            http_url = f"http://{domain_without_www}"
            https_url = f"https://{domain_without_www}"
            http_www_url = f"http://www.{domain_without_www}"
            https_www_url = f"https://www.{domain_without_www}"

            # Check if link contains url domain
            link_contains_self_domain = (self.domain and self.domain in url_domain)
            
            # Pattern to match external links
            external_link_pattern = re.compile(r"^[a-zA-Z]{3,5}:?//")
            link_matches_external_pattern = (external_link_pattern.match(full_link) or full_link.startswith("//"))
            
            # Check if link contains url domain in various formats
            link_has_url = (
                domain_without_www in full_link
                and (full_link.startswith(http_url)
                    or full_link.startswith(https_url)
                    or full_link.startswith(http_www_url)
                    or full_link.startswith(https_www_url)
                    or full_link.startswith(domain_without_www)
                    or full_link.startswith(self.domain)
                    or f"@{domain_without_www}" in full_link  # For email addresses (it's considered internal)
                )
            )

            # Categorize links as internal or external based on their format
            if full_link.startswith("//"):  # Protocol-relative URLs are external
                alias = "external_links", "raw_external_links", "external_links_structured_list"
            elif full_link.startswith("/"):  # Single slash links are internal
                alias = "internal_links", "raw_internal_links", "internal_links_structured_list"
            elif (link_matches_external_pattern and not link_contains_self_domain) or not link_has_url:
                alias = "external_links", "raw_external_links", "external_links_structured_list"
            else:
                alias = "internal_links", "raw_internal_links", "internal_links_structured_list"
            type_of_links, type_of_raw_links, type_of_structured_links = alias

            # Store the link in three formats:
            # 1. Just the URL
            self.all_links[type_of_links].append(full_link)
            # 2. Raw HTML of the link tag
            self.all_links[type_of_raw_links].append(str(link_tag))
            # 3. Dictionary with all link attributes
            dict_link = {attr: link_tag.attrs[attr] for attr in link_tag.attrs}
            dict_link["full_link"] = full_link
            self.all_links[type_of_structured_links].append(dict_link)
        self.remove_duplicates()

    def remove_duplicates(self) -> None:
        self.all_links["internal_links"] = list(set(self.all_links["internal_links"]))
        self.all_links["external_links"] = list(set(self.all_links["external_links"]))
        self.all_links["raw_internal_links"] = list(set(self.all_links["raw_internal_links"]))
        self.all_links["raw_external_links"] = list(set(self.all_links["raw_external_links"]))

    def get_all_links(self) -> tuple[list[str], list[str], list[dict], list[str], list[str], list[dict]]:
        if self.all_links == self.default_links():
            self.extract_links()

        return (
            self.all_links["internal_links"],
            self.all_links["raw_internal_links"],
            self.all_links["internal_links_structured_list"],
            self.all_links["external_links"],
            self.all_links["raw_external_links"],
            self.all_links["external_links_structured_list"],
        )

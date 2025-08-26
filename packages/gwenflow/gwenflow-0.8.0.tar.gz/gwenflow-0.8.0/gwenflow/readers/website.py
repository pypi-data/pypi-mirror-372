
import time
import random
import httpx
from urllib.parse import urljoin, urlparse

from typing import Set, Dict, List, Tuple

from gwenflow.logger import logger
from gwenflow.readers import PDFReader
from gwenflow.readers.base import Reader
from gwenflow.types import Document
from gwenflow.readers.base import Reader

try:
    from bs4 import BeautifulSoup  # noqa: F401
except ImportError:
    raise ImportError("BeautifulSoup is not installed. Please install it with `pip install beautifulsoup4`.")


class WebsiteReader(Reader):
    """Reader for Websites"""

    max_depth: int = 3
    max_links: int = 100000

    delay: bool = True

    _visited: Set[str] = set()
    _urls_to_crawl: List[Tuple[str, int]] = []

    def sleep(self, min_seconds=1, max_seconds=3):
        """Introduce a random delay."""
        sleep_time = random.uniform(min_seconds, max_seconds)
        time.sleep(sleep_time)

    def _get_primary_domain(self, url: str) -> str:
        """Extract primary domain from the given URL (excluding subdomains)."""
        domain_parts = urlparse(url).netloc.split(".")
        return ".".join(domain_parts[-2:])

    def _extract_html_content(self, soup: BeautifulSoup) -> str:
        """Extracts the main content from a BeautifulSoup object."""

        for tag in ["article", "main"]:
            element = soup.find(tag)
            if element:
                return element.get_text(strip=True, separator=" ")

        for class_name in ["content", "main-content", "page-content", "post-content"]:
            element = soup.find(class_=class_name)
            if element:
                return element.get_text(strip=True, separator=" ")

        return ""

    def _extract_pdf_content(self, url: str) -> str:
        """Extracts the main content from a PDF file."""
        try:
            documents = PDFReader().read(url)
            content = [document.content for document in documents]
            content = "\n\n".join(content)
            return content
        except:
            return ""

    def crawl(self, url: str, starting_depth: int = 1) -> Dict[str, str]:
        """Crawls an url and returns a dictionary of URLs and their corresponding content."""

        num_links = 0
        crawler_result: Dict[str, str] = {}
        primary_domain = self._get_primary_domain(url)

        self._urls_to_crawl.append((url, starting_depth))

        headers = {
            'accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Accept-Language': 'en-US,en;q=0.9,it;q=0.8,es;q=0.7',
            'referer': 'https://www.google.com/',
        }

        with httpx.Client() as client:

            while self._urls_to_crawl:

                # Unpack URL and depth from the global list
                current_url, current_depth = self._urls_to_crawl.pop(0)

                # Skip if...
                if (
                    current_url in self._visited
                    or not urlparse(current_url).netloc.endswith(primary_domain)
                    or current_depth > self.max_depth
                    or num_links >= self.max_links
                ):
                    continue

                self._visited.add(current_url)

                # Delay
                if self.delay:
                    self.sleep()

                # Crawler
                try:
                    logger.debug(f"Reading: {current_url}")
                    response = client.get(current_url, timeout=10, headers=headers)
                    soup = BeautifulSoup(response.content, "html.parser")

                    # Extract main content
                    if current_url.endswith(".pdf"):
                        main_content = self._extract_pdf_content(current_url)
                    else:
                        main_content = self._extract_html_content(soup)

                    crawler_result[current_url] = main_content
                    num_links += 1

                    # Add found URLs to the global list, with incremented depth
                    for link in soup.find_all("a", href=True):
                        full_url = urljoin(current_url, link["href"])
                        parsed_url = urlparse(full_url)

                        # TODO: adjust to use PDFReader and TextReader if files are found
                        if parsed_url.netloc.endswith(primary_domain) and not any(
                            parsed_url.path.endswith(ext) for ext in [".jpg", ".png"]
                        ):
                            if full_url not in self._visited and (full_url, current_depth + 1) not in self._urls_to_crawl:
                                self._urls_to_crawl.append((full_url, current_depth + 1))

                except Exception as e:
                    logger.debug(f"Failed to crawl: {current_url}: {e}")
                    pass

        return crawler_result

    def read(self, url: str) -> List[Document]:
        """Reads a website and returns a list of documents."""

        documents = []

        result = self.crawl(url)

        for url, content in result.items():
            documents.append(
                Document(
                    id=self.key(str(url)),
                    content=content,
                    metadata={"url": str(url)},
                )
            )
        
        return documents
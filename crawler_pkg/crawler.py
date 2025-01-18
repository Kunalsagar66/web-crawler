import asyncio
import logging
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import aiofiles
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Config:
    """Configuration settings for the crawler."""
    USER_AGENT = "Mozilla/5.0"
    TIMEOUT = 10
    PRODUCT_PATTERNS = ["/product/", "/item/", "/p/","/catalogue/"]


class URLUtils:
    """Utility methods for URL handling."""

    @staticmethod
    def is_same_domain(base_url, url):
        """Check if the URL belongs to the same domain as the base URL."""
        return urlparse(base_url).netloc == urlparse(url).netloc

    @staticmethod
    def is_product_url(url, patterns):
        """Check if the URL matches any product patterns."""
        return any(pattern in url for pattern in patterns)


class Fetcher:
    """Handles HTTP requests."""

    def __init__(self):
        self.headers = {"User-Agent": Config.USER_AGENT}

    async def fetch(self, session, url):
        """
        Fetch the content of a URL.
        :param session: The aiohttp session.
        :param url: The URL to fetch.
        :return: HTML content or None if an error occurs.
        """
        try:
            async with session.get(url, timeout=Config.TIMEOUT, headers=self.headers) as response:
                if response.status == 200:
                    return await response.text()
                logging.warning(f"Failed to fetch {url} with status {response.status}")
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
        return None


class Parser:
    """Parses HTML content and extracts links."""

    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()

    async def parse_page(self, html_content, urls_to_visit):
        """
        Parse a page and extract product URLs and discoverable links.
        :param html_content: The HTML content of the page.
        :param urls_to_visit: Queue of URLs to visit.
        :return: A set of product URLs.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        product_urls = set()

        for link in soup.find_all("a", href=True):
            href = urljoin(self.base_url, link["href"])
            if href not in self.visited_urls and URLUtils.is_same_domain(self.base_url, href):
                self.visited_urls.add(href)
                if URLUtils.is_product_url(href, Config.PRODUCT_PATTERNS):
                    product_urls.add(href)
                else:
                    urls_to_visit.append(href)

        return product_urls


class ProductURLCrawler:
    """Main class to manage crawling."""

    def __init__(self, domains):
        self.domains = domains
        self.fetcher = Fetcher()

    async def crawl_domain(self, domain):
        """
        Crawl a single domain to discover product URLs.
        :param domain: The domain to crawl.
        :return: A set of discovered product URLs.
        """
        async with ClientSession() as session:
            urls_to_visit = [domain]
            discovered_product_urls = set()
            parser = Parser(domain)

            while urls_to_visit:
                current_url = urls_to_visit.pop(0)
                logging.info(f"Crawling {current_url}")
                html_content = await self.fetcher.fetch(session, current_url)

                if html_content:
                    product_urls = await parser.parse_page(html_content, urls_to_visit)
                    discovered_product_urls.update(product_urls)

            return discovered_product_urls

    async def start_crawling(self):
        """
        Start crawling all domains and return discovered product URLs.
        :return: A dictionary mapping domains to their product URLs.
        """
        tasks = [self.crawl_domain(domain) for domain in self.domains]
        results = await asyncio.gather(*tasks)

        return {domain: list(result) for domain, result in zip(self.domains, results)}


async def save_results(results, filename="product_urls.json"):
    """
    Save crawling results to a file.
    :param results: The crawling results.
    :param filename: The file to save results to.
    """
    async with aiofiles.open(filename, "w") as f:
        await f.write(json.dumps(results, indent=4))
    logging.info(f"Results saved to {filename}")


async def main():
    """Main function to initiate crawling."""
    domains = ["https://example1.com", "https://example2.com","https://books.toscrape.com"]
    crawler = ProductURLCrawler(domains)
    results = await crawler.start_crawling()
    await save_results(results)


if __name__ == "__main__":
    asyncio.run(main())

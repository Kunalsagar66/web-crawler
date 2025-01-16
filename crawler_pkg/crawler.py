import asyncio
import re
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import aiofiles


class ProductURLCrawler:
    def __init__(self, domains):
        self.domains = domains
        self.product_patterns = ["/product/", "/item/", "/p/"]
        self.visited_urls = set()

    async def fetch(self, session, url):
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
        return None

    def is_product_url(self, url):
        for pattern in self.product_patterns:
            if pattern in url:
                return True
        return False

    async def parse_page(self, session, base_url, url):
        html_content = await self.fetch(session, url)
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        product_urls = set()

        for link in soup.find_all("a", href=True):
            href = urljoin(base_url, link["href"])
            parsed_url = urlparse(href)

            # Ensure the URL belongs to the same domain and avoid duplicates
            if base_url in href and href not in self.visited_urls:
                self.visited_urls.add(href)

                # Check if the URL matches a product pattern
                if self.is_product_url(href):
                    product_urls.add(href)

        return list(product_urls)

    async def crawl_domain(self, domain):
        async with ClientSession() as session:
            urls_to_visit = [domain]
            discovered_product_urls = set()

            while urls_to_visit:
                current_url = urls_to_visit.pop(0)
                self.visited_urls.add(current_url)
                product_urls = await self.parse_page(session, domain, current_url)
                discovered_product_urls.update(product_urls)

            return discovered_product_urls

    async def start_crawling(self):
        tasks = [self.crawl_domain(domain) for domain in self.domains]
        results = await asyncio.gather(*tasks)

        # Map domains to their discovered product URLs
        domain_to_urls = {
            domain: list(result) for domain, result in zip(self.domains, results)
        }  # Convert sets to lists

        return domain_to_urls


async def main():
    domains = ["https://example1.com", "https://example2.com"]  # Add more domains here
    crawler = ProductURLCrawler(domains)

    results = await crawler.start_crawling()

    # Save the results to a file
    async with aiofiles.open("product_urls.json", "w") as f:
        import json
        await f.write(json.dumps(results, indent=4))

    print("Crawling completed. Results saved to 'product_urls.json'.")


if __name__ == "__main__":
    asyncio.run(main())

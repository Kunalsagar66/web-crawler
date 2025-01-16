# E-commerce Product URL Crawler

## Objective
This tool discovers product URLs from e-commerce websites, mapping each domain to its respective product pages.

## Features
- Supports asynchronous crawling for efficiency.
- Handles multiple domains simultaneously.
- Identifies product URLs using common patterns like `/product/`, `/item/`, `/p/`.

## Requirements
- Python 3.8+
- Libraries: `requests`, `beautifulsoup4`, `aiohttp`, `aiofiles`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Kunalsagar66/web-crawler.git
   cd crawler

2. Install dependencies:
    bash
    pip install -r requirements.txt

## Usage
1. Add domains to the domains list in crawler.py.
2. Run the crawler:
    bash
    Copy code
    python crawler.py
3. View results in results.json.

## Output Format
json:
{
  "example1.com": ["https://example1.com/product/123", ...],
  "example2.com": ["https://example2.com/item/456", ...]
}
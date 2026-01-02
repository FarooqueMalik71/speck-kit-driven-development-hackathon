import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
from typing import List, Set, Optional
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)


class CrawlerService:
    """
    Service for crawling Docusaurus book websites to extract all page URLs and content
    """

    def __init__(self, rate_limit_delay: float = 1.0, max_pages: int = 1000, timeout: int = 30):
        self.rate_limit_delay = rate_limit_delay
        self.max_pages = max_pages
        self.timeout = timeout
        self.session = requests.Session()
        # Set a user agent to be respectful to servers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RAG-Crawler/1.0; +https://example.com/bot)'
        })

    def get_all_page_urls(self, root_url: str) -> List[str]:
        """
        Discover and return all page URLs within the Docusaurus book
        """
        logger.info(f"Starting to crawl: {root_url}")
        all_urls = set()
        to_visit = [root_url]
        visited = set()

        while to_visit and len(all_urls) < self.max_pages:
            current_url = to_visit.pop(0)

            # Skip if already visited
            if current_url in visited:
                continue

            visited.add(current_url)

            try:
                # Respect rate limiting
                time.sleep(self.rate_limit_delay)

                logger.info(f"Crawling: {current_url}")
                response = self.session.get(current_url, timeout=self.timeout)

                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {current_url}: Status {response.status_code}")
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract all links from the page
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    absolute_url = urljoin(current_url, href)

                    # Only keep URLs from the same domain and that look like pages
                    if self._is_valid_page_url(absolute_url, root_url):
                        if absolute_url not in visited and absolute_url not in to_visit:
                            to_visit.append(absolute_url)
                            all_urls.add(absolute_url)

            except requests.RequestException as e:
                logger.error(f"Error crawling {current_url}: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error crawling {current_url}: {str(e)}")
                continue

        logger.info(f"Crawling completed. Found {len(all_urls)} unique URLs")
        return list(all_urls)

    def get_page_content(self, url: str) -> Optional[str]:
        """
        Extract clean content from a single page
        """
        try:
            time.sleep(self.rate_limit_delay)  # Respect rate limiting
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code != 200:
                logger.warning(f"Failed to fetch {url}: Status {response.status_code}")
                return None

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove unwanted elements like navigation, headers, footers, etc.
            for element in soup(['nav', 'header', 'footer', 'aside', 'script', 'style']):
                element.decompose()

            # Try to find the main content area in Docusaurus sites
            # Docusaurus typically uses these selectors for main content
            main_content = (
                soup.select_one('main div[class*="container"]') or
                soup.select_one('main article') or
                soup.select_one('main') or
                soup.select_one('article') or
                soup.select_one('div[class*="docItem"]') or
                soup.select_one('div[class*="markdown"]') or
                soup.find('div', class_=lambda x: x and ('doc' in x or 'content' in x or 'main' in x))
            )

            if main_content:
                # Extract text content, removing extra whitespace
                content = main_content.get_text(separator=' ', strip=True)
            else:
                # Fallback to body content if main content not found
                body = soup.find('body')
                if body:
                    content = body.get_text(separator=' ', strip=True)
                else:
                    content = soup.get_text(separator=' ', strip=True)

            # Clean up the content
            content = self._clean_content(content)

            return content

        except requests.RequestException as e:
            logger.error(f"Error fetching content from {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return None

    def _is_valid_page_url(self, url: str, root_url: str) -> bool:
        """
        Check if a URL is a valid page URL within the same domain
        """
        try:
            parsed_url = urlparse(url)
            parsed_root = urlparse(root_url)

            # Check if it's the same domain
            if parsed_url.netloc != parsed_root.netloc:
                return False

            # Check if it's an HTML page (not a file download, etc.)
            if any(parsed_url.path.endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.zip', '.exe', '.jpg', '.png', '.gif']):
                return False

            # Check if it's not an external link
            if url.startswith(('http://', 'https://')) and parsed_url.netloc != parsed_root.netloc:
                return False

            # Exclude common non-page URLs
            excluded_paths = ['/api/', '/assets/', '/static/', '/images/', '/img/']
            for excluded_path in excluded_paths:
                if excluded_path in parsed_url.path:
                    return False

            return True

        except Exception:
            return False

    def _clean_content(self, content: str) -> str:
        """
        Clean extracted content to remove noise
        """
        if not content:
            return ""

        # Remove extra whitespace and normalize
        import re
        # Replace multiple whitespace characters with single space
        content = re.sub(r'\s+', ' ', content)
        # Remove leading/trailing whitespace
        content = content.strip()

        # Remove common navigation elements that might have slipped through
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:  # Only keep lines with meaningful content
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def get_page_title(self, url: str) -> str:
        """
        Extract the title from a page
        """
        try:
            time.sleep(self.rate_limit_delay)  # Respect rate limiting
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code != 200:
                return ""

            soup = BeautifulSoup(response.content, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text().strip()
            else:
                # Try to find a heading that might serve as title
                h1 = soup.find('h1')
                if h1:
                    return h1.get_text().strip()
                return ""

        except Exception as e:
            logger.error(f"Error extracting title from {url}: {str(e)}")
            return ""


if __name__ == "__main__":
    # Example usage
    crawler = CrawlerService(rate_limit_delay=0.5, max_pages=10)

    # Example: Crawl a sample Docusaurus site
    # urls = crawler.get_all_page_urls("https://example-docusaurus-site.com")
    # print(f"Found {len(urls)} URLs")
    #
    # for url in urls[:3]:  # Just process first 3 for example
    #     content = crawler.get_page_content(url)
    #     title = crawler.get_page_title(url)
    #     print(f"\nURL: {url}")
    #     print(f"Title: {title}")
    #     print(f"Content preview: {content[:200]}...")
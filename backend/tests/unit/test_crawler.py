import unittest
from unittest.mock import Mock, patch, MagicMock
from src.services.crawler import CrawlerService
import requests


class TestCrawlerService(unittest.TestCase):
    """
    Unit tests for CrawlerService
    """

    def setUp(self):
        """
        Set up test fixtures
        """
        self.crawler = CrawlerService(rate_limit_delay=0.01, max_pages=10)

    def test_init(self):
        """
        Test that CrawlerService initializes correctly
        """
        self.assertEqual(self.crawler.rate_limit_delay, 0.01)
        self.assertEqual(self.crawler.max_pages, 10)
        self.assertIsNotNone(self.crawler.session)

    @patch('src.services.crawler.requests.Session.get')
    def test_get_page_content_success(self, mock_get):
        """
        Test that get_page_content works with successful response
        """
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html><body><main><p>Test content</p></main></body></html>'
        mock_get.return_value = mock_response

        # Call method
        content = self.crawler.get_page_content('https://example.com')

        # Assertions
        self.assertIsNotNone(content)
        self.assertIn('Test content', content)
        mock_get.assert_called_once()

    @patch('src.services.crawler.requests.Session.get')
    def test_get_page_content_failure(self, mock_get):
        """
        Test that get_page_content handles failed requests
        """
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Call method
        content = self.crawler.get_page_content('https://example.com')

        # Assertions
        self.assertIsNone(content)

    @patch('src.services.crawler.requests.Session.get')
    def test_get_page_content_exception(self, mock_get):
        """
        Test that get_page_content handles exceptions
        """
        # Mock exception
        mock_get.side_effect = requests.RequestException("Connection error")

        # Call method
        content = self.crawler.get_page_content('https://example.com')

        # Assertions
        self.assertIsNone(content)

    def test_is_valid_page_url_same_domain(self):
        """
        Test that is_valid_page_url correctly identifies valid URLs
        """
        root_url = "https://example.com/docs"
        test_url = "https://example.com/docs/intro"

        result = self.crawler._is_valid_page_url(test_url, root_url)

        self.assertTrue(result)

    def test_is_valid_page_url_different_domain(self):
        """
        Test that is_valid_page_url rejects different domains
        """
        root_url = "https://example.com"
        test_url = "https://other.com/page"

        result = self.crawler._is_valid_page_url(test_url, root_url)

        self.assertFalse(result)

    def test_clean_content(self):
        """
        Test that clean_content removes extra whitespace
        """
        dirty_content = "   This   is   messy   content   \n\n\n   with   extra   spaces   "
        expected = "This is messy content with extra spaces"

        result = self.crawler._clean_content(dirty_content)

        self.assertEqual(result, expected)

    def test_is_valid_page_url_excluded_paths(self):
        """
        Test that is_valid_page_url excludes certain paths
        """
        root_url = "https://example.com"

        excluded_urls = [
            "https://example.com/api/users",
            "https://example.com/assets/style.css",
            "https://example.com/static/main.js",
            "https://example.com/images/photo.jpg"
        ]

        for url in excluded_urls:
            with self.subTest(url=url):
                result = self.crawler._is_valid_page_url(url, root_url)
                self.assertFalse(result, f"URL {url} should be excluded")


if __name__ == '__main__':
    unittest.main()
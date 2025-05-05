import requests
import re
import logging
import time
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup basic logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

class TokenScraper:
    def __init__(self, url, max_retries = 3, backoff_factor = 0.5):
        self.url = url
        self.token = None
        self.session_id = None
        self.session = self._create_session(max_retries, backoff_factor)

    def _create_session(self, max_retries, backoff_factor):
        """Create a requests Session with retry strategy."""
        session = requests.Session()
        retries = Retry(
            total = max_retries,
            backoff_factor = backoff_factor,
            status_forcelist = [429, 500, 502, 503, 504],
            allowed_methods = ["GET"]
        )
        adapter = HTTPAdapter(max_retries = retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def scrape(self):
        """Main method to perform scraping."""
        try:
            response = self._fetch_html()
            script_content = self._extract_script_content(response.text)
            self.token = self._extract_token(script_content)
            self.session_id = self._extract_session_id(response.cookies)
            logger.info("Successfully scraped token and session ID.")
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise

    def _fetch_html(self):
        """Fetch the page HTML content."""
        try:
            logger.info(f"Fetching URL: {self.url}")
            response = self.session.get(self.url, timeout = 10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            raise

    def _extract_script_content(self, html_text):
        """Extract the <script> tag content containing 'ajax_token'."""
        soup = BeautifulSoup(html_text, 'html.parser')
        script_tag = soup.find('script', text = re.compile('ajax_token'))

        if not script_tag or not script_tag.string:
            error_msg = "Couldn't find the script tag containing 'ajax_token'."
            logger.error(error_msg)
            raise ValueError(error_msg)

        return script_tag.string

    def _extract_token(self, script_content):
        """Extract the ajax_token from script content."""
        match = re.search(r"ajax_token\s*=\s*'([a-z0-9]{64})'", script_content)
        if not match:
            error_msg = "Couldn't extract 'ajax_token' from the script content."
            logger.error(error_msg)
            raise ValueError(error_msg)
        return match.group(1)

    def _extract_session_id(self, cookies):
        """Extract the PHPSESSID cookie."""
        try:
            return cookies['PHPSESSID']
        except KeyError:
            error_msg = "PHPSESSID cookie not found in response."
            logger.error(error_msg)
            raise ValueError(error_msg)

    def get_credentials(self):
        """Retrieve scraped credentials."""
        if not self.token or not self.session_id:
            raise ValueError("Token or Session ID not scraped yet. Call scrape() first.")
        return {
            'token': self.token,
            'session_id': self.session_id
        }

import requests
import json
import logging
import time

# Set up logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

class BalanceFetcher:
    def __init__(self, url_api, card_number, card_code, token, session_id, max_retries = 3, retry_delay = 2):
        self.url_api = url_api
        self.card_number = card_number
        self.card_code = card_code
        self.token = token
        self.session_id = session_id
        self.max_retries = max_retries
        self.retry_delay = retry_delay  # seconds
        self.accomodation = None
        self.active_hungarians = None

    def fetch_balance(self):
        """Fetch balance information with retries."""
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Fetching balance (Attempt {attempt})...")
                response = self._send_balance_request()

                response_data = self._parse_response(response)

                if response_data[0] == 'RC':
                    logger.warning('Captcha triggered due to too many requests.')
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        raise RuntimeError('Captcha protection could not be bypassed after retries.')

                elif response_data[0] == 'HI':
                    raise ValueError('Invalid card number or card code.')

                self._extract_balances(response_data)
                logger.info("Balance fetched successfully.")
                break  # Success! Exit the retry loop.

            except (requests.RequestException, ValueError, RuntimeError) as e:
                logger.error(f"Attempt {attempt} failed: {e}")
                if attempt == self.max_retries:
                    raise  # Re-raise on final failure
                time.sleep(self.retry_delay)

    def _send_balance_request(self):
        """Send POST request to fetch balance data."""
        request_body = {
            's_azonosito_k': self.card_number,
            's_telekod_k': self.card_code,
            'ajax_token': self.token,
            's_captcha': ''
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }

        cookies = {'PHPSESSID': self.session_id}

        response = requests.post(
            self.url_api,
            headers = headers,
            data = request_body,
            cookies = cookies,
            timeout = 10  # Add timeout to avoid hanging
        )
        response.raise_for_status()  # Raise HTTP errors automatically
        return response

    def _parse_response(self, response):
        """Parse JSON from the API response."""
        try:
            return response.json()
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {e}")
            raise ValueError('Invalid JSON response from server.')

    def _extract_balances(self, response_data):
        """Extract balances from parsed response."""
        try:
            self.accomodation = response_data[1]['szamla_osszeg9']
            self.active_hungarians = response_data[1]['szamla_osszeg8']
        except (KeyError, TypeError, IndexError) as e:
            logger.error(f"Error parsing balance fields: {e}")
            raise ValueError('Malformed balance data received.')

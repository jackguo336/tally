import logging
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.parse import urlencode

from tally.models.club_feed import FeedResponse


logger = logging.getLogger(__name__)


class StravaService:
    def __init__(self):
        self.driver: webdriver.Chrome = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=Options()
        )
        self.is_logged_in = False

    def get_club_feed(self, club_id: str, cursor: str = None) -> FeedResponse:
        self.login()

        logger.debug(f"Getting club feed for club {club_id} with cursor {cursor}")
        try:
            feed_json = self._get_json_content(
                f"https://www.strava.com/clubs/{club_id}/feed",
                params={
                    "feed_type": "club",
                    "club_id": club_id,
                    "before": cursor,
                    "cursor": cursor,
                },
            )
        except Exception as e:
            raise Exception(f"Failed to get activities: {e}")

        return FeedResponse.model_validate(feed_json)

    def _get_json_content(self, url: str, params: dict) -> str:
        # Ensure params that are None are not included in the URL
        formatted_params = urlencode({k: v for k, v in params.items() if v is not None})
        url_with_params = f"{url}?{formatted_params}" if formatted_params else url

        self.driver.get(url_with_params)
        return json.loads(self.driver.find_element(By.TAG_NAME, "pre").text)

    def login(self) -> None:
        if self.is_logged_in:
            return

        print("Log in to Strava to provide access to team and user activity data")
        self.driver.get("https://www.strava.com/login")

        # Wait for user to be logged in
        login_wait_timeout = 30
        max_login_wait_attempts = 3
        for index in range(max_login_wait_attempts):
            try:
                WebDriverWait(self.driver, login_wait_timeout).until(
                    EC.presence_of_element_located((By.ID, "athlete-profile"))
                )
                self.is_logged_in = True
                break
            except TimeoutException:
                print(
                    f"Waiting for login to complete (attempt {index + 1} of {max_login_wait_attempts})"
                )
                continue
        else:
            raise Exception("Failed to log in to Strava")

        print("Login successful")

    def __del__(self):
        self.driver.quit()

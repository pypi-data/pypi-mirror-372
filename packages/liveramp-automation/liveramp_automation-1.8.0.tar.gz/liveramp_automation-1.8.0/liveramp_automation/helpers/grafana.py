import json
import copy
from typing import Dict, Any
from playwright.sync_api import sync_playwright, Response
from liveramp_automation.utils.log import Logger


class GrafanaAuthenticationError(Exception):
    """Custom exception for Grafana authentication failures."""

    pass


class GrafanaAPIError(Exception):
    """Custom exception for Grafana API failures."""

    pass


class GrafanaClient:
    """
    GrafanaClient provides a context-managed interface for authenticating with Grafana
    using the "Sign in with Grafana.com" option and performing authenticated API queries 
    to Loki via Playwright.

    This client automates the browser-based authentication flow and provides a clean
    interface for querying Loki data sources through Grafana's API.

    Usage:
        with GrafanaClient(username, password) as client:
            response = client.query_loki(payload_data)

    Attributes:
        _username (str): The username/email for Grafana.com login.
        _password (str): The password for Grafana.com login.
        _base_url (str): The base Grafana URL.
        _headless (bool): Whether to run browser in headless mode.
        _timeout (int): Timeout for operations in milliseconds.
        _login_url (str): The complete login URL.
        _api_url (str): The complete API query URL.
    """

    def __init__(
        self,
        username: str,
        password: str,
        base_url: str = "https://liveramp.grafana.net",
        headless: bool = True,
        timeout: int = 60000,
    ):
        """
        Initialize the GrafanaClient with user credentials and configuration.

        Args:
            username (str): The username/email for Grafana.com login.
            password (str): The password for Grafana.com login.
            base_url (str, optional): The base Grafana URL. 
                Defaults to "https://liveramp.grafana.net".
            headless (bool, optional): Whether to run browser in headless mode. 
                Defaults to True.
            timeout (int, optional): Timeout for operations in milliseconds. 
                Defaults to 60000 (60 seconds).

        Note:
            The base_url will have any trailing slashes automatically removed.
        """
        self._username = username
        self._password = password
        self._base_url = base_url.rstrip("/")
        self._headless = headless
        self._timeout = timeout

        # Playwright instances
        self._p = None
        self._browser = None
        self._context = None
        self._page = None

        # URLs
        self._login_url = f"{self._base_url}/login"
        self._api_url = f"{self._base_url}/api/ds/query"

    def __enter__(self):
        """
        Enter the context manager, launching a browser and performing authentication.

        This method:
        1. Launches a Chromium browser instance
        2. Creates a new browser context and page
        3. Performs the authentication flow
        4. Returns the authenticated client instance

        Returns:
            GrafanaClient: The authenticated client instance ready for use.

        Raises:
            GrafanaAuthenticationError: If initialization or authentication fails.

        Note:
            The browser is configured with security and performance optimizations
            including disabled web security for API access.
        """
        Logger.info("Initializing GrafanaClient...")
        try:
            self._p = sync_playwright().start()
            self._browser = self._p.chromium.launch(
                headless=self._headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                ],
            )
            self._context = self._browser.new_context(
                viewport={"width": 1920, "height": 1080},
            )
            self._page = self._context.new_page()

            self._authenticate()
            Logger.info("GrafanaClient created successfully and authenticated.")
            return self

        except Exception as e:
            Logger.error(f"Failed to initialize GrafanaClient: {e}")
            self._cleanup()
            raise GrafanaAuthenticationError(f"Failed to initialize: {e}")

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager, ensuring proper cleanup of all resources.

        This method automatically cleans up:
        - Browser page
        - Browser context
        - Browser instance
        - Playwright process

        Args:
            exc_type: The exception type if an exception occurred.
            exc_value: The exception value if an exception occurred.
            traceback: The traceback if an exception occurred.

        Note:
            Cleanup is performed regardless of whether an exception occurred.
            Any cleanup errors are logged as warnings but don't prevent exit.
        """
        Logger.info("Exiting GrafanaClient context. Cleaning up resources.")
        self._cleanup()

    def _cleanup(self):
        """
        Clean up Playwright resources in the correct order.

        This method ensures all browser resources are properly closed:
        1. Page (closes the current tab)
        2. Context (closes the browser context)
        3. Browser (closes the browser instance)
        4. Playwright process (stops the Playwright service)

        Note:
            Cleanup is performed in reverse order of creation to ensure
            proper resource deallocation. Any errors during cleanup are
            logged as warnings but don't interrupt the cleanup process.
        """
        resources = [
            (self._page, "close"),
            (self._context, "close"),
            (self._browser, "close"),
            (self._p, "stop"),
        ]

        for resource, method_name in resources:
            if resource:
                try:
                    getattr(resource, method_name)()
                except Exception as e:
                    Logger.warning(
                        f"Error during cleanup of {resource.__class__.__name__}: {e}"
                    )

    def _authenticate(self):
        """
        Perform the authentication flow using "Sign in with Grafana.com".

        This method automates the complete login process:
        1. Navigates to the Grafana login page
        2. Clicks the "Sign in with Grafana.com" button
        3. Fills in the username/email field
        4. Submits the username and clicks "Sign In"
        5. Fills in the password field
        6. Submits the password and completes authentication
        7. Waits for successful login by checking for the home page URL

        Raises:
            GrafanaAuthenticationError: If any step of the authentication process fails.

        Note:
            The method uses Playwright's role-based selectors for robust element
            identification. It waits for the page to reach the home URL to confirm
            successful authentication.
        """
        Logger.debug("Starting authentication...")

        # Navigate to login page
        Logger.debug("Navigating to Grafana login page...")
        self._page.goto(self._login_url, timeout=self._timeout)

        # Wait for page to load
        self._page.wait_for_load_state("networkidle", timeout=self._timeout)

        # Click login button
        Logger.debug("Clicking login button...")
        login_button = self._page.get_by_role("link", name="Sign in with Grafana.com")
        login_button.click()

        # Fill username
        Logger.debug("Filling username...")
        username_field = self._page.get_by_role("textbox", name="Email or username")
        username_field.fill(self._username)

        # Click next
        next_button = self._page.get_by_role("button", name="Sign In")
        next_button.click()

        # Fill password
        Logger.debug("Filling password...")
        password_field = self._page.get_by_role("textbox", name="Password")
        password_field.fill(self._password)

        # Submit
        submit_button = self._page.get_by_role("button", name="Sign In")
        submit_button.click()

        # Wait for successful login
        Logger.debug("Waiting for successful login...")
        self._page.wait_for_url("**/home", timeout=30000)

        Logger.info("Authentication successful!")

    def query_loki(
        self, payload: dict, from_timestamp: str = None, to_timestamp: str = None
    ) -> Dict[str, Any]:
        """
        Perform an authenticated API query to the Loki data source.

        This method sends a POST request to Grafana's datasource query API
        with the provided Loki query payload. It automatically handles
        authentication headers and can optionally override timestamps.

        Args:
            payload (dict): The Loki query payload containing queries, timestamps,
                and datasource configuration. Must follow Grafana's Loki query format.
            from_timestamp (str, optional): Override the 'from' timestamp in the payload.
                If provided, this value will replace the existing 'from' field.
                Defaults to None (no override).
            to_timestamp (str, optional): Override the 'to' timestamp in the payload.
                If provided, this value will replace the existing 'to' field.
                Defaults to None (no override).

        Returns:
            Dict[str, Any]: The parsed JSON response from the Loki API containing
                query results and metadata.

        Raises:
            GrafanaAPIError: If the API query fails due to network issues,
                authentication problems, or API errors.

        Note:
            - The original payload is not modified; a deep copy is created for processing.
            - Timestamp overrides are applied after copying the payload.
            - The API request includes appropriate headers and parameters for Loki queries.
            - All API responses are validated for success status before returning.
        """
        # Create a deep copy of the payload to avoid modifying the original
        payload = copy.deepcopy(payload)

        # Override timestamps if provided
        if from_timestamp:
            payload["from"] = from_timestamp
        if to_timestamp:
            payload["to"] = to_timestamp
        headers = {"content-type": "application/json"}
        params = {"ds_type": "loki"}

        Logger.debug(f"Sending POST request to {self._api_url}")
        Logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

        try:
            response: Response = self._context.request.post(
                self._api_url,
                data=json.dumps(payload),
                headers=headers,
                params=params,
                timeout=self._timeout,
            )

            if not response.ok:
                error_message = (
                    f"API query failed.\n"
                    f"Status Code: {response.status}\n"
                    f"Response Text: {response.text()}"
                )
                Logger.error(error_message)
                raise GrafanaAPIError(error_message)

            Logger.info(f"API query successful. Status: {response.status}")
            return response.json()

        except Exception as e:
            if isinstance(e, GrafanaAPIError):
                raise
            raise GrafanaAPIError(f"API query failed: {e}")

"""
# Example usage and testing
if __name__ == "__main__":
    # Example configuration
    config = {
        "username": "qe.eng.testing@liveramp.com",
        "password": "XXXXXXXXXXXXXXX",
        "headless": False,
        "timeout": 60000,
    }

    # Example Loki query payload
    loki_payload = {
        "queries": [
            {
                "refId": "A",
                "expr": '{team="opi", cluster_name="opi-prod-2", exporter="OTLP", environment="prod"} |= `6507093151`',
                "queryType": "range",
                "datasource": {"type": "loki", "uid": "grafanacloud-logs"},
                "maxLines": 1000,
                "direction": "backward",
            }
        ],
        "from": "1756131268306",  # Start timestamp in milliseconds
        "to": "1756217668306",  # End timestamp in milliseconds
    }

    try:
        with GrafanaClient(**config) as client:
            # Query Loki with the payload
            loki_response = client.query_loki(loki_payload)
            Logger.info(f"Loki query results: {loki_response}")

    except GrafanaAuthenticationError as e:
        Logger.error(f"Authentication failed: {e}")
    except GrafanaAPIError as e:
        Logger.error(f"API error: {e}")
    except Exception as e:
        Logger.error(f"Unexpected error: {e}")
"""
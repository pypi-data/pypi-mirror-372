import platform
import subprocess
import time
import warnings
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any, List, Optional, Union

import requests
from selenium import webdriver
from selenium.common.exceptions import (
    InvalidSelectorException,
    MoveTargetOutOfBoundsException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .__logs import LogManager

warnings.filterwarnings(action="ignore")


if platform.system() == "Windows":
    import winreg


class CustomChromeDriverManager:
    """
    Manages the automated download and installation of ChromeDriver, ensuring
    compatibility with the installed version of Google Chrome.
    Works on Windows, Linux, and macOS.
    """

    CHROME_DRIVER_JSON_URL = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"

    def __init__(self, path: Optional[Union[str, Path]] = None, verify_ssl: bool = True):
        self.verify_ssl = verify_ssl
        self.system = platform.system()
        self.root_path = Path(path) if path else Path.cwd()
        self.driver_filename = "chromedriver.exe" if self.system == "Windows" else "chromedriver"
        self.driver_path = self.root_path / self.driver_filename

    def install(self) -> str:
        """
        Orquestra o processo de verificação e instalação para o Chromedriver.

        Retorna o caminho (string) para o driver executável.
        """
        chrome_version = self._get_installed_chrome_version()
        if not chrome_version:
            raise ValueError("Could not find installed Google Chrome version.")

        print(f"Google Chrome version {chrome_version} detected.")
        download_url = self._get_driver_download_url(chrome_version)
        if not download_url:
            raise RuntimeError(
                f"Could not find a ChromeDriver download URL for version {chrome_version}"
            )

        driver_executable_path = self._download_and_place_driver(download_url)
        if not driver_executable_path:
            raise RuntimeError("Failed to download and extract ChromeDriver.")

        return str(driver_executable_path)

    def _get_installed_chrome_version(self) -> Optional[str]:
        """Checks the version of Google Chrome installed on the system."""
        version_checkers = {
            "Windows": self._get_chrome_version_windows,
            "Linux": self._get_chrome_version_linux_or_mac,
            "Darwin": self._get_chrome_version_linux_or_mac,
        }
        checker = version_checkers.get(self.system)
        if checker:
            return checker()
        return None

    def _get_chrome_version_windows(self) -> Optional[str]:
        """Checks the installed Google Chrome version on Windows by reading the registry."""
        for root_key in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
            try:
                with winreg.OpenKey(root_key, r"Software\Google\Chrome\BLBeacon") as key:
                    version, _ = winreg.QueryValueEx(key, "version")
                    if version:
                        return version
            except (FileNotFoundError, NameError):
                continue
        return None

    def _get_chrome_version_linux_or_mac(self) -> Optional[str]:
        """Checks the installed Google Chrome version on Linux or macOS."""
        executables = {
            "Linux": [
                "google-chrome",
                "google-chrome-stable",
                "chromium-browser",
                "chromium",
            ],
            "Darwin": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
        }
        for executable in executables.get(self.system, []):
            try:
                result = subprocess.run(
                    [executable, "--version"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                return result.stdout.strip().split()[-1]
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
        return None

    def _get_driver_download_url(self, chrome_version: str) -> Optional[str]:
        """
        Finds the download URL for the ChromeDriver corresponding to the Chrome version and platform.
        """
        major_version = chrome_version.split(".")[0]
        platform_mapping = {
            "Linux": "linux64",
            "Darwin": "mac-arm64" if platform.machine() == "arm64" else "mac-x64",
            "Windows": "win64",
        }
        platform_name = platform_mapping.get(self.system)
        if not platform_name:
            return None

        try:
            response = requests.get(self.CHROME_DRIVER_JSON_URL, verify=self.verify_ssl)
            response.raise_for_status()
            data = response.json()

            for channel_data in data.get("channels", {}).values():
                if channel_data.get("version", "").startswith(major_version):
                    for download in channel_data.get("downloads", {}).get("chromedriver", []):
                        if download.get("platform") == platform_name:
                            return download.get("url")
            return None
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error accessing Chrome driver API: {e}") from e

    def _download_and_place_driver(self, url: str) -> Optional[Path]:
        """Downloads, extracts, and places the ChromeDriver in the target path."""
        try:
            print(f"Downloading driver from: {url}")
            response = requests.get(url, stream=True, verify=self.verify_ssl)
            response.raise_for_status()

            with BytesIO(response.content) as buffer, zipfile.ZipFile(buffer) as zf:
                driver_entry_name = next(
                    (name for name in zf.namelist() if name.endswith(self.driver_filename)),
                    None,
                )

                if driver_entry_name:
                    extracted_content = zf.read(driver_entry_name)
                    self.driver_path.parent.mkdir(parents=True, exist_ok=True)
                    self.driver_path.write_bytes(extracted_content)

                    if self.system in ["Linux", "Darwin"]:
                        self.driver_path.chmod(0o755)

                    return self.driver_path
            return None
        except (requests.RequestException, zipfile.BadZipFile, OSError, StopIteration) as e:
            raise RuntimeError(f"An error occurred during download or extraction: {e}") from e


class WebDriverManipulator:
    """
    A WebDriver wrapper class that automates driver management and provides a simplified
    interface for browser interaction. Designed to be extensible.
    """

    def __init__(
        self,
        driver_path: Optional[Union[str, Path]] = None,
        options: Optional[ChromeOptions] = None,
        default_timeout: int = 30,
        verify_ssl: bool = False,
    ):
        # Instantiate the corrected LogManager and get the logger
        log_manager = LogManager()
        self._logger, self.exception_decorator = log_manager.get_logger()
        self.default_timeout = default_timeout

        try:
            self.driver: WebDriver = self._initialize_driver(driver_path, options, verify_ssl)
            self.action_chains = ActionChains(self.driver)
            self._logger.info("Web session initialized successfully.")
        except Exception as e:
            self._logger.error(f"Failed to initialize web session: {e}")
            raise

    def _initialize_driver(
        self,
        driver_path: Optional[Union[str, Path]],
        options: Optional[ChromeOptions],
        verify_ssl: bool,
    ) -> WebDriver:
        self._logger.debug("Initializing WebDriver.")

        if not driver_path:
            self._logger.info("No driver_path provided. Using automatic driver manager.")
            manager = CustomChromeDriverManager(verify_ssl=verify_ssl)
            driver_path = manager.install()

        if not Path(driver_path).is_file():
            raise FileNotFoundError(f"ChromeDriver executable not found at: {driver_path}")

        service = ChromeService(executable_path=str(driver_path))
        return webdriver.Chrome(service=service, options=options)

    def quit(self):
        if hasattr(self, "driver") and self.driver:
            self._logger.info("Closing WebDriver session.")
            self.driver.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def _get_by_strategy(self, selector_type: str) -> By:
        strategy_map = {
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "xpath": By.XPATH,
            "tag_name": By.TAG_NAME,
            "css_selector": By.CSS_SELECTOR,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT,
        }
        normalized_type = selector_type.lower().strip()
        if normalized_type not in strategy_map:
            self._logger.error(f"Unsupported selector type: '{selector_type}'")
            raise ValueError(
                f"Selector '{selector_type}' is not supported. Use one of {list(strategy_map.keys())}."
            )
        return strategy_map[normalized_type]

    def find_element(
        self,
        selector_value: str,
        selector_type: str = "xpath",
        timeout: Optional[int] = None,
        raise_exception: bool = True,
    ) -> Optional[WebElement]:
        current_timeout = timeout if timeout is not None else self.default_timeout
        by_strategy = self._get_by_strategy(selector_type)

        try:
            wait = WebDriverWait(self.driver, current_timeout)
            element = wait.until(EC.presence_of_element_located((by_strategy, selector_value)))
            self._logger.debug(f"Element '{selector_value}' found by {selector_type}.")
            return element
        except (TimeoutException, NoSuchElementException):
            if raise_exception:
                self._logger.error(
                    f"Element '{selector_value}' not found by {selector_type} within {current_timeout}s."
                )
                raise
            self._logger.warning(
                f"Element '{selector_value}' not found by {selector_type} (exception suppressed)."
            )
            return None
        except InvalidSelectorException:
            self._logger.error(f"Invalid selector: '{selector_value}' ({selector_type}).")
            if raise_exception:
                raise
            return None

    def find_elements(
        self,
        selector_value: str,
        selector_type: str = "xpath",
        timeout: Optional[int] = None,
        min_elements: int = 0,
    ) -> List[WebElement]:
        current_timeout = timeout if timeout is not None else self.default_timeout
        by_strategy = self._get_by_strategy(selector_type)

        try:
            wait = WebDriverWait(self.driver, current_timeout)
            if min_elements > 0:
                wait.until(
                    lambda d: len(d.find_elements(by_strategy, selector_value)) >= min_elements
                )
            
            elements = self.driver.find_elements(by_strategy, selector_value)
            self._logger.debug(
                f"Found {len(elements)} elements for '{selector_value}' by {selector_type}."
            )
            return elements
        except TimeoutException:
            self._logger.error(
                f"Timeout: Could not find at least {min_elements} elements for '{selector_value}' in {current_timeout}s."
            )
            raise
        except InvalidSelectorException:
            self._logger.error(
                f"Invalid selector when finding elements: '{selector_value}' ({selector_type})."
            )
            raise

    def find_element_in_frames(
        self,
        selector_value: str,
        selector_type: str = "xpath",
        timeout: Optional[int] = None,
        raise_exception: bool = True,
    ) -> Optional[WebElement]:
        current_timeout = timeout if timeout is not None else self.default_timeout
        end_time = time.time() + current_timeout

        self._logger.info(
            f"Starting recursive frame search for '{selector_value}'. Timeout: {current_timeout}s."
        )
        
        self.driver.switch_to.default_content()
        result = self._search_in_frame_recursively(selector_value, selector_type, end_time)
        self.driver.switch_to.default_content()

        if result:
            self._logger.info(f"Element '{selector_value}' found in a frame.")
            return result

        if raise_exception:
            self._logger.error(f"Element '{selector_value}' not found in any frame after recursive search.")
            raise NoSuchElementException(f"Element '{selector_value}' not found in any frame.")
        
        return None

    def _search_in_frame_recursively(self, selector: str, by: str, end_time: float) -> Optional[WebElement]:
        if time.time() > end_time:
            return None

        try:
            element = self.find_element(selector, by, timeout=1, raise_exception=False)
            if element:
                return element
        except Exception:
            pass

        frames = self.driver.find_elements(By.TAG_NAME, "iframe") + self.driver.find_elements(By.TAG_NAME, "frame")

        for frame in frames:
            if time.time() > end_time:
                break
            
            try:
                self.driver.switch_to.frame(frame)
                self._logger.debug("Switched to a nested frame.")
                
                found_element = self._search_in_frame_recursively(selector, by, end_time)
                if found_element:
                    return found_element
                    
            except Exception as e:
                self._logger.warning(f"Could not switch to or search in a frame: {e}")
            finally:
                self.driver.switch_to.parent_frame()
                self._logger.debug("Switched back to parent frame.")
        
        return None

    def click(self, element: WebElement, use_action_chains: bool = False):
        try:
            if use_action_chains:
                self._logger.debug("Performing click with ActionChains.")
                self.action_chains.move_to_element(element).click().perform()
            else:
                element.click()
            self._logger.debug("Element clicked successfully.")
        except MoveTargetOutOfBoundsException as e:
            self._logger.warning(f"Element out of bounds, trying click with ActionChains. Details: {e}")
            self.action_chains.move_to_element(element).click().perform()
        except Exception as e:
            self._logger.error(f"Error clicking element: {e}")
            raise

    def send_keys(self, element: WebElement, *values: str, clear_first: bool = False):
        try:
            if clear_first:
                element.clear()
                self._logger.debug("Element cleared before sending keys.")
            element.send_keys(*values)
            self._logger.debug(f"Keys sent to element: {values}")
        except Exception as e:
            self._logger.error(f"Error sending keys to element: {e}")
            raise

    def get_text(self, element: WebElement) -> str:
        try:
            text = element.text
            self._logger.debug(f"Retrieved text from element: '{text}'")
            return text
        except Exception as e:
            self._logger.error(f"Error getting text from element: {e}")
            raise

    def get_attribute(self, element: WebElement, attribute_name: str) -> str:
        try:
            value = element.get_attribute(attribute_name)
            self._logger.debug(f"Retrieved attribute '{attribute_name}': '{value}'")
            return value
        except Exception as e:
            self._logger.error(f"Error getting attribute '{attribute_name}': {e}")
            raise

    def wait_for_visibility(
        self,
        selector_value: str,
        selector_type: str = "xpath",
        timeout: Optional[int] = None,
    ) -> WebElement:
        current_timeout = timeout if timeout is not None else self.default_timeout
        by_strategy = self._get_by_strategy(selector_type)
        try:
            wait = WebDriverWait(self.driver, current_timeout)
            element = wait.until(EC.visibility_of_element_located((by_strategy, selector_value)))
            self._logger.debug(f"Element '{selector_value}' is visible.")
            return element
        except TimeoutException:
            self._logger.error(f"Timeout: Element '{selector_value}' did not become visible in {current_timeout}s.")
            raise

    def wait_for_clickable(
        self,
        selector_value: str,
        selector_type: str = "xpath",
        timeout: Optional[int] = None,
    ) -> WebElement:
        current_timeout = timeout if timeout is not None else self.default_timeout
        by_strategy = self._get_by_strategy(selector_type)
        try:
            wait = WebDriverWait(self.driver, current_timeout)
            element = wait.until(EC.element_to_be_clickable((by_strategy, selector_value)))
            self._logger.debug(f"Element '{selector_value}' is clickable.")
            return element
        except TimeoutException:
            self._logger.error(f"Timeout: Element '{selector_value}' did not become clickable in {current_timeout}s.")
            raise

    def execute_script(self, script: str, *args: Any) -> Any:
        try:
            self._logger.debug(f"Executing JS script: {script[:100]}...")
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self._logger.error(f"Error executing JavaScript: {e}")
            raise

    def get(self, url: str):
        try:
            self.driver.get(url)
            self._logger.info(f"Navigated to URL: {url}")
        except Exception as e:
            self._logger.error(f"Error navigating to URL '{url}': {e}")
            raise

    @property
    def current_url(self) -> str:
        return self.driver.current_url

    def refresh(self):
        self.driver.refresh()
        self._logger.info("Page refreshed.")

    def switch_to_tab(self, tab_index: int):
        try:
            window_handles = self.driver.window_handles
            if 0 <= tab_index < len(window_handles):
                self.driver.switch_to.window(window_handles[tab_index])
                self._logger.info(f"Switched to tab index: {tab_index}")
            else:
                raise IndexError(f"Tab index {tab_index} is out of range.")
        except Exception as e:
            self._logger.error(f"Error switching to tab {tab_index}: {e}")
            raise

    def take_screenshot(self, file_path: str = "screenshot.png"):
        try:
            self.driver.save_screenshot(file_path)
            self._logger.info(f"Screenshot saved to: {file_path}")
        except Exception as e:
            self._logger.error(f"Error taking screenshot at '{file_path}': {e}")
            raise

from typing import Generator
from contextlib import contextmanager

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver


@contextmanager
def get_driver() -> Generator[WebDriver, None, None]:
    """
    Obtains a Selenium web driver instance that can be used to automate interactions with a Chrome web browser.
    The driver is properly closed when it is no longer needed.
    """
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/chromium"
    # prevent issues that may arise when running Chrome in a Docker container
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    
    driver: WebDriver = webdriver.Chrome(
        options=options,
        # desired_capabilities=DesiredCapabilities.CHROME,
    )
    try:
        yield driver
    finally:
        driver.quit()
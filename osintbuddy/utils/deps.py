import typing

import selenium.webdriver
import selenium.webdriver.chrome.options
import selenium.webdriver.remote.webdriver


class ChromeOptionsProtocol(typing.Protocol):
    """Protocol for ChromeOptions to provide precise typing for add_argument and binary_location."""

    binary_location: str

    def add_argument(self, argument: str) -> None:
        """
        Add a command-line argument to the ChromeOptions.

        Parameters
        ----------
        argument : str
            The argument to pass to Chrome (e.g., "--headless").
        """
        ...


def build_chrome_options(
    binary_location: str = "/usr/bin/chromium",
    headless: bool = True,
    no_sandbox: bool = True,
    disable_dev_shm: bool = True,
) -> ChromeOptionsProtocol:
    """
    Create and configure ChromeOptions for a headless Chrome driver.

    Parameters
    ----------
    binary_location : str, optional
        Path to the Chrome or Chromium binary (default '/usr/bin/chromium').
    headless : bool, optional
        Whether to run Chrome in headless mode (default True).
    no_sandbox : bool, optional
        Whether to add the '--no-sandbox' flag (default True).
    disable_dev_shm : bool, optional
        Whether to add the '--disable-dev-shm-usage' flag (default True).

    Returns
    -------
    ChromeOptionsProtocol
        Configured ChromeOptions instance implementing ChromeOptionsProtocol.

    Examples
    --------
    >>> opts = build_chrome_options(headless=False)
    >>> isinstance(opts, selenium.webdriver.chrome.options.Options)
    True
    """
    # Cast the real Options into our Protocol so add_argument is properly typed
    options: ChromeOptionsProtocol = typing.cast(
        "ChromeOptionsProtocol",
        selenium.webdriver.chrome.options.Options(),
    )
    options.binary_location = binary_location

    if headless:
        options.add_argument("--headless")
    if no_sandbox:
        options.add_argument("--no-sandbox")
    if disable_dev_shm:
        options.add_argument("--disable-dev-shm-usage")

    return options


def get_driver(
    chrome_options: ChromeOptionsProtocol = build_chrome_options(),
) -> None:
    """
    Initializes a Chrome WebDriver instance and ensures cleanup.

    Parameters
    ----------
    chrome_options : ChromeOptionsProtocol, optional
        Pre-configured ChromeOptions (default from build_chrome_options).

    Returns
    -------
    None

    Raises
    ------
    selenium.common.exceptions.WebDriverException
        If the driver fails to start.

    Examples
    --------
    >>> driver = get_driver()
    >>> driver.get("https://example.com")
    >>> title = driver.title
    >>> driver.quit()
    """
    driver: selenium.webdriver.remote.webdriver.WebDriver = (
        selenium.webdriver.Chrome(
            options=typing.cast(
                "selenium.webdriver.chrome.options.Options",
                chrome_options,
            )
        )
    )
    driver.get("https://example.com")
    driver.quit()

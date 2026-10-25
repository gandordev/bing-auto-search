# global imports ---------------------------------------------------
import logging
import random
import time

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchWindowException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# local imports ----------------------------------------------------
from .keywords import SEARCH_TERMS

log = logging.getLogger(__name__)

DELAY = 5
PAGE_LOAD_TIMEOUT = 15
ELEMENT_TIMEOUT = 8
MAX_RETRIES = 2
MAX_CONSECUTIVE_FAILURES = 5


# region Private methods
def _build_driver() -> webdriver.Edge:
    """
    Build and return a Selenium WebDriver instance for Microsoft Edge.

    Selenium Manager (bundled with Selenium >= 4.6) resolves the driver
    automatically, so no external driver manager is needed.

    Returns
    -------
    webdriver.Edge
        The Selenium WebDriver instance for Microsoft Edge.
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # Don't wait for the full page load, just DOMContentLoaded
    options.page_load_strategy = "eager"

    driver = webdriver.Edge(options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


def _search_with_retry(driver: webdriver.Edge, term: str, first: bool) -> bool:
    """
    Run one search, retrying on transient errors.

    Parameters
    ----------
    driver : webdriver.Edge
        The Selenium WebDriver instance for Microsoft Edge.
    term : str
        The search term to use.
    first : bool
        Whether this is the first search of the run (reuses the initial tab).

    Returns
    -------
    bool
        True if the search succeeded, False if all attempts failed.
    """
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            _search(driver, term, new_tab=not first or attempt > 1)
            return True
        except (TimeoutException, NoSuchWindowException) as e:
            log.warning(
                "Attempt %d failed for «%s»: %s", attempt, term, type(e).__name__
            )
            _recover_window(driver)
            time.sleep(random.uniform(0.5, 1.5))
        except WebDriverException as e:
            # Non-transient errors (browser crashed, etc.): let run() handle them
            if "invalid session" in str(e).lower() or "disconnected" in str(e).lower():
                raise
            log.warning("Error on «%s»: %s", term, e.msg or e)
            _recover_window(driver)
    return False


def _search(driver: webdriver.Edge, term: str, new_tab: bool) -> None:
    """
    Perform a search in Bing using the specified term.

    Parameters
    ----------
    driver : webdriver.Edge
        The Selenium WebDriver instance for Microsoft Edge.
    term : str
        The search term to use.
    new_tab : bool
        Whether to open a new tab before searching.

    Raises
    ------
    TimeoutException, WebDriverException
        If the search box or the results page can't be reached.
    """
    if new_tab:
        driver.switch_to.new_window("tab")

    try:
        driver.get("https://www.bing.com")
    except TimeoutException:
        # The search box may be usable even if the full load timed out
        driver.execute_script("window.stop();")

    search_box = WebDriverWait(driver, ELEMENT_TIMEOUT).until(
        EC.element_to_be_clickable((By.NAME, "q"))
    )

    for char in term:
        search_box.send_keys(char)
        time.sleep(random.uniform(0.01, 0.04))
    time.sleep(random.uniform(0.1, 0.2))
    search_box.send_keys(Keys.RETURN)

    # Confirm we actually navigated to the results page
    WebDriverWait(driver, ELEMENT_TIMEOUT).until(EC.url_contains("search?q="))


def _recover_window(driver: webdriver.Edge) -> None:
    """Make sure the driver points to a valid window after an error."""
    try:
        handles = driver.window_handles
        if handles:
            driver.switch_to.window(handles[-1])
        else:
            driver.switch_to.new_window("tab")
    except WebDriverException:
        pass


def _close_old_tabs(driver: webdriver.Edge, keep_last: int = 1) -> None:
    """
    Close old tabs, keeping the last `keep_last` tabs open.

    Parameters
    ----------
    driver : webdriver.Edge
        The Selenium WebDriver instance for Microsoft Edge.
    keep_last : int, optional
        The number of last tabs to keep open, by default 1
    """
    try:
        handles = driver.window_handles
        for handle in handles[:-keep_last]:
            driver.switch_to.window(handle)
            driver.close()
        driver.switch_to.window(driver.window_handles[-1])
    except NoSuchWindowException:
        _recover_window(driver)


# endregion


def run(total: int = 45) -> None:
    """
    Run the automated search session.

    Parameters
    ----------
    total : int, optional
        The number of searches to perform, by default 45. Capped at the
        number of available search terms so no term is repeated.
    """
    if not SEARCH_TERMS:
        log.error("SEARCH_TERMS is empty; nothing to search for.")
        return

    terms = random.sample(SEARCH_TERMS, k=min(total, len(SEARCH_TERMS)))
    total = len(terms)
    log.info("Starting automated search with %d searches...", total)

    driver = None
    done = failed = consecutive_failures = 0

    try:
        driver = _build_driver()

        for i, term in enumerate(terms, start=1):
            print(f"[{i:>2}/{total}] 🔍 Searching: «{term}»")

            if _search_with_retry(driver, term, first=(i == 1)):
                done += 1
                consecutive_failures = 0
            else:
                failed += 1
                consecutive_failures += 1
                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    log.error(
                        "%d consecutive failures; aborting.", consecutive_failures
                    )
                    break

            _close_old_tabs(driver, keep_last=1)
            time.sleep(DELAY)

        log.info("Finished: %d succeeded, %d failed.", done, failed)
    except KeyboardInterrupt:
        log.info("Program ended by user.")
    except WebDriverException as e:
        log.error("WebDriver error: %s", e.msg or e)
    finally:
        if driver is not None:
            try:
                driver.quit()
            except WebDriverException:
                pass  # the browser was already closed
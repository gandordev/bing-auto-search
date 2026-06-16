# global imports ---------------------------------------------------
import random
import time

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# local imports ----------------------------------------------------
from .keywords import SEARCH_TERMS

DELAY = 1


def run(total: int = 45):
    print(f"Starting automated search with {total} searches...")

    # Seleccionar términos aleatorios (con repetición si total > len(SEARCH_TERMS))
    terms = random.choices(SEARCH_TERMS, k=total)

    try:
        driver = _build_driver()

        for i, term in enumerate(terms, start=1):
            print(f"[{i:>2}/{total}] 🔍 Buscando: «{term}»")
            _search(driver, term, tab_index=i - 1)
            _close_old_tabs(driver, keep_last=1)

            time.sleep(DELAY)

        print("All searches completed successfully.")
        driver.quit()
    except KeyboardInterrupt:
        print("\nProgram ended by user.")
    except WebDriverException as e:
        print(f"Error initializing WebDriver: {e}")


# Private methods ---------------------------------------------------
def _build_driver() -> webdriver.Edge:
    """
    Build and return a Selenium WebDriver instance for Microsoft Edge.

    Returns
    -------
    webdriver.Edge
        The Selenium WebDriver instance for Microsoft Edge.
    """
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)

    # Ocultar webdriver flag
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


def _search(driver: webdriver.Edge, term: str, tab_index: int):
    """
    Perform a search in Bing using the specified term.

    Parameters
    ----------
    driver : webdriver.Edge
        The Selenium WebDriver instance for Microsoft Edge.
    term : str
        The search term to use.
    tab_index : int
        The index of the tab to use for the search.
    """
    # Abrir nueva pestaña (excepto la primera)
    if tab_index > 0:
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])

    driver.get("https://www.bing.com")
    time.sleep(random.uniform(1.5, 3.0))

    try:
        search_box = driver.find_element(By.NAME, "q")
        # Simula escritura humana carácter a carácter
        for char in term:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.04, 0.15))
        time.sleep(random.uniform(0.5, 1.2))
        search_box.send_keys(Keys.RETURN)
        time.sleep(random.uniform(2.0, 4.0))
    except Exception as e:
        print(f"Error during search for term '{term}': {e}")


def _close_old_tabs(driver: webdriver.Edge, keep_last: int = 5):
    """
    Close old tabs, keeping the last `keep_last` tabs open.

    Parameters
    ----------
    driver : webdriver.Edge
        The Selenium WebDriver instance for Microsoft Edge.
    keep_last : int, optional
        The number of last tabs to keep open, by default 5
    """
    handles = driver.window_handles
    if len(handles) > keep_last:
        for handle in handles[:-keep_last]:
            driver.switch_to.window(handle)
            driver.close()
        driver.switch_to.window(driver.window_handles[-1])

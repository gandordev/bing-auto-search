# Auto Search

Auto Search automates web searches in Microsoft Edge (Bing) using Selenium. It opens Edge in headless mode, performs a configurable number of searches using predefined search terms, and closes old tabs to keep the browser manageable. This can be useful for automated testing, demonstrations, or batch lookups.

## Features

- Automates searches in Microsoft Edge via Selenium WebDriver.
- Uses a built-in list of search terms (see `src/keywords.py`) and picks random terms on each run.
- Configurable number of searches via the command-line argument `-n/--num` (default: 45).
- Simulates human-like typing and random delays to mimic natural interaction.
- Resilient error handling:
  - Each search is retried on transient errors (timeouts, closed tabs).
  - A failed search does not abort the whole run.
  - The run stops early after several consecutive failures (e.g. no network, or Bing changed its page).
  - The browser is always closed on exit, even after errors or `Ctrl+C`.
- Progress and errors are reported through Python's `logging` module.

## Requirements

- Python 3.10+ (required by current Selenium releases; tested on Python 3.14)
- Microsoft Edge installed
- [`uv`](https://docs.astral.sh/uv/) (recommended for dependency management)
- Python packages:
  - `selenium` (4.6 or newer; the driver is managed automatically by Selenium Manager)

> `webdriver-manager` is **no longer needed**. Selenium Manager, bundled with Selenium, downloads the matching Edge driver on its own. If you still have it installed, you can remove it with `uv remove webdriver-manager` (or `pip uninstall webdriver-manager`).

## Installation

Install project dependencies and create a local `.venv`:

```bash
uv sync
```

## Usage

Run the application using the project's environment:

```bash
uv run main.py            # 45 searches (default)
uv run main.py -n 60      # 60 searches
```

For a quick sanity check after installing or updating Selenium, run a short batch first:

```bash
uv run main.py -n 3
```

Useful `uv` helpers:

- Create a virtual environment explicitly: `uv venv`
- Update Selenium: `uv lock --upgrade-package selenium && uv sync`
- Use the pip-compatible interface: `uv pip sync requirements.txt`

## Configuration

Search terms:

- Edit `src/keywords.py` and modify the `SEARCH_TERMS` list. It must not be empty.

Behavior constants at the top of `src/search.py`:

| Constant | Default | Purpose |
|---|---|---|
| `DELAY` | `0.15` | Pause (seconds) between searches |
| `PAGE_LOAD_TIMEOUT` | `15` | Max seconds to wait for a page load |
| `ELEMENT_TIMEOUT` | `8` | Max seconds to wait for the search box / results |
| `MAX_RETRIES` | `2` | Extra attempts per search term after a failure |
| `MAX_CONSECUTIVE_FAILURES` | `5` | Failed searches in a row before the run aborts |

Typing speed and per-step random sleeps can be adjusted inside the `_search` function.

Logging:

- Log output is configured in `main.py`. Use `logging.basicConfig(level=logging.INFO)` for normal output, or `logging.DEBUG` for more detail.

## How it works

1. `main.py` parses the `-n` argument and calls `run(total=...)` from `src/search.py`.
2. `src/search.py` builds a headless Edge WebDriver (driver resolved by Selenium Manager) and picks `total` random terms.
3. For each term, it opens a new tab, loads Bing, waits for the search box, types the term character by character, presses Enter, and confirms that the results page loaded.
4. If a search fails, it is retried; if it still fails, it is counted and the run continues. Too many consecutive failures abort the run.
5. Old tabs are closed after each search so only the latest one stays open.
6. The browser is closed in a `finally` block, so no orphaned Edge processes are left behind.

## Troubleshooting

- **WebDriver fails to initialize:** make sure Microsoft Edge is installed and up to date, and that Selenium is current (`uv lock --upgrade-package selenium`). Selenium Manager needs network access the first time it downloads the driver, so proxy or firewall restrictions can interfere.
- **Many searches fail or the run aborts with "consecutive failures":** Bing may be showing a consent banner, a verification page, or a changed layout. Temporarily remove `--headless=new` in `_build_driver()` to see what the browser actually displays.
- **Timeouts on slow connections:** increase `PAGE_LOAD_TIMEOUT` and `ELEMENT_TIMEOUT`.
- **`ImportError: attempted relative import`:** run the project through `main.py` (`uv run main.py`) rather than executing `src/search.py` directly.
- **Leftover Edge processes:** these should not occur anymore, since the driver is always closed on exit. If one is left after a hard kill, end it from the task manager.

## Safety & Notes

- This tool automates browser actions. Use it responsibly and respect the terms of service of the sites involved.
- Automated searches can be detected.

## Files of interest

- `main.py`: CLI entry point
- `src/search.py`: core automation logic
- `src/keywords.py`: list of search terms

## License

This project is provided as-is. Modify as needed for your use case.

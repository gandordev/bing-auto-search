# Auto Search

Auto Search automates web searches in Microsoft Edge (Bing) using Selenium. It opens Edge, performs a configurable number of searches using predefined search terms, and closes old tabs to keep the browser manageable. This can be useful for automated testing, demonstrations, or batch lookups.

**Features**
- Automates searches in Microsoft Edge via Selenium WebDriver.
- Uses a built-in list of search terms (see `src/keywords.py`) and selects random terms for each run.
- Configurable number of searches via the command-line argument `-n/--num` (default: 45).
- Simulates human-like typing and random delays to mimic natural interaction.

**Requirements**
- Python 3.8+
- Microsoft Edge browser installed
- The following Python packages:
	- `selenium`
	- `webdriver-manager`

- Install project dependencies and create a local `.venv`:

```bash
uv sync
```

- Run the application using the project's environment:

```bash
uv run main.py -n 60
```

- Useful `uv` helpers:

- Create a virtual environment explicitly: `uv venv`
- Install tools as standalone: `uv tool install <tool>`
- Use the pip-compatible interface: `uv pip sync requirements.txt`

**Configuration**
- To change or extend the search terms, edit `src/keywords.py` and modify the `SEARCH_TERMS` list.
- To adjust timing behavior, edit the `DELAY` constant in `src/search.py` or modify the random sleep ranges inside the `_search` function.

**How it works (brief)**
- `main.py` parses the `-n` argument and calls `run(total=...)` from `src/search.py`.
- `src/search.py` builds an Edge WebDriver (via `webdriver_manager`), opens Bing, simulates typing each search term, and navigates results.
- Old tabs are closed periodically to keep the browser focused on the most recent searches.

**Troubleshooting**
- If WebDriver fails to initialize, ensure Microsoft Edge is installed and up-to-date.
- Check that `webdriver-manager` can download the appropriate Edge driver (network/proxy restrictions can interfere).
- If Selenium raises exceptions during interaction, try increasing delays to improve stability.

**Safety & Notes**
- This tool automates browser actions. Use it responsibly and respect terms of service for external sites.

**Files of interest**
- `main.py` — CLI entry point
- `src/search.py` — core automation logic
- `src/keywords.py` — list of search terms

**License**
This project is provided as-is. Modify as needed for your use case.


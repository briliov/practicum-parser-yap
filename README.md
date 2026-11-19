# Practicum Parser YAP

Practicum Parser YAP is a command-line Python web scraper for parsing `docs.python.org`, featuring HTTP response caching, rotating file logging, and multiple output formats.

## TECH STACK

![Python](https://img.shields.io/badge/python-black?style=for-the-badge&logo=python&logoColor=ffdd54)
![Requests-Cache](https://img.shields.io/badge/Requests_Cache-black?style=for-the-badge&logoColor=#005FAD)
![PrettyTable](https://img.shields.io/badge/PrettyTable-black?style=for-the-badge&logoColor=#005FAD)
![BeautifulSoup4](https://img.shields.io/badge/requests-black?style=for-the-badge&logoColor=#005FAD)
![LXML](https://img.shields.io/badge/xml-black?style=for-the-badge&logo=xml&logoColor=#005FAD)
![SQLite](https://img.shields.io/badge/SQLite-black?style=for-the-badge&logo=sqlite&logoColor=blue)
![Git](https://img.shields.io/badge/git-black.svg?style=for-the-badge&logo=git&logoColor=orange)

## Project Structure

- `configs.py` — configures `argparse` CLI arguments (`mode`, `-c/--clear-cache`, `-o/--output`) and sets up rotating file and console logging in `logs/`.
- `constants.py` — defines the base documentation URL (`docs.python.org/3/`), project root directory path, and datetime formatting string.
- `exceptions.py` — defines the custom `ParserFindTagException` raised when expected HTML tags are missing.
- `main.py` — entry point implementing the core scraping modes (`whats-new`, `latest-versions`, `download`) with `CachedSession` management.
- `outputs.py` — handles data presentation in standard terminal output, formatted ASCII tables via `PrettyTable`, or timestamped CSV files in `results/`.
- `utils.py` — provides helper wrappers for HTTP requests (`get_response`) and safe HTML tag lookups (`find_tag`) with error logging.

## How to Run the Project

Clone the repository and navigate into it

```bash
git clone https://github.com
```

```bash
cd practicum-parser-yap
```

Create and activate a virtual environment

```bash
python3 -m venv .venv
```

Linux | Mac

```bash
source .venv/bin/activate
```

Windows

```bash
source .venv/scripts/activate
```

Install dependencies from requirements.txt

```bash
python3 -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

Run the parser with the required mode and optional flags

```bash
python3 main.py whats-new -o pretty
```

```bash
python3 main.py latest-versions -o file -c
```

```bash
python3 main.py download
```

---

#### ✦ Author: **[Egor Briliov](https://github.com)**
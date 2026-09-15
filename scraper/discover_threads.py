# This script scrapes thread links from 10 pages across each major Nairaland categories and saves them to a CSV file.

import time
import random
from typing import TypedDict
from pathlib import Path

import requests
import pandas as pd 
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


urls = {
    "politics": "https://www.nairaland.com/politics",
    "education": "https://www.nairaland.com/education",
    "sports": "https://www.nairaland.com/sports",
    "jokes": "https://www.nairaland.com/jokes",
    "romance": "https://www.nairaland.com/romance",
    "tech": "https://www.nairaland.com/techmarket"
}

ua = UserAgent()
headers = {"User-Agent": ua.random}
page_numbers = range(10)


# Data directory setup
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw_data"


class Thread(TypedDict):
    title: str
    link: str
    category: str


def get_category_page_url(category_url: str, page_number: int) -> str:
    """Build a Nairaland category URL for a zero-based page number."""
    if page_number == 0:
        return category_url
    else:
        return f"{category_url}/{page_number}"


def fetch_page_html(url: str) -> str | None:
    """Fetch a category or thread page and return its HTML."""
    try:
        time.sleep(random.uniform(1, 3))
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        print(f"Successfully accessed {url}")
        return response.text
    except requests.RequestException as error:
        print(f"Could not fetch {url}: {error}")
        return None


def parse_html(page_html: str | None) -> BeautifulSoup | None:
    """Parse page HTML into a BeautifulSoup object."""
    if page_html is None:
        return None
    return BeautifulSoup(page_html, "html.parser")


def get_threads(soup: BeautifulSoup | None) -> list[dict[str, str]]:
    """Extract thread data from a category page soup."""
    if soup is None:
        return []

    tables = soup.find_all("table")
    if not tables:
        return []

    thread_link_table = tables[1] if len(tables) > 1 else tables[0]

    thread_data = []
    for thread in thread_link_table.find_all("tr")[1:]:
        td = thread.find("td")
        if not td:
            continue

        a_tag = td.find("b").find("a")

        if not a_tag:
            continue

        link = a_tag["href"]
        title = a_tag.text.strip()

        thread_data.append({
            "title": title,
            "link": f"https://www.nairaland.com{link}"
            })

    return thread_data


def get_page_thread_data(category_url: str) -> list[dict[str, str]]:
    """Collect unique thread data from the first ten pages of a category."""
    thread_data = []

    for page_number in page_numbers:
        page_url = get_category_page_url(category_url, page_number)
        soup = parse_html(fetch_page_html(page_url))
        thread_data.extend(get_threads(soup))
        time.sleep(random.uniform(1, 3))

    return thread_data


def get_category_thread_data() -> list[Thread]:
    """Collect thread data from all specified categories."""
    all_thread_data = []
    for category, url in urls.items():
        thread_data = get_page_thread_data(category_url=url)
        for thread in thread_data:
            thread["category"] = category

        all_thread_data.extend(thread_data)

    return all_thread_data


def deduplicate_threads(data: list[Thread]) -> list[Thread]:
    """Deduplicate threads based on their links."""

    seen=set()
    results=[]

    for item in data:
        if item["link"] not in seen:
            seen.add(item["link"])
            results.append(item)

    return results


def save_data(data: list[Thread]) -> Path:
    """Save collected thread data in the configured external data folder."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_DIR / "thread_links.csv"

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    return output_path


def main():
    """Main function to execute the scraping process."""
    data = get_category_thread_data()
    data = deduplicate_threads(data)
    print(f"No of threads links scraped: {len(data)}")
    output_path = save_data(data)
    print(f"Thread data has been saved to '{output_path}'.")


if __name__ == "__main__":
    main()

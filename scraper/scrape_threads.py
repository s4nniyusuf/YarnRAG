# This script scrapes thread data from a forum, extracting the main content and comments from each thread. It saves the collected data in a JSONL file for further analysis.

import random
import time
import json
from pathlib import Path

import requests
import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


# ua = UserAgent()
# headers = {"User-Agent": ua.random}

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "DNT": "1",
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw_data"


def load_data():
    """"Load thread links from the CSV file into a list of dictionaries."""
    df = pd.read_csv(DATA_DIR / "thread_links.csv")
    return df.to_dict(orient="records")


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


def get_thread_data(soup: BeautifulSoup | None) -> tuple[str, list[dict[str, str|int]]] | None:
    """Extract thread comments from the parsed HTML."""

    if soup is None:
        return None

    thread_table = soup.find("table", {"summary": "posts"})

    if thread_table is None:
        return None

    # Thread post content extraction
    content = thread_table.find("tbody").find_all("tr")[1].find("td").find("div", {"class": "narrow"}).text.strip()
    print(content)

    # Thread comments extraction
    x = 0
    comments = []

    for tbody in thread_table.find_all("tbody")[1:]: # the first one is the main post
        tr = tbody.find_all("tr")

        if len(tr) < 2: # comments are usually in the second <tr> of each <tbody>
            continue
        else:
            x+=1
            comment= tr[1].find("td").find("div", {"class": "narrow"}).text.strip()
            
            comments.append(comment)

    return content, comments


def format_data(content: str, comments: list[dict[str, str|int]], category: str, title: str, link: str) -> list[dict[str, str|list[dict[str, str|int]]]]:
    """Format the extracted thread data into a structured dictionary."""
    return{
        "category": category,
        "title": title,
        "link": link,
        "content": content,
        "comments": comments
    }


def save_data(data: dict[str, str | list[dict[str, str|int]]]) -> None:
    """Save one thread to a JSONL file."""
    OUTPUT_PATH = DATA_DIR / "thread_data.jsonl"
    with open(OUTPUT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

 
def main():
    """Main function to load data, fetch pages, and parse HTML."""
    data = load_data()

    for item in data:
        # Fetch the HTML of the thread page
        page_html = fetch_page_html(url=item["link"])

        # Parse the HTML into a BeautifulSoup object
        soup = parse_html(page_html=page_html)

        # Extract thread content and comments
        thread_data = get_thread_data(soup=soup)
        if thread_data is None:
            print(f"Failed to extract data for thread: {item['title']}")
            continue

        content, comments = thread_data

        # Format the extracted data into a structured format
        formated_data = format_data(
            content=content, 
            comments=comments, 
            category=item["category"], 
            title=item["title"], 
            link=item["link"]
        )

        # Save the formatted data to a JSONL file
        save_data(data=formated_data)


if __name__ == "__main__":
    main()

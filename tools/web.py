import subprocess
import webbrowser
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0 Safari/537.36"
    )
}


def normalize_url(url: str) -> str:
    url = url.strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


def open_website(url: str) -> str:
    try:
        url = normalize_url(url)
        webbrowser.open(url)
        return f"Opened {url}."
    except Exception as e:
        return f"Couldn't open website: {e}"


def open_url_in_safari(url: str) -> str:
    try:
        url = normalize_url(url)

        subprocess.Popen([
            "open",
            "-a",
            "Safari",
            url
        ])

        return f"Opened {url} in Safari."

    except Exception as e:
        return f"Couldn't open Safari: {e}"


def search_web(query: str) -> str:
    try:
        url = (
            "https://www.google.com/search?q="
            + quote(query)
        )

        webbrowser.open(url)

        return f"Searching for {query}."

    except Exception as e:
        return f"Couldn't search the web: {e}"


def fetch_webpage(url: str) -> str:
    """
    Download a webpage and extract readable text.
    """

    try:
        url = normalize_url(url)

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for element in soup([
            "script",
            "style",
            "noscript",
            "nav",
            "footer",
            "header",
            "aside"
        ]):
            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        text = " ".join(text.split())

        if not text:
            return "No readable text found on the webpage."

        return text[:16000]

    except Exception as e:
        return f"Couldn't read webpage: {e}"


def search_news(query: str, limit: int = 5) -> list:
    """
    Search Google News RSS and return structured results.
    """

    rss_url = (
        "https://news.google.com/rss/search?q="
        + quote(query)
        + "&hl=en-GB&gl=GB&ceid=GB:en"
    )

    response = requests.get(
        rss_url,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.content,
        "xml"
    )

    items = soup.find_all("item")

    results = []

    for item in items[:limit]:

        title = (
            item.title.get_text(
                " ",
                strip=True
            )
            if item.title
            else ""
        )

        link = (
            item.link.get_text(
                " ",
                strip=True
            )
            if item.link
            else ""
        )

        description = ""

        if item.description:

            description = BeautifulSoup(
                item.description.get_text(),
                "html.parser"
            ).get_text(
                " ",
                strip=True
            )

        results.append({
            "title": title,
            "url": link,
            "summary": description
        })

    return results


def research_web(query: str) -> str:
    """
    Perform multi-source web research.

    Returns structured research that can be given
    to the local JARVIS reasoning model.
    """

    try:

        print(f"🌐 Researching: {query}")

        results = search_news(
            query,
            limit=6
        )

        if not results:
            return (
                "No current search results were found. "
                "Do not invent research."
            )

        output = [
            f"WEB RESEARCH FOR: {query}",
            "",
            f"Found {len(results)} relevant sources.",
            ""
        ]

        for i, result in enumerate(results, 1):

            output.append(
                f"SOURCE {i}"
            )

            output.append(
                f"TITLE: {result['title']}"
            )

            output.append(
                f"URL: {result['url']}"
            )

            output.append(
                f"SUMMARY: {result['summary']}"
            )

            output.append(
                "-" * 60
            )

        return "\n".join(output)[:18000]

    except Exception as e:

        return f"Web research failed: {e}"


from pathlib import Path
from io import StringIO

import pandas as pd
import requests
from bs4 import BeautifulSoup




STANDINGS_URL = (
    "https://www.bbc.co.uk/sport/football/"
    "premier-league/table"
)

TOP_SCORERS_URL = (
    "https://www.bbc.co.uk/sport/football/"
    "premier-league/top-scorers"
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    )
}



def get_html_tables(url):
    """Download a webpage and parse its HTML tables
    using BeautifulSoup and Pandas.
    """
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    html_tables = soup.find_all("table")

    if not html_tables:
        raise ValueError(
            f"No HTML tables found at {url}. "
            "The page may load data dynamically."
        )

    tables = []

    for html_table in html_tables:
        try:
            parsed = pd.read_html(
                StringIO(str(html_table))
            )
            tables.extend(parsed)
        except ValueError:
            continue

    if not tables:
        raise ValueError(
            f"Could not parse any HTML tables from {url}"
        )

    return tables


def find_table(tables, keywords, page_name):
    """Find a table containing all required column keywords."""
    for table in tables:
        columns = " ".join(
            str(column).lower()
            for column in table.columns
        )

        if all(keyword.lower() in columns
               for keyword in keywords):
            print(f"{page_name}: matching table found")
            print("Columns:", list(table.columns))
            return table.copy()

    print(f"\nCould not identify {page_name}.")

    for index, table in enumerate(tables):
        print(
            f"Table {index}: {list(table.columns)}"
        )

    raise ValueError(
        f"Could not find the expected {page_name} columns."
    )



def scrape_standings():
    """Scrape and save the Premier League table."""
    tables = get_html_tables(STANDINGS_URL)

    standings = find_table(
        tables,
        keywords=["team", "played", "points"],
        page_name="Standings"
    )

    standings["Team"] = standings["Team"].astype(str).str.replace(
        r"^\s*\d+\s*",
        "",
        regex=True
    )

    output_path = DATA_DIR / "league_table.csv"

    standings.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nStandings saved to: {output_path}")
    print(standings.head())

    return standings



def scrape_top_scorers():
    """Scrape and save the Premier League top scorers."""
    tables = get_html_tables(TOP_SCORERS_URL)

    # BBC uses Name rather than Player.
    scorers = find_table(
        tables,
        keywords=["name", "goals"],
        page_name="Top scorers"
    )

    rename_columns = {}

    for column in scorers.columns:
        name = str(column).strip().lower()

        if name == "name":
            rename_columns[column] = "Player"
        elif name == "goals":
            rename_columns[column] = "Goals"
        elif name == "assists":
            rename_columns[column] = "Assists"
        elif name == "played":
            rename_columns[column] = "Played"

    scorers = scorers.rename(columns=rename_columns)

    required = ["Player", "Goals"]

    for column in required:
        if column not in scorers.columns:
            raise ValueError(
                f"Required column {column!r} is missing."
            )


    for column in ["Goals", "Assists", "Played"]:
        if column in scorers.columns:
            scorers[column] = pd.to_numeric(
                scorers[column],
                errors="coerce"
            )

    scorers = scorers.dropna(
        subset=["Player", "Goals"]
    )

    scorers = scorers.sort_values(
        "Goals",
        ascending=False
    )


    useful_columns = [
        column for column in
        ["Player", "Goals", "Assists", "Played"]
        if column in scorers.columns
    ]

    scorers = scorers[useful_columns]

    output_path = DATA_DIR / "top_scorers.csv"

    scorers.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nTop scorers saved to: {output_path}")
    print(scorers.head(10))

    return scorers



if __name__ == "__main__":
    try:
        scrape_standings()
    except (
        requests.RequestException,
        ValueError
    ) as error:
        print(f"Standings scraping failed: {error}")

    try:
        scrape_top_scorers()
    except (
        requests.RequestException,
        ValueError
    ) as error:
        print(f"Top-scorers scraping failed: {error}")

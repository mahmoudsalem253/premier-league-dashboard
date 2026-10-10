
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")


def clean_standings():
    path = DATA_DIR / "league_table.csv"
    df = pd.read_csv(path)

   
    df["Team"] = df["Team"].str.replace(
        r"^\s*\d+\s*", "", regex=True
    )

    numeric_columns = [
        "Played",
        "Won",
        "Drawn",
        "Lost",
        "Goals For",
        "Goals Against",
        "Goal Difference",
        "Points",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    df = df.drop_duplicates(subset=["Team"])

    df = df.sort_values(
        ["Points", "Goal Difference", "Goals For"],
        ascending=[False, False, False]
    ).reset_index(drop=True)

    df.insert(0, "Position", range(1, len(df) + 1))

    return df


def clean_scorers():
    path = DATA_DIR / "top_scorers.csv"
    df = pd.read_csv(path)

    df["Goals"] = pd.to_numeric(
        df["Goals"], errors="coerce"
    )

    df = df.dropna(subset=["Player", "Goals"])
    df = df.sort_values("Goals", ascending=False)

    return df.reset_index(drop=True)


if __name__ == "__main__":
    standings = clean_standings()
    scorers = clean_scorers()

    print("\nClean league table:")
    print(standings.head())

    print("\nTop scorers:")
    print(scorers.head(10))

"""Parse the hunt events CSV from the hunt website to see who won by various metrics

ADV = team advanced to that level
REQ = team requested a hint

Edit the values of the constants at the top of this file for your purposes, e.g.
START_TIME, TEAM_NAMES, etc.
"""
import csv
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Start time
START_TIME = datetime.strptime("2000-01-01 00:00:00+0000", "%Y-%m-%d %H:%M:%S%z")
# 2.0 hours per hint
# N.B. assumes all hints _requested_ take a penalty,
# script will need editing if you want to only account for hints _used_
PENALTY_PER_HINT_IN_HOURS = 2.0
# "Final" level, the advance to which encodes that the team finished
FINAL_LEVEL = "51"
# List of team names as strings
TEAM_NAMES: list["TeamName"] = []
# Path to hunt event csv taken from the website
CSV_FILE_PATH = r"C:\Users\username\Downloads\hunt.huntevent.csv"

TeamName = str


def parse_timestamp(timestamp: str) -> datetime:
    return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").replace(
        tzinfo=timezone.utc
    )


def main(csv_file: str) -> None:
    teams = TEAM_NAMES
    team_raw_times: dict[TeamName, float] = defaultdict(float)
    team_running_totals: dict[TeamName, float] = defaultdict(float)
    team_hints_requested: dict[TeamName, int] = defaultdict(int)
    team_levels: dict[TeamName, int] = defaultdict(int)

    with Path(csv_file).open(encoding="utf-8") as f:
        csv_reader = csv.DictReader(f)

        for line in csv_reader:
            team = line["user"]
            assert team in teams
            # penalty of x hours per hint
            if line["type"] == "REQ":
                team_running_totals[team] += PENALTY_PER_HINT_IN_HOURS
                team_hints_requested[team] += 1
            elif line["type"] == "ADV":
                team_levels[team] += 1
                # Final level
                if line["level"] == FINAL_LEVEL:
                    timestamp = line["time"].split(".")[0]
                    finish_time = parse_timestamp(timestamp)
                    time_taken = (finish_time - START_TIME).total_seconds() / 60 / 60
                    print(time_taken)
                    team_running_totals[team] += time_taken
                    team_raw_times[team] = time_taken

    print("Raw times", team_raw_times)
    print("Running totals", team_running_totals)
    print("Hints requested", team_hints_requested)
    print("Team levels completed", team_levels)


if __name__ == "__main__":
    main(CSV_FILE_PATH)

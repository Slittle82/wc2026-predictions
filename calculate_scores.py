#!/usr/bin/env python3
"""
World Cup 2026 Prediction Contest - Score Calculator
Durham Football Lodge

Reads predictions from the published Google Sheets CSV (or a local CSV fallback),
reads actual match results from results.json, and writes two files:

  - leaderboard-data.json : ranked standings for the leaderboard
  - predictions.json      : everyone's picks, for the "My Picks" viewer

SCORING (per the contest rules):
  - 1 pt  for each correctly predicted individual score (home / away)
  - 3 pts for the correct result (win / draw / loss)
  - 1 pt  bonus when BOTH scores are exactly correct (perfect prediction = 6 pts)
  Maximum 6 pts per match.

  Tournament winner pick:
  - 12 pts if the predicted winner actually wins the tournament
  -  5 pts if the predicted winner finishes as runner-up

Tie-breakers: (1) most perfect (6pt) predictions, (2) most correct results (3pt).

USAGE
  python3 calculate_scores.py                  # fetch live CSV from Google Sheets
  python3 calculate_scores.py --csv-file x.csv # use a local CSV instead
  python3 calculate_scores.py --md-file x.md   # parse a pipe-delimited markdown table
"""

import argparse
import csv
import json
import os
import ssl
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from urllib.request import Request, urlopen

# Published Google Sheets CSV (Leaderboard tab)
PREDICTIONS_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vSMUj24sQdxvVfZz_wwk22sPr8q2"
    "wow2insdtVTa8e7p4tgOvsEp6diYMN1-22TsXFzoLyqM47SZE9H/pub?gid=1733040974&single=true&output=csv"
)

RESULTS_FILE = "results.json"
LEADERBOARD_OUT = "leaderboard-data.json"
PREDICTIONS_OUT = "predictions.json"
TOTAL_MATCHES = 72


# --------------------------------------------------------------------------- #
# Scoring helpers
# --------------------------------------------------------------------------- #
def parse_score(score_str: str) -> Optional[Tuple[int, int]]:
    """Parse 'home-away' (e.g. '2-1') into (home, away). Returns None if invalid."""
    if not score_str or "-" not in score_str:
        return None
    try:
        home, away = score_str.strip().split("-", 1)
        return (int(home), int(away))
    except (ValueError, IndexError):
        return None


def result_of(home: int, away: int) -> int:
    """1 = home win, 0 = draw, -1 = away win."""
    return (home > away) - (home < away)


def calculate_match_points(prediction: str, actual: str) -> int:
    """Points for a single match. See scoring rules in the module docstring."""
    pred = parse_score(prediction)
    act = parse_score(actual)
    if not pred or not act:
        return 0

    points = 0
    if pred[0] == act[0]:
        points += 1                       # correct home score
    if pred[1] == act[1]:
        points += 1                       # correct away score
    if result_of(*pred) == result_of(*act):
        points += 3                       # correct result
    if pred == act:
        points += 1                       # perfect-prediction bonus -> total 6
    return points


# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #
def fetch_rows_from_url(url: str) -> List[dict]:
    """Fetch and parse the published CSV into a list of row dicts."""
    try:
        context = ssl._create_unverified_context()
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; WC2026Scorer/1.0)",
            "Accept": "text/csv,text/plain,*/*",
        })
        data = urlopen(req, context=context).read().decode("utf-8").splitlines()
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR fetching CSV: {exc}")
        print(f"Attempted URL: {url}")
        print("Make sure the sheet is published to the web as CSV (File -> Share -> Publish to web).")
        sys.exit(1)
    return list(csv.DictReader(data))


def fetch_rows_from_csv_file(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fetch_rows_from_md_file(path: str) -> List[dict]:
    """Parse a pipe-delimited markdown table (skips any |:-:| separator rows)."""
    rows = []
    with open(path, encoding="utf-8") as fh:
        lines = [ln.rstrip("\n") for ln in fh if ln.strip().startswith("|")]
    cells = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
    cells = [c for c in cells if not all(set(x) <= set(":- ") for x in c)]
    if not cells:
        return rows
    header = cells[0]
    for row in cells[1:]:
        rows.append({header[i]: (row[i] if i < len(row) else "") for i in range(len(header))})
    return rows


def load_results() -> dict:
    """Load actual results / winner from results.json (returns sensible defaults)."""
    if not os.path.exists(RESULTS_FILE):
        return {"results": {}, "winner": None, "runner_up": None}
    with open(RESULTS_FILE, encoding="utf-8") as fh:
        data = json.load(fh)
    return {
        "results": {k.upper(): v for k, v in (data.get("results") or {}).items() if v},
        "winner": data.get("winner"),
        "runner_up": data.get("runner_up"),
    }


# --------------------------------------------------------------------------- #
# Column detection
# --------------------------------------------------------------------------- #
def find_columns(columns: List[str]) -> Tuple[Dict[str, str], Optional[str], Optional[str], Optional[str], Optional[str]]:
    """Locate match columns (A1..L6), name, payment and winner columns."""
    match_cols: Dict[str, str] = {}
    name_col = winner_col = payment_col = email_col = None
    for col in columns:
        c = col.strip()
        low = c.lower()
        if len(c) >= 3 and c[0].isalpha() and c[1].isdigit() and c[2] == ":":
            match_cols[c.split(":")[0].strip().upper()] = col
        elif "winner" in low:
            winner_col = col
        elif low == "name":
            name_col = col
        elif "email" in low:
            email_col = col
        elif any(k in low for k in ("confirm", "entry", "transfer", "monet", "payment")):
            payment_col = col
    return match_cols, name_col, winner_col, payment_col, email_col


def split_fixture(column_header: str) -> Tuple[str, str]:
    """'A1: Mexico vs South Africa' -> ('Mexico', 'South Africa')."""
    try:
        teams = column_header.split(":", 1)[1]
        home, away = teams.split(" vs ", 1)
        return home.strip(), away.strip()
    except (IndexError, ValueError):
        return "", ""


# --------------------------------------------------------------------------- #
# Build outputs
# --------------------------------------------------------------------------- #
def build(rows: List[dict], results: dict) -> Tuple[dict, dict]:
    actual = results["results"]
    winner = results["winner"]
    runner_up = results["runner_up"]

    columns = list(rows[0].keys()) if rows else []
    match_cols, name_col, winner_col, payment_col, email_col = find_columns(columns)

    # Stable match metadata, ordered A1..L6
    ordered_ids = sorted(match_cols.keys(), key=lambda m: (m[0], int(m[1:])))
    matches_meta = []
    for mid in ordered_ids:
        home, away = split_fixture(match_cols[mid])
        matches_meta.append({
            "id": mid,
            "group": mid[0],
            "home": home,
            "away": away,
            "result": actual.get(mid),
        })

    leaderboard, entrants = [], []
    for row in rows:
        name = (row.get(name_col, "") if name_col else "").strip()
        if not name:
            continue
        payment = (row.get(payment_col, "") if payment_col else "").strip()
        winner_pick = (row.get(winner_col, "") if winner_col else "").strip()

        match_points = perfect = correct_results = 0
        picks = {}
        for mid in ordered_ids:
            pick = (row.get(match_cols[mid], "") or "").strip()
            picks[mid] = pick
            pts = calculate_match_points(pick, actual.get(mid, ""))
            match_points += pts
            if pts == 6:
                perfect += 1
            elif pts == 3:
                correct_results += 1

        winner_points = 0
        if winner_pick and winner:
            if winner_pick.lower() == winner.lower():
                winner_points = 12
            elif runner_up and winner_pick.lower() == runner_up.lower():
                winner_points = 5

        total = match_points + winner_points
        paid = bool(payment) and payment.lower() not in ("no", "false")

        # NOTE: email is intentionally NOT included in the published output
        # (leaderboard-data.json is public on GitHub Pages).
        leaderboard.append({
            "name": name,
            "paid": paid,
            "total_points": total,
            "match_points": match_points,
            "winner_points": winner_points,
            "winner_pick": winner_pick,
            "games_6pt": perfect,
            "games_3pt": correct_results,
        })
        entrants.append({"name": name, "winner_pick": winner_pick, "picks": picks})

    leaderboard.sort(key=lambda e: (e["total_points"], e["games_6pt"], e["games_3pt"]), reverse=True)
    for i, entry in enumerate(leaderboard, 1):
        entry["rank"] = i

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    leaderboard_data = {
        "last_updated": now,
        "total_entries": len(leaderboard),
        "matches_completed": len(actual),
        "total_matches": TOTAL_MATCHES,
        "winner": winner,
        "runner_up": runner_up,
        "leaderboard": leaderboard,
    }
    predictions_data = {
        "last_updated": now,
        "winner_actual": winner,
        "matches": matches_meta,
        "entrants": sorted(entrants, key=lambda e: e["name"].lower()),
    }
    return leaderboard_data, predictions_data


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(description="WC2026 score calculator")
    ap.add_argument("--csv-file", help="Use a local CSV instead of the live sheet")
    ap.add_argument("--md-file", help="Parse a local pipe-delimited markdown table")
    args = ap.parse_args()

    print("=" * 60)
    print("World Cup 2026 Prediction Contest - Score Calculator")
    print("=" * 60)

    if args.md_file:
        rows = fetch_rows_from_md_file(args.md_file)
        print(f"Loaded {len(rows)} rows from markdown: {args.md_file}")
    elif args.csv_file:
        rows = fetch_rows_from_csv_file(args.csv_file)
        print(f"Loaded {len(rows)} rows from CSV: {args.csv_file}")
    else:
        rows = fetch_rows_from_url(PREDICTIONS_CSV_URL)
        print(f"Fetched {len(rows)} rows from Google Sheets")

    if not rows:
        print("No data found.")
        sys.exit(1)

    results = load_results()
    leaderboard_data, predictions_data = build(rows, results)

    with open(LEADERBOARD_OUT, "w", encoding="utf-8") as fh:
        json.dump(leaderboard_data, fh, indent=2, ensure_ascii=False)
    with open(PREDICTIONS_OUT, "w", encoding="utf-8") as fh:
        json.dump(predictions_data, fh, indent=2, ensure_ascii=False)

    lb = leaderboard_data["leaderboard"]
    print(f"\n[OK] {LEADERBOARD_OUT} + {PREDICTIONS_OUT} written")
    print(f"[OK] Entries: {len(lb)}  |  Matches scored: {leaderboard_data['matches_completed']}/{TOTAL_MATCHES}")
    if leaderboard_data["winner"]:
        print(f"[OK] Tournament winner set to: {leaderboard_data['winner']}")
    print("\n" + "=" * 60)
    print("TOP 10")
    print("=" * 60)
    for e in lb[:10]:
        print(f"{e['rank']:2d}. {e['name']:24s} {e['total_points']:3d} pts "
              f"(match {e['match_points']}, winner {e['winner_points']} | "
              f"6pt x{e['games_6pt']}, 3pt x{e['games_3pt']})")
    print("=" * 60)


if __name__ == "__main__":
    main()

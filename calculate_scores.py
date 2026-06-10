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
RANK_HISTORY_OUT = "rank-history.json"
RANK_HISTORY_MAX = 60
TOTAL_MATCHES = 72

# Kick-off times (all BST / +01:00, 2026). Used for the countdown, latest-results
# ordering and matchday grouping on the website.
KICKOFFS = {
    "A1": "2026-06-11T20:00:00+01:00", "A2": "2026-06-12T03:00:00+01:00",
    "A3": "2026-06-18T17:00:00+01:00", "A4": "2026-06-19T03:00:00+01:00",
    "A5": "2026-06-25T03:00:00+01:00", "A6": "2026-06-25T03:00:00+01:00",
    "B1": "2026-06-12T20:00:00+01:00", "B2": "2026-06-13T02:00:00+01:00",
    "B3": "2026-06-18T23:00:00+01:00", "B4": "2026-06-19T02:00:00+01:00",
    "B5": "2026-06-24T20:00:00+01:00", "B6": "2026-06-24T20:00:00+01:00",
    "C1": "2026-06-13T23:00:00+01:00", "C2": "2026-06-14T02:00:00+01:00",
    "C3": "2026-06-19T23:00:00+01:00", "C4": "2026-06-20T01:30:00+01:00",
    "C5": "2026-06-24T23:00:00+01:00", "C6": "2026-06-24T23:00:00+01:00",
    "D1": "2026-06-13T20:00:00+01:00", "D2": "2026-06-14T05:00:00+01:00",
    "D3": "2026-06-19T20:00:00+01:00", "D4": "2026-06-20T03:00:00+01:00",
    "D5": "2026-06-25T23:00:00+01:00", "D6": "2026-06-25T23:00:00+01:00",
    "E1": "2026-06-14T20:00:00+01:00", "E2": "2026-06-15T00:00:00+01:00",
    "E3": "2026-06-20T21:00:00+01:00", "E4": "2026-06-21T01:00:00+01:00",
    "E5": "2026-06-25T20:00:00+01:00", "E6": "2026-06-25T20:00:00+01:00",
    "F1": "2026-06-14T23:00:00+01:00", "F2": "2026-06-15T02:00:00+01:00",
    "F3": "2026-06-20T18:00:00+01:00", "F4": "2026-06-21T00:00:00+01:00",
    "F5": "2026-06-26T00:00:00+01:00", "F6": "2026-06-26T00:00:00+01:00",
    "G1": "2026-06-15T20:00:00+01:00", "G2": "2026-06-16T02:00:00+01:00",
    "G3": "2026-06-20T20:00:00+01:00", "G4": "2026-06-21T02:00:00+01:00",
    "G5": "2026-06-26T23:00:00+01:00", "G6": "2026-06-26T23:00:00+01:00",
    "H1": "2026-06-15T17:00:00+01:00", "H2": "2026-06-15T23:00:00+01:00",
    "H3": "2026-06-21T17:00:00+01:00", "H4": "2026-06-21T23:00:00+01:00",
    "H5": "2026-06-26T20:00:00+01:00", "H6": "2026-06-26T20:00:00+01:00",
    "I1": "2026-06-16T20:00:00+01:00", "I2": "2026-06-17T02:00:00+01:00",
    "I3": "2026-06-22T20:00:00+01:00", "I4": "2026-06-22T20:00:00+01:00",
    "I5": "2026-06-26T20:00:00+01:00", "I6": "2026-06-26T20:00:00+01:00",
    "J1": "2026-06-16T23:00:00+01:00", "J2": "2026-06-17T05:00:00+01:00",
    "J3": "2026-06-22T23:00:00+01:00", "J4": "2026-06-22T23:00:00+01:00",
    "J5": "2026-06-28T03:00:00+01:00", "J6": "2026-06-28T03:00:00+01:00",
    "K1": "2026-06-17T20:00:00+01:00", "K2": "2026-06-18T02:00:00+01:00",
    "K3": "2026-06-23T20:00:00+01:00", "K4": "2026-06-24T02:00:00+01:00",
    "K5": "2026-06-27T23:00:00+01:00", "K6": "2026-06-27T23:00:00+01:00",
    "L1": "2026-06-17T21:00:00+01:00", "L2": "2026-06-18T00:00:00+01:00",
    "L3": "2026-06-23T23:00:00+01:00", "L4": "2026-06-24T02:00:00+01:00",
    "L5": "2026-06-27T20:00:00+01:00", "L6": "2026-06-27T20:00:00+01:00",
}


def load_previous_ranks() -> Dict[str, int]:
    """Read the existing leaderboard output to capture each player's prior rank."""
    if not os.path.exists(LEADERBOARD_OUT):
        return {}
    try:
        with open(LEADERBOARD_OUT, encoding="utf-8") as fh:
            data = json.load(fh)
        return {e["name"]: e["rank"] for e in data.get("leaderboard", []) if "rank" in e}
    except (json.JSONDecodeError, KeyError, OSError):
        return {}


def load_rank_history() -> List[dict]:
    """Read the existing rank-history.json (list of {date, ranks: {name: rank}})."""
    if not os.path.exists(RANK_HISTORY_OUT):
        return []
    try:
        with open(RANK_HISTORY_OUT, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


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
def build(rows: List[dict], results: dict) -> Tuple[dict, dict, List[dict]]:
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
            "kickoff": KICKOFFS.get(mid),
            "result": actual.get(mid),
        })

    previous_ranks = load_previous_ranks()

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
        entry["previous_rank"] = previous_ranks.get(entry["name"])

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

    # Append today's rank snapshot to the rank-history (for the leaderboard
    # trend sparklines). One snapshot per calendar day (UTC); re-running the
    # script on the same day overwrites that day's snapshot.
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rank_history = load_rank_history()
    snapshot = {"date": today, "ranks": {e["name"]: e["rank"] for e in leaderboard}}
    if rank_history and rank_history[-1].get("date") == today:
        rank_history[-1] = snapshot
    else:
        rank_history.append(snapshot)
    rank_history = rank_history[-RANK_HISTORY_MAX:]

    return leaderboard_data, predictions_data, rank_history


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
    leaderboard_data, predictions_data, rank_history = build(rows, results)

    with open(LEADERBOARD_OUT, "w", encoding="utf-8") as fh:
        json.dump(leaderboard_data, fh, indent=2, ensure_ascii=False)
    with open(PREDICTIONS_OUT, "w", encoding="utf-8") as fh:
        json.dump(predictions_data, fh, indent=2, ensure_ascii=False)
    with open(RANK_HISTORY_OUT, "w", encoding="utf-8") as fh:
        json.dump(rank_history, fh, indent=2, ensure_ascii=False)

    lb = leaderboard_data["leaderboard"]
    print(f"\n[OK] {LEADERBOARD_OUT} + {PREDICTIONS_OUT} + {RANK_HISTORY_OUT} written")
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

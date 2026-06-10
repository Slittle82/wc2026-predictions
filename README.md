# World Cup 2026 Prediction Contest — Durham Football Lodge

A static, no-server leaderboard for the WC2026 group-stage prediction contest.

**Live site:** https://slittle82.github.io/wc2026-predictions/

```
Google Form  →  Google Sheets (published CSV)  →  GitHub Action  →  GitHub Pages
   entries          predictions + names            scoring            website
```

## How to update scores (the only thing you do)

Everything runs on GitHub — **no Mac/Terminal needed**.

1. On GitHub, open **`results.json`** and click the pencil (✏️) to edit.
2. Fill in the finished matches as `"home-away"`, e.g.:
   ```json
   "results": {
     "A1": "2-1",
     "A2": "1-1",
     "B1": "3-0"
   }
   ```
   Leave unfinished matches as `""`.
3. When the tournament ends, set `"winner"` (and `"runner_up"` for the losing finalist).
4. Click **Commit changes**.
5. The **Update Leaderboard** Action runs automatically (~1 min): it fetches the live
   predictions from Google Sheets, recalculates everyone's scores, and republishes
   `leaderboard-data.json` and `predictions.json`. The website updates itself.

You can also trigger it manually: **Actions → Update Leaderboard → Run workflow**.

## The website (`index.html`)

- **Leaderboard** — ranked standings with totals, match points, winner-bonus points,
  perfect-score count, paid status, and live name search.
- **My Picks** — anyone selects their name to see all 72 of their predictions, grouped,
  with points per match once results are in.
- **Fixtures** — every group-stage match with actual results as they come in.
- **Rules** — entry, payment, scoring and tie-breakers.

## Scoring

| Outcome | Points |
|---|---|
| Correct result only (W/D/L) | 3 |
| Correct result + one exact team score | 4 |
| Perfect prediction (both scores exact) | 6 |
| One team's score correct, wrong result | 1 |
| Tournament winner correct | +12 |
| Predicted winner finishes runner-up | +5 |

Tie-breakers: most perfect (6-pt) predictions, then most correct results (3-pt).

## Files

| File | Purpose |
|---|---|
| `index.html` | The website (Leaderboard / My Picks / Fixtures / Rules) |
| `results.json` | **Edit this** to enter match results + winner |
| `calculate_scores.py` | Scoring engine → writes the two JSON files |
| `leaderboard-data.json` | Generated: ranked standings |
| `predictions.json` | Generated: everyone's picks (for My Picks + Fixtures) |
| `.github/workflows/update-leaderboard.yml` | Runs the script automatically on GitHub |
| `MATCH_IDS.md` | Reference list of all 72 match IDs |

## Running locally (optional)

```bash
python3 calculate_scores.py            # uses the live published Google Sheet
```

Set `gh-pages`/Pages source to the `main` branch root, with `index.html` as the entry page.

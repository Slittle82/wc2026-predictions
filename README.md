# World Cup 2026 Prediction Contest - Leaderboard System

Python-based scoring calculator and leaderboard for your World Cup 2026 prediction contest.

## ✅ What's Already Configured

- **Google Sheets CSV URL**: Already set in `calculate_scores.py`
- **Column parsing**: Automatically detects A1-L6 match IDs (all 72 matches)
- **Payment column**: Recognizes your payment confirmation field
- **Scoring logic**: 
  - 1pt for each correct score (home/away)
  - 1pt for correct result (win/draw/loss)
  - Max 3pts per match
  - 12pts for tournament winner
  - 5pts for runner-up
- **Tie-breakers**: 3pt games → 2pt games → 1pt games

## 🚀 Quick Start

### 1. Verify Your Sheet is Published

Your CSV URL is configured, but make sure the sheet is accessible:

1. Open your Google Sheet
2. **File → Share → Publish to web**
3. Select "Form Responses 1" (the sheet with responses)
4. Format: "Comma-separated values (.csv)"
5. Click **Publish**
6. Test: Open this URL in your browser - it should download a CSV:
   ```
   https://docs.google.com/spreadsheets/d/e/2PACX-1vSMUj24sQdxvVfZz_wwk22sPr8q2wow2insdtVTa8e7p4tgOvsEp6diYMN1-22TsXFzoLyqM47SZE9H/pub?gid=1733040974&single=true&output=csv
   ```

### 2. Run the Script

```bash
python3 calculate_scores.py
```

**Output:**
- Creates `leaderboard-data.json`
- Shows top 10 standings in console
- Ready to deploy!

### 3. Deploy to GitHub Pages

```bash
# Initialize repo
git init
git add calculate_scores.py leaderboard.html leaderboard-data.json MATCH_IDS.md
git commit -m "Initial World Cup 2026 leaderboard"

# Push to GitHub
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/wc2026-predictions.git
git push -u origin main
```

Then enable GitHub Pages:
1. Go to repo **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** / folder: **/ (root)**
4. Save

Your leaderboard will be live at:
```
https://YOUR_USERNAME.github.io/wc2026-predictions/
```

(Rename `leaderboard.html` to `index.html` if you want it as the default page)

## 📊 Updating After Matches

### Step 1: Edit `calculate_scores.py`

Find the `RESULTS = {}` section (around line 246) and add match results:

```python
RESULTS = {
    'A1': '2-1',  # Mexico vs South Africa - FINISHED
    'A2': '1-1',  # South Korea vs Czechia - FINISHED
    'B1': '3-0',  # Canada vs Bosnia & Herzegovina - FINISHED
    # Add more as matches complete...
}
```

**Match ID Reference:** See `MATCH_IDS.md` for all 72 matches

### Step 2: Run the Script

```bash
python3 calculate_scores.py
```

### Step 3: Push to GitHub

```bash
git add leaderboard-data.json
git commit -m "Updated: Matches A1, A2, B1"
git push
```

GitHub Pages updates automatically in ~2 minutes.

## 🎯 Match ID Format

Your form uses this format:
- **Group A**: A1, A2, A3, A4, A5, A6
- **Group B**: B1, B2, B3, B4, B5, B6
- ... up to ...
- **Group L**: L1, L2, L3, L4, L5, L6

Examples from your form:
- `A1` = "A1: Mexico vs South Africa"
- `D2` = "D2: Australia vs Turkiye"
- `L6` = "L6: Croatia vs Ghana"

See `MATCH_IDS.md` for complete list with dates and times.

## 🏆 Tournament Winner/Runner-up

When the tournament ends, update these in `calculate_scores.py`:

```python
WINNER = "England"      # 12 points
RUNNER_UP = "Brazil"    # 5 points
```

## 📁 Files Included

- **`calculate_scores.py`** - Main scoring script (pre-configured)
- **`leaderboard.html`** - Web page for displaying results
- **`MATCH_IDS.md`** - Quick reference for all 72 matches
- **`leaderboard-data.json`** - Generated output (create by running script)

## 🔧 Troubleshooting

### "Error fetching CSV: 403 Forbidden"

Your sheet isn't published. Follow Step 1 above.

### "No data found in CSV"

Check that people have submitted predictions via your Google Form.

### Match points seem wrong

Verify:
1. Score format is always "X-Y" (e.g., "2-1" not "2 - 1")
2. Match ID matches your form (check `MATCH_IDS.md`)
3. Results are entered in the correct format

### Leaderboard not updating on GitHub Pages

- Wait 2-3 minutes after pushing
- Hard refresh browser (Ctrl+Shift+R / Cmd+Shift+R)
- Check GitHub Actions tab for deployment status

## 💡 Advanced: Automation

You could set up GitHub Actions to run the script automatically, but for your low-maintenance preference, **manual updates give you full control** and are simpler.

## 📋 Workflow Summary

**During Tournament (per match):**
1. Match finishes → Add result to `RESULTS` in script
2. Run `python3 calculate_scores.py`
3. `git add leaderboard-data.json && git commit -m "Match XX" && git push`
4. Done! (2 minutes total)

**No servers, no hosting costs, no complex infrastructure.**

## 🎮 Example Session

```bash
# Match A1 just finished: Mexico 2-1 South Africa
# Edit calculate_scores.py and add:
#   'A1': '2-1',

$ python3 calculate_scores.py
============================================================
World Cup 2026 Prediction Contest - Score Calculator
============================================================

Fetching data from Google Sheets...
Processing 1 completed matches

✓ Leaderboard generated: leaderboard-data.json
✓ Total entries: 15
✓ Matches completed: 1/72

============================================================
TOP 10 LEADERBOARD
============================================================
 1. Alice Smith          3 pts (3pt: 1 | 2pt: 0 | 1pt: 0)
 2. Bob Jones            2 pts (3pt: 0 | 2pt: 1 | 1pt: 0)
 3. Charlie Brown        1 pts (3pt: 0 | 2pt: 0 | 1pt: 1)
...

$ git add leaderboard-data.json
$ git commit -m "Match A1: Mexico 2-1 South Africa"
$ git push

# Leaderboard updates on GitHub Pages in ~2 minutes ✓
```

## ✨ Features

- ✅ Exact scoring logic as per your rules
- ✅ Proper tie-breaker handling
- ✅ Mobile-responsive leaderboard
- ✅ Payment status tracking
- ✅ Prize pool calculation (75% winner, 25% charity)
- ✅ Auto-refresh every 5 minutes
- ✅ No maintenance once deployed

---

**Questions?** Check `MATCH_IDS.md` for match reference, or review the code comments in `calculate_scores.py`.

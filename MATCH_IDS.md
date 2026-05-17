# Match ID Reference Guide

Use these match IDs when updating the `RESULTS` dictionary in `calculate_scores.py`.

## How to Use

In the script, update results like this:

```python
RESULTS = {
    'A1': '2-1',  # Mexico vs South Africa
    'A2': '1-1',  # South Korea vs Czechia
    'B1': '3-0',  # Canada vs Bosnia & Herzegovina
    # ... add more as matches finish
}
```

---

## All 72 Matches

### Group A (A1-A6)
- **A1**: Mexico vs South Africa — 11 June, 20:00 BST
- **A2**: South Korea vs Czechia — 12 June, 03:00 BST
- **A3**: Czechia vs South Africa — 18 June, 17:00 BST
- **A4**: Mexico vs South Korea — 19 June, 03:00 BST
- **A5**: Czechia vs Mexico — 25 June, 03:00 BST
- **A6**: South Africa vs South Korea — 25 June, 03:00 BST

### Group B (B1-B6)
- **B1**: Canada vs Bosnia & Herzegovina — 12 June, 20:00 BST
- **B2**: Qatar vs Switzerland — 13 June, 02:00 BST
- **B3**: Bosnia & Herzegovina vs Switzerland — 18 June, 23:00 BST
- **B4**: Canada vs Qatar — 19 June, 02:00 BST
- **B5**: Switzerland vs Canada — 24 June, 20:00 BST
- **B6**: Bosnia and Herzegovina vs Qatar — 24 June, 20:00 BST

### Group C (C1-C6)
- **C1**: Brazil vs Morocco — 13 June, 23:00 BST
- **C2**: Haiti vs Scotland — 14 June, 02:00 BST
- **C3**: Scotland vs Morocco — 19 June, 23:00 BST
- **C4**: Brazil vs Haiti — 20 June, 01:30 BST
- **C5**: Scotland vs Brazil — 24 June, 23:00 BST
- **C6**: Morocco vs Haiti — 24 June, 23:00 BST

### Group D (D1-D6)
- **D1**: United States vs Paraguay — 13 June, 20:00 BST
- **D2**: Australia vs Turkiye — 14 June, 05:00 BST
- **D3**: United States vs Australia — 19 June, 20:00 BST
- **D4**: Turkiye vs Paraguay — 20 June, 03:00 BST
- **D5**: Turkiye vs United States — 25 June, 23:00 BST
- **D6**: Paraguay vs Australia — 25 June, 23:00 BST

### Group E (E1-E6)
- **E1**: Germany vs Curacao — 14 June, 20:00 BST
- **E2**: Ivory Coast vs Ecuador — 15 June, 00:00 BST
- **E3**: Germany vs Ivory Coast — 20 June, 21:00 BST
- **E4**: Curacao vs Ecuador — 21 June, 01:00 BST
- **E5**: Ecuador vs Germany — 25 June, 20:00 BST
- **E6**: Curacao vs Ivory Coast — 25 June, 20:00 BST

### Group F (F1-F6)
- **F1**: Netherlands vs Japan — 14 June, 23:00 BST
- **F2**: Sweden vs Tunisia — 15 June, 02:00 BST
- **F3**: Netherlands vs Sweden — 20 June, 18:00 BST
- **F4**: Japan vs Tunisia — 21 June, 00:00 BST
- **F5**: Tunisia vs Netherlands — 26 June, 00:00 BST
- **F6**: Japan vs Sweden — 26 June, 00:00 BST

### Group G (G1-G6)
- **G1**: Belgium vs Egypt — 15 June, 20:00 BST
- **G2**: Iran vs New Zealand — 16 June, 02:00 BST
- **G3**: Belgium vs Iran — 20 June, 20:00 BST
- **G4**: Egypt vs New Zealand — 21 June, 02:00 BST
- **G5**: New Zealand vs Belgium — 26 June, 23:00 BST
- **G6**: Egypt vs Iran — 26 June, 23:00 BST

### Group H (H1-H6)
- **H1**: Spain vs Cape Verde — 15 June, 17:00 BST
- **H2**: Saudi Arabia vs Uruguay — 15 June, 23:00 BST
- **H3**: Spain vs Saudi Arabia — 21 June, 17:00 BST
- **H4**: Uruguay vs Cape Verde — 21 June, 23:00 BST
- **H5**: Uruguay vs Spain — 26 June, 20:00 BST
- **H6**: Cape Verde vs Saudi Arabia — 26 June, 20:00 BST

### Group I (I1-I6)
- **I1**: France vs Senegal — 16 June, 20:00 BST
- **I2**: Iraq vs Norway — 17 June, 02:00 BST
- **I3**: France vs Iraq — 22 June, 20:00 BST
- **I4**: Senegal vs Norway — 22 June, 20:00 BST
- **I5**: Norway vs France — 26 June, 20:00 BST
- **I6**: Senegal vs Iraq — 26 June, 20:00 BST

### Group J (J1-J6)
- **J1**: Argentina vs Algeria — 16 June, 23:00 BST
- **J2**: Austria vs Jordan — 17 June, 05:00 BST
- **J3**: Argentina vs Austria — 22 June, 23:00 BST
- **J4**: Algeria vs Jordan — 22 June, 23:00 BST
- **J5**: Jordan vs Argentina — 28 June, 03:00 BST
- **J6**: Algeria vs Austria — 28 June, 03:00 BST

### Group K (K1-K6)
- **K1**: Portugal vs Uzbekistan — 17 June, 20:00 BST
- **K2**: DR Congo vs Colombia — 18 June, 02:00 BST
- **K3**: Portugal vs DR Congo — 23 June, 20:00 BST
- **K4**: Uzbekistan vs Colombia — 24 June, 02:00 BST
- **K5**: Colombia vs Portugal — 27 June, 23:00 BST
- **K6**: Uzbekistan vs DR Congo — 27 June, 23:00 BST

### Group L (L1-L6)
- **L1**: England vs Croatia — 17 June, 21:00 BST
- **L2**: Ghana vs Panama — 18 June, 00:00 BST
- **L3**: England vs Ghana — 23 June, 23:00 BST
- **L4**: Croatia vs Panama — 24 June, 02:00 BST
- **L5**: Panama vs England — 27 June, 20:00 BST
- **L6**: Croatia vs Ghana — 27 June, 20:00 BST

---

## Example: After First Day of Matches

```python
RESULTS = {
    'A1': '2-1',  # Mexico beat South Africa 2-1
}
```

## Example: After First Week

```python
RESULTS = {
    'A1': '2-1',  # Mexico vs South Africa
    'A2': '1-1',  # South Korea vs Czechia (draw)
    'B1': '3-0',  # Canada vs Bosnia & Herzegovina
    'B2': '0-2',  # Qatar vs Switzerland
    'C1': '4-1',  # Brazil vs Morocco
    'C2': '1-0',  # Haiti vs Scotland
    'D1': '2-2',  # United States vs Paraguay (draw)
    'D2': '1-3',  # Australia vs Turkiye
}
```

---

## Quick Update Workflow

1. Open `calculate_scores.py` in a text editor
2. Find the `RESULTS = {` section (around line 243)
3. Add the new match result: `'A1': '2-1',`
4. Save the file
5. Run: `python3 calculate_scores.py`
6. Commit and push `leaderboard-data.json` to GitHub

Done! 🎉

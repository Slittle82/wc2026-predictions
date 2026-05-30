#!/usr/bin/env python3
"""
World Cup 2026 Prediction Contest Score Calculator

Reads predictions from Google Sheets CSV export and calculates scores based on:
- 1 point for each correct individual score (home or away)
- 1 point for correct result (win/draw/loss)
- Maximum 3 points per match (both scores + result correct)
- 12 points for correct tournament winner
- 5 points for correct runner-up

Outputs leaderboard JSON for display on GitHub Pages.
"""

import csv
import json
import sys
from typing import Dict, List, Tuple
from urllib.request import urlopen, Request


def parse_score(score_str: str) -> Tuple[int, int]:
    """Parse a score string like '3-1' into (home, away) tuple."""
    if not score_str or '-' not in score_str:
        return None
    try:
        parts = score_str.strip().split('-')
        return (int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return None


def get_result(home: int, away: int) -> int:
    """Get match result: 1 = home win, 0 = draw, -1 = away win."""
    if home > away:
        return 1
    elif home < away:
        return -1
    else:
        return 0


def calculate_match_points(prediction: str, actual: str) -> Tuple[int, str]:
    """
    Calculate points for a single match prediction.
    
    Scoring system:
    - 1pt for each correct team score (home or away, max 2pts from scores)
    - 3pts for correct result (win/draw/loss)
    - Total can be: 0, 1, 2, 3, 4, 5, or 6 points
    
    Examples:
    - Actual 3-1, Predict 3-1: 1+1+3 = 6pts (perfect)
    - Actual 3-1, Predict 3-0: 1+3 = 4pts (home score + result)
    - Actual 3-1, Predict 2-1: 1+3 = 4pts (away score + result)
    - Actual 3-1, Predict 1-0: 3pts (result only)
    - Actual 3-1, Predict 3-2: 1pt (home score only, wrong result)
    - Actual 3-1, Predict 0-2: 0pts (nothing correct)
    
    Returns:
        (points, category) where category is '6pt', '5pt', '4pt', '3pt', '2pt', '1pt', or '0pt'
    """
    pred_score = parse_score(prediction)
    actual_score = parse_score(actual)
    
    # If either is invalid or actual result not available yet, return 0
    if not pred_score or not actual_score:
        return (0, '0pt')
    
    pred_home, pred_away = pred_score
    actual_home, actual_away = actual_score
    
    # Count correct elements
    points = 0
    
    # 1pt for correct home score
    if pred_home == actual_home:
        points += 1
    
    # 1pt for correct away score
    if pred_away == actual_away:
        points += 1
    
    # 3pts for correct result
    if get_result(pred_home, pred_away) == get_result(actual_home, actual_away):
        points += 3
    
    # Bonus: 1pt if both scores AND result are all correct (perfect prediction gets 6pts)
    if pred_home == actual_home and pred_away == actual_away and get_result(pred_home, pred_away) == get_result(actual_home, actual_away):
        points += 1  # Bonus to make perfect = 6pts (1+1+3+1)
    
    # Determine category for display
    if points == 6:
        category = '6pt'  # Both scores + result
    elif points == 5:
        category = '5pt'  # Both scores + result
    elif points == 4:
        category = '4pt'  # One score + result (1+3)
    elif points == 3:
        category = '3pt'  # Result only
    elif points == 2:
        category = '2pt'  # Both scores correct but wrong result
    elif points == 1:
        category = '1pt'  # One score correct (regardless of result)
    else:
        category = '0pt'  # Nothing correct
    
    return (points, category)


def calculate_leaderboard(predictions_csv_url: str, results: Dict[str, str], 
                         winner: str = None, runner_up: str = None) -> List[Dict]:
    """
    Calculate leaderboard from predictions CSV and results.
    
    Args:
        predictions_csv_url: URL to published Google Sheets CSV
        results: Dict mapping match IDs to actual scores (e.g., {'A1': '3-1', 'B2': '2-0'})
        winner: Tournament winner team name
        runner_up: Tournament runner-up team name
    
    Returns:
        List of participant dicts sorted by total points and tie-breakers
    """
    # Fetch CSV data
    try:
        import ssl
        # Create SSL context that doesn't verify certificates (for Google Sheets)
        context = ssl._create_unverified_context()
        
        req = Request(predictions_csv_url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        req.add_header('Accept', 'text/csv,text/plain,*/*')
        response = urlopen(req, context=context)
        csv_data = response.read().decode('utf-8').splitlines()
    except Exception as e:
        print(f"Error fetching CSV: {e}")
        print(f"\nAttempted URL: {predictions_csv_url}")
        print("\nTroubleshooting:")
        print("1. Make sure your Google Sheet is published to the web")
        print("2. Go to File → Share → Publish to web")
        print("3. In the dialog, select:")
        print("   - 'Entire Document' or the specific sheet")
        print("   - 'Comma-separated values (.csv)'")
        print("4. Click 'Publish' and copy the URL")
        print("5. The URL should look like:")
        print("   https://docs.google.com/spreadsheets/d/e/2PACX-.../pub?output=csv")
        print("\nAlternative: Try accessing the URL in your browser first to verify it works")
        sys.exit(1)
    
    # Parse CSV
    reader = csv.DictReader(csv_data)
    rows = list(reader)
    
    if not rows:
        print("No data found in CSV")
        sys.exit(1)
    
    # Get all columns
    first_row = rows[0]
    all_columns = list(first_row.keys())
    
    # Match columns are labeled A1-A6, B1-B6, etc. up to L6 (72 total)
    # Find them by looking for pattern like "A1:", "B2:", etc.
    match_columns = {}  # Will map match_id (e.g., 'A1') to full column name
    winner_column = None
    
    for col in all_columns:
        # Check if column matches pattern like "A1:", "B2:", etc.
        if len(col) >= 3 and col[0].isalpha() and col[1].isdigit() and col[2] == ':':
            # Extract match ID (e.g., "A1" from "A1: Mexico vs South Africa")
            match_id = col.split(':')[0].strip()
            match_columns[match_id] = col
        # Find winner column
        elif 'winner' in col.lower() and 'tournament' in col.lower():
            winner_column = col
    
    print(f"Found {len(match_columns)} match columns")
    if winner_column:
        print(f"Winner column: '{winner_column}'")
    
    # Calculate scores for each participant
    leaderboard = []
    
    for row in rows:
        name = row.get('Name', '').strip()
        email = row.get('Email address', '').strip()
        payment = row.get('Please confirm that you have transferred £10 entry fee. Do not progress until fee is transferred.', '').strip()
        
        # Skip if no name
        if not name:
            continue
        
        # Initialize counters
        total_points = 0
        games_6pt = 0
        games_3pt = 0
        winner_points = 0
        
        # Calculate match points
        for match_id, column_name in match_columns.items():
            prediction = row.get(column_name, '').strip()
            actual = results.get(match_id, '')
            
            points, category = calculate_match_points(prediction, actual)
            total_points += points
            
            # Track for tie-breakers: 6pt games (perfect) and 3pt games (result only)
            if points == 6:
                games_6pt += 1
            elif points == 3:
                games_3pt += 1
        
        # Calculate winner/runner-up points
        predicted_winner = ''
        if winner_column:
            predicted_winner = row.get(winner_column, '').strip()
            
            if predicted_winner and winner:
                if predicted_winner.lower() == winner.lower():
                    winner_points = 12
                    total_points += 12
                elif runner_up and predicted_winner.lower() == runner_up.lower():
                    winner_points = 5
                    total_points += 5
        
        leaderboard.append({
            'name': name,
            'email': email,
            'payment': payment,
            'total_points': total_points,
            'match_points': total_points - winner_points,
            'winner_points': winner_points,
            'games_6pt': games_6pt,
            'games_3pt': games_3pt,
            'predicted_winner': predicted_winner
        })
    
    # Sort by tie-breaker rules:
    # 1. Total points (highest first)
    # 2. Most 6pt games (perfect predictions)
    # 3. Most 3pt games (correct results)
    leaderboard.sort(
        key=lambda x: (x['total_points'], x['games_6pt'], x['games_3pt']),
        reverse=True
    )
    
    # Add rank
    for i, entry in enumerate(leaderboard, 1):
        entry['rank'] = i
    
    return leaderboard


def main():
    """Main entry point - customize this section with your configuration."""
    
    # CONFIGURATION - UPDATE THESE VALUES
    # ====================================
    
    # Your published Google Sheets CSV URL
    PREDICTIONS_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSMUj24sQdxvVfZz_wwk22sPr8q2wow2insdtVTa8e7p4tgOvsEp6diYMN1-22TsXFzoLyqM47SZE9H/pub?gid=1733040974&single=true&output=csv"
    
    # Match results - add these as matches are played
    # Format: 'A1': 'home-away', 'B2': 'home-away', etc.
    # Match IDs match your form: A1-A6 (Group A), B1-B6 (Group B), etc.
    RESULTS = {
        # Group A examples:
        # 'A1': '2-1',  # Mexico vs South Africa
        # 'A2': '1-1',  # South Korea vs Czechia
        # 'A3': '0-0',  # Czechia vs South Africa
        # 'A4': '3-1',  # Mexico vs South Korea
        # 'A5': '2-0',  # Czechia vs Mexico
        # 'A6': '1-0',  # South Africa vs South Korea
        
        # Add more as matches are played...
    }
    
    # Tournament winner and runner-up (leave as None until known)
    WINNER = None  # e.g., "England"
    RUNNER_UP = None  # e.g., "Brazil"
    
    # Output file path
    OUTPUT_FILE = "leaderboard-data.json"
    
    # ====================================
    # END CONFIGURATION
    # ====================================
    
    print("=" * 60)
    print("World Cup 2026 Prediction Contest - Score Calculator")
    print("=" * 60)
    print(f"\nFetching data from Google Sheets...")
    print(f"Processing {len(RESULTS)} completed matches\n")
    
    # Calculate leaderboard
    leaderboard = calculate_leaderboard(
        PREDICTIONS_CSV_URL,
        RESULTS,
        WINNER,
        RUNNER_UP
    )
    
    # Prepare output data
    output = {
        'last_updated': None,  # Will be set by JavaScript
        'total_entries': len(leaderboard),
        'matches_completed': len(RESULTS),
        'total_matches': 72,
        'winner': WINNER,
        'runner_up': RUNNER_UP,
        'leaderboard': leaderboard
    }
    
    # Write to JSON file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Leaderboard generated: {OUTPUT_FILE}")
    print(f"✓ Total entries: {len(leaderboard)}")
    print(f"✓ Matches completed: {len(RESULTS)}/72")
    
    # Display top 10
    print("\n" + "=" * 60)
    print("TOP 10 LEADERBOARD")
    print("=" * 60)
    for entry in leaderboard[:10]:
        print(f"{entry['rank']:2d}. {entry['name']:20s} {entry['total_points']:3d} pts "
              f"(3pt:{entry['games_3pt']:2d} | 2pt:{entry['games_2pt']:2d} | 1pt:{entry['games_1pt']:2d})")
    
    if len(leaderboard) > 10:
        print(f"\n... and {len(leaderboard) - 10} more entries")
    
    print("\n" + "=" * 60)
    print("Update complete! Push leaderboard-data.json to GitHub Pages.")
    print("=" * 60)


if __name__ == '__main__':
    main()

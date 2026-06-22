#!/usr/bin/env python3
"""
Generate an HTML dashboard of recent stumped games.
Outputs to stumpers_report.html
"""
import json
import sys
from pathlib import Path
from collections import defaultdict
import statistics
import requests
from datetime import datetime
from urllib.parse import quote

# Supabase credentials
SUPABASE_URL = "https://ciwopsvjasfustqjspqm.supabase.co/rest/v1"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNpd29wc3ZqYXNmdXN0cWpzcHFtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE1MzMxOTksImV4cCI6MjA5NzEwOTE5OX0.S3cOJS1J6HFAUIL8Ypfg6Q73JrITLfpdksVpRUx1pLk"
ADMIN_KEY = "ushermein114!"

def fetch_stumped_games(limit=30):
    """Fetch recent stumped games from Supabase."""
    try:
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json"
        }
        url = f"{SUPABASE_URL}/games?outcome=eq.stumped&order=created_at.desc&limit={limit}"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching stumped games: {e}", file=sys.stderr)
        return []

def generate_html(games):
    """Generate HTML dashboard."""
    if not games:
        return "<p>No stumped games found.</p>"

    # Calculate stats
    question_counts = [g.get('question_count', 0) for g in games]
    remaining_counts = [g.get('remaining_candidates') for g in games if g.get('remaining_candidates')]

    stats = {
        'total': len(games),
        'avg_questions': statistics.mean(question_counts) if question_counts else 0,
        'median_questions': statistics.median(question_counts) if question_counts else 0,
        'avg_remaining': statistics.mean(remaining_counts) if remaining_counts else 0,
    }

    # Build stumper map
    stumper_counts = defaultdict(int)
    for game in games:
        stumper = game.get('stumper_name') or game.get('guessed_movie_title', 'Unknown')
        stumper_counts[stumper] += 1

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stumpers Dashboard - Indian Movie Charades</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .stat-box {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .stat-label {{ color: #666; font-size: 12px; text-transform: uppercase; }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-top: 5px;
        }}
        .games-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .game-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-top: 4px solid #667eea;
        }}
        .game-card.repeated {{
            border-top-color: #ff6b6b;
        }}
        .stumper-title {{
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            word-break: break-word;
        }}
        .game-meta {{
            font-size: 13px;
            color: #666;
            margin-bottom: 8px;
        }}
        .meta-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
        }}
        .meta-label {{ color: #999; }}
        .meta-value {{ font-weight: 600; color: #333; }}
        .guessed {{
            background: #f0f0f0;
            padding: 8px;
            border-radius: 4px;
            margin-top: 10px;
            font-size: 13px;
        }}
        .guessed-label {{
            color: #666;
            font-size: 11px;
            text-transform: uppercase;
        }}
        .repeated-badge {{
            display: inline-block;
            background: #ff6b6b;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 8px;
        }}
        .footer {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            color: #666;
            font-size: 13px;
        }}
        .admin-link {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            margin-top: 10px;
            font-weight: 600;
        }}
        .admin-link:hover {{ background: #5568d3; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 Stumpers Dashboard</h1>
            <p style="color: #666; margin-bottom: 20px;">Films the genie couldn't identify</p>

            <div class="stats">
                <div class="stat-box">
                    <div class="stat-label">Total Stumpers</div>
                    <div class="stat-value">{stats['total']}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Avg Questions</div>
                    <div class="stat-value">{stats['avg_questions']:.1f}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Median Questions</div>
                    <div class="stat-value">{stats['median_questions']:.0f}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Avg Remaining</div>
                    <div class="stat-value">{stats['avg_remaining']:.1f}</div>
                </div>
            </div>
        </div>

        <div class="games-grid">
"""

    for game in games:
        stumper = game.get('stumper_name') or game.get('guessed_movie_title', 'Unknown')
        guessed = game.get('guessed_movie_title', 'Unknown')
        questions = game.get('question_count', 0)
        remaining = game.get('remaining_candidates', '?')
        created = game.get('created_at', '?')

        # Format date
        if created != '?':
            try:
                dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                created = dt.strftime('%b %d, %I:%M %p')
            except:
                pass

        count = stumper_counts[stumper]
        repeated_class = 'repeated' if count > 1 else ''
        repeated_badge = f'<span class="repeated-badge">×{count}</span>' if count > 1 else ''

        html += f"""
            <div class="game-card {repeated_class}">
                <div class="stumper-title">
                    {stumper}{repeated_badge}
                </div>
                <div class="game-meta">
                    <div class="meta-row">
                        <span class="meta-label">Asked</span>
                        <span class="meta-value">{questions} questions</span>
                    </div>
                    <div class="meta-row">
                        <span class="meta-label">Remaining</span>
                        <span class="meta-value">{remaining} candidates</span>
                    </div>
                    <div class="meta-row">
                        <span class="meta-label">Time</span>
                        <span class="meta-value">{created}</span>
                    </div>
                </div>
                <div class="guessed">
                    <div class="guessed-label">Genie guessed:</div>
                    {guessed}
                </div>
            </div>
"""

    html += """
        </div>

        <div class="footer">
            <p>Use the admin dashboard to review and manage stumpers</p>
            <a href="https://movie-charades.onrender.com/admin?key=ushermein114!" class="admin-link" target="_blank">
                Open Admin Dashboard →
            </a>
            <p style="margin-top: 15px; font-size: 12px;">
                Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC") + """
            </p>
        </div>
    </div>
</body>
</html>
"""
    return html

def main():
    print("Fetching stumped games from Supabase...")
    games = fetch_stumped_games(limit=30)

    if not games:
        print("No stumped games found.")
        return

    print(f"Generating dashboard with {len(games)} games...")
    html = generate_html(games)

    output_path = Path("stumpers_report.html")
    output_path.write_text(html)

    print(f"✓ Dashboard saved to {output_path}")
    print(f"\nOpen in browser: open {output_path}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
generate_star_history.py — Fetch stargazers for a GitHub repo and render a static SVG chart.
No third-party dependencies (stdlib only).
"""

import os
import sys
import json
import ssl
import subprocess
import urllib.request
from datetime import datetime

REPO = os.environ.get("GITHUB_REPOSITORY", "winstonkoh87/Athena-Public")
OUTPUT_PATH = sys.argv[1] if len(sys.argv) > 1 else ".github/assets/star-history.svg"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

if not TOKEN:
    try:
        TOKEN = subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    except Exception:
        TOKEN = None

def fetch_stargazers(repo, token):
    stargazers = []
    
    # Try gh CLI first if available locally
    try:
        cmd = ["gh", "api", f"repos/{repo}/stargazers", "--paginate", "-H", "Accept: application/vnd.github.v3.star+json"]
        output = subprocess.check_output(cmd, text=True)
        data = json.loads(output)
        for item in data:
            starred_at = item.get("starred_at")
            if starred_at:
                stargazers.append(datetime.strptime(starred_at, "%Y-%m-%dT%H:%M:%SZ"))
        if stargazers:
            stargazers.sort()
            return stargazers
    except Exception:
        pass

    # Fallback to urllib.request
    page = 1
    try:
        ctx = ssl.create_default_context()
    except Exception:
        ctx = ssl._create_unverified_context()

    while True:
        url = f"https://api.github.com/repos/{repo}/stargazers?per_page=100&page={page}"
        headers = {
            "Accept": "application/vnd.github.v3.star+json",
            "User-Agent": "Athena-Star-History-Generator"
        }
        if token:
            headers["Authorization"] = f"token {token}"
            
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, context=ctx) as resp:
                data = json.loads(resp.read().decode())
                if not data:
                    break
                for item in data:
                    starred_at = item.get("starred_at")
                    if starred_at:
                        stargazers.append(datetime.strptime(starred_at, "%Y-%m-%dT%H:%M:%SZ"))
                if len(data) < 100:
                    break
                page += 1
        except Exception as e:
            # If default SSL failed, try unverified SSL context
            try:
                unverified_ctx = ssl._create_unverified_context()
                with urllib.request.urlopen(req, context=unverified_ctx) as resp:
                    data = json.loads(resp.read().decode())
                    if not data:
                        break
                    for item in data:
                        starred_at = item.get("starred_at")
                        if starred_at:
                            stargazers.append(datetime.strptime(starred_at, "%Y-%m-%dT%H:%M:%SZ"))
                    if len(data) < 100:
                        break
                    page += 1
            except Exception as e2:
                print(f"Warning/Error fetching page {page}: {e2}", file=sys.stderr)
                break
            
    stargazers.sort()
    return stargazers

def generate_svg(stargazers, repo_name):
    width = 800
    height = 420
    padding_top = 70
    padding_bottom = 60
    padding_left = 65
    padding_right = 40
    
    chart_w = width - padding_left - padding_right
    chart_h = height - padding_top - padding_bottom
    
    total_stars = len(stargazers)
    
    if not stargazers:
        dates = [datetime.now()]
        counts = [0]
    else:
        dates = [stargazers[0]]
        counts = [1]
        for idx, dt in enumerate(stargazers[1:], start=2):
            dates.append(dt)
            counts.append(idx)
            
    min_date = dates[0]
    max_date = dates[-1] if len(dates) > 1 else datetime.now()
    if min_date == max_date:
        time_span = 1
    else:
        time_span = (max_date - min_date).total_seconds()
        
    max_y = max(total_stars, 10)
    if max_y <= 50:
        y_step = 10
    elif max_y <= 200:
        y_step = 50
    elif max_y <= 500:
        y_step = 100
    else:
        y_step = 200
        
    grid_max_y = ((max_y // y_step) + 1) * y_step
    
    points = []
    for d, c in zip(dates, counts):
        if time_span > 0:
            x_ratio = (d - min_date).total_seconds() / time_span
        else:
            x_ratio = 1.0
        y_ratio = c / grid_max_y
        
        px = padding_left + x_ratio * chart_w
        py = padding_top + chart_h - (y_ratio * chart_h)
        points.append((px, py))
        
    path_d = f"M {points[0][0]:.1f} {points[0][1]:.1f}"
    for px, py in points[1:]:
        path_d += f" L {px:.1f} {py:.1f}"
        
    area_d = path_d + f" L {points[-1][0]:.1f} {padding_top + chart_h:.1f} L {points[0][0]:.1f} {padding_top + chart_h:.1f} Z"
    
    y_grid_html = []
    for y_val in range(0, grid_max_y + 1, y_step):
        y_pos = padding_top + chart_h - (y_val / grid_max_y * chart_h)
        y_grid_html.append(
            f'<line x1="{padding_left}" y1="{y_pos:.1f}" x2="{width - padding_right}" y2="{y_pos:.1f}" stroke="#21262d" stroke-width="1" stroke-dasharray="4 4"/>\n'
            f'<text x="{padding_left - 10}" y="{y_pos + 4:.1f}" fill="#8b949e" font-size="11" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" text-anchor="end">{y_val}</text>'
        )
        
    x_grid_html = []
    num_ticks = 4
    for i in range(num_ticks):
        fraction = i / (num_ticks - 1)
        tick_x = padding_left + fraction * chart_w
        tick_time = min_date.timestamp() + fraction * time_span
        tick_date_str = datetime.fromtimestamp(tick_time).strftime("%b %Y")
        x_grid_html.append(
            f'<text x="{tick_x:.1f}" y="{height - 25}" fill="#8b949e" font-size="11" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" text-anchor="middle">{tick_date_str}</text>'
        )
        
    last_px, last_py = points[-1]
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">
  <style>
    .title {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 600; fill: #f0f6fc; }}
    .subtitle {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; fill: #8b949e; }}
    .badge-bg {{ fill: #161b22; stroke: #30363d; stroke-width: 1px; rx: 6px; }}
    .badge-text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 13px; font-weight: 600; fill: #10b981; }}
  </style>

  <!-- Background Card -->
  <rect width="{width}" height="{height}" rx="12" fill="#0d1117" stroke="#30363d" stroke-width="1"/>

  <!-- Header -->
  <text x="{padding_left}" y="36" class="title">🌟 Star History</text>
  <text x="{padding_left + 140}" y="36" class="subtitle">{repo_name}</text>

  <!-- Star Count Badge -->
  <rect x="{width - padding_right - 110}" y="18" width="110" height="30" class="badge-bg"/>
  <text x="{width - padding_right - 55}" y="38" class="badge-text" text-anchor="middle">★ {total_stars} Stars</text>

  <!-- Grid Lines & Labels -->
  {''.join(y_grid_html)}
  {''.join(x_grid_html)}

  <!-- Area Fill Gradient -->
  <defs>
    <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#10b981" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#10b981" stop-opacity="0.0"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Chart Area & Path -->
  <path d="{area_d}" fill="url(#areaGradient)"/>
  <path d="{path_d}" fill="none" stroke="#10b981" stroke-width="2.5" filter="url(#glow)"/>

  <!-- Current Position Marker -->
  <circle cx="{last_px:.1f}" cy="{last_py:.1f}" r="5" fill="#10b981" stroke="#0d1117" stroke-width="2"/>
</svg>"""

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Successfully generated star history SVG at {OUTPUT_PATH} ({total_stars} stars)")

if __name__ == "__main__":
    stars = fetch_stargazers(REPO, TOKEN)
    generate_svg(stars, REPO)

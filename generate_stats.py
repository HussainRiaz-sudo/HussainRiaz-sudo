import html
import json
import math
import os
import re
import urllib.parse
import urllib.request

USERNAME = "HussainRiaz-sudo"
LANGS_COUNT = 5

LANGUAGE_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "SCSS": "#c6538c",
    "Jupyter Notebook": "#DA5B0B",
    "SQL": "#e38c00",
    "TSQL": "#e38c00",
    "PLpgSQL": "#336790",
    "C#": "#178600",
    "C++": "#f34b7d",
    "C": "#555555",
    "Java": "#b07219",
    "Kotlin": "#A97BFF",
    "Dart": "#00B4AB",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Ruby": "#701516",
    "PHP": "#4F5D95",
    "Swift": "#F05138",
    "R": "#198CE7",
    "Shell": "#89e051",
    "PowerShell": "#012456",
    "Dockerfile": "#384d54",
    "Vue": "#41b883",
}


def build_headers():
    headers = {
        "User-Agent": "HussainRiaz-sudo-Stats-Generator",
        "Accept": "application/vnd.github+json",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def get_json(url):
    req = urllib.request.Request(url, headers=build_headers())
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_calendar_contributions(username):
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        page_html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8")
        matches = re.findall(
            r'data-date="\d{4}-\d{2}-\d{2}"[^>]*>.*?(\d+|No)\s+contribution',
            page_html,
            re.DOTALL,
        )
        return sum(0 if c == "No" else int(c) for c in matches)
    except Exception:
        return 0


def fetch_all_repos(username):
    repos = []
    page = 1
    while True:
        url = (
            f"https://api.github.com/users/{username}/repos"
            f"?per_page=100&type=owner&page={page}"
        )
        batch = get_json(url)
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def fetch_search_count(endpoint, query):
    encoded = urllib.parse.quote(query, safe=":+")
    url = f"https://api.github.com/search/{endpoint}?q={encoded}&per_page=1"
    try:
        data = get_json(url)
        return int(data.get("total_count", 0))
    except Exception:
        return 0


def calculate_rank_progress(commits, prs, issues, stars, followers):
    def exp_cdf(x):
        return 1.0 - (2.0 ** (-x))

    def log_cdf(x):
        return x / (1.0 + x)

    commits_w, prs_w, issues_w, stars_w, followers_w = 2.0, 3.0, 1.0, 4.0, 1.0
    total_w = commits_w + prs_w + issues_w + stars_w + followers_w

    score = (
        commits_w * exp_cdf(commits / 250.0)
        + prs_w * exp_cdf(prs / 50.0)
        + issues_w * exp_cdf(issues / 25.0)
        + stars_w * log_cdf(stars / 50.0)
        + followers_w * log_cdf(followers / 10.0)
    ) / total_w

    progress = max(25.0, min(100.0, score * 100.0 + min(20.0, commits / 10.0)))
    return progress


def render_stats_svg(
    display_name, stars, commits, prs, issues, contributed_to, progress
):
    safe_title = html.escape(f"{display_name}'s GitHub Stats")
    radius = 40.0
    circumference = 2.0 * math.pi * radius
    arc_len = circumference * (progress / 100.0)

    rows = [
        (
            "Total Stars Earned:",
            f"{stars:,}",
            "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Zm0 2.445L6.615 5.5a.75.75 0 0 1-.564.41l-3.097.45 2.24 2.184a.75.75 0 0 1 .216.664l-.528 3.084 2.769-1.456a.75.75 0 0 1 .698 0l2.77 1.456-.53-3.084a.75.75 0 0 1 .216-.664l2.24-2.183-3.096-.45a.75.75 0 0 1-.564-.41L8 2.694Z",
        ),
        (
            "Total Commits:",
            f"{commits:,}",
            "M1.643 3.143.427 1.927A.25.25 0 0 0 0 2.104V5.75c0 .138.112.25.25.25h3.646a.25.25 0 0 0 .177-.427L2.715 4.215a6.5 6.5 0 1 1-1.18 4.458.75.75 0 1 0-1.493.154 8.001 8.001 0 1 0 1.6-5.684ZM7.75 4a.75.75 0 0 1 .75.75v2.992l2.028.812a.75.75 0 0 1-.557 1.392l-2.5-1A.751.751 0 0 1 7 8.25v-3.5A.75.75 0 0 1 7.75 4Z",
        ),
        (
            "Total PRs:",
            f"{prs:,}",
            "M1.5 3.25a2.25 2.25 0 1 1 3 2.122v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25Zm5.677-.177L9.573.677A.25.25 0 0 1 10 .854V2.5h1A2.5 2.5 0 0 1 13.5 5v5.628a2.251 2.251 0 1 1-1.5 0V5a1 1 0 0 0-1-1h-1v1.646a.25.25 0 0 1-.427.177L7.177 3.427a.25.25 0 0 1 0-.354ZM3.75 2.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm0 9.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm8.25.75a.75.75 0 1 0 1.5 0 .75.75 0 0 0-1.5 0Z",
        ),
        (
            "Total Issues:",
            f"{issues:,}",
            "M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3ZM8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0ZM1.5 8a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0Z",
        ),
        (
            "Contributed to:",
            f"{contributed_to:,}",
            "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z",
        ),
    ]

    rows_svg = []
    for idx, (label, val, icon_path) in enumerate(rows):
        y = 56 + idx * 25
        delay = 0.45 + idx * 0.12
        rows_svg.append(
            f"""        <g transform="translate(25, {y})" style="animation: fadeInAnimation 0.5s ease-in-out {delay:.2f}s backwards">
            <path fill="#2A9D8F" fill-rule="evenodd" d="{icon_path}"/>
            <text x="25" y="12.5" fill="#E0E1DD" font-family="'Segoe UI', Ubuntu, sans-serif" font-weight="600" font-size="14px">{html.escape(label)}</text>
            <text x="205" y="12.5" fill="#E0E1DD" font-family="'Segoe UI', Ubuntu, sans-serif" font-weight="700" font-size="14px">{html.escape(val)}</text>
        </g>"""
        )

    rows_joined = "\n".join(rows_svg)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="467" height="195" viewBox="0 0 467 195" fill="none" role="img" aria-label="{safe_title}">
    <style>
        @keyframes fadeInAnimation {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        @keyframes rankAnimation {{
            from {{ stroke-dasharray: 0 {circumference:.2f}; }}
            to {{ stroke-dasharray: {arc_len:.2f} {circumference:.2f}; }}
        }}
    </style>
    <rect x="0.5" y="0.5" rx="8" height="194" width="466" fill="#111E16" stroke="#2D6A4F" stroke-width="1"/>
    <g transform="translate(25, 35)">
        <text x="0" y="0" fill="#52796F" font-family="'Segoe UI', Ubuntu, sans-serif" font-weight="600" font-size="18px" style="animation: fadeInAnimation 0.8s ease-in-out backwards">{safe_title}</text>
    </g>
    <g>
{rows_joined}
    </g>
    <g transform="translate(382, 112)">
        <circle cx="0" cy="0" r="{radius:.0f}" fill="none" stroke="#2D6A4F" stroke-opacity="0.4" stroke-width="6"/>
        <circle cx="0" cy="0" r="{radius:.0f}" fill="none" stroke="#2A9D8F" stroke-width="6"
                stroke-dasharray="{arc_len:.2f} {circumference:.2f}"
                stroke-linecap="round" transform="rotate(-90)"
                style="animation: rankAnimation 1s ease-in-out backwards"/>
        <g transform="translate(-16, -16) scale(2)" style="animation: fadeInAnimation 0.6s ease-in-out 0.5s backwards">
            <path fill="#E0E1DD" fill-rule="evenodd" d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"/>
        </g>
    </g>
</svg>
"""


def render_top_langs_svg(lang_totals, count=5):
    sorted_langs = sorted(lang_totals.items(), key=lambda x: x[1], reverse=True)[:count]
    total_bytes = sum(b for _, b in sorted_langs) or 1

    bar_width = 417.0
    segments = []
    cur_x = 25.0
    for idx, (lang, b) in enumerate(sorted_langs):
        pct = (b / total_bytes) * 100.0
        seg_w = (b / total_bytes) * bar_width
        if idx == len(sorted_langs) - 1:
            seg_w = max(0.0, (25.0 + bar_width) - cur_x)
        color = LANGUAGE_COLORS.get(lang, "#2A9D8F")
        segments.append((lang, pct, cur_x, seg_w, color))
        cur_x += seg_w

    bar_rects = "\n".join(
        f'        <rect x="{x:.2f}" y="55" width="{w:.2f}" height="10" fill="{color}"/>'
        for _, _, x, w, color in segments
    )

    legend_items = []
    for idx, (lang, pct, _, _, color) in enumerate(segments):
        col = idx % 2
        row = idx // 2
        lx = 25 + col * 212
        ly = 95 + row * 32
        delay = 0.45 + idx * 0.12
        legend_items.append(
            f"""        <g transform="translate({lx}, {ly})" style="animation: fadeInAnimation 0.5s ease-in-out {delay:.2f}s backwards">
            <circle cx="6" cy="-4.5" r="5.5" fill="{color}"/>
            <text x="18" y="0" fill="#E0E1DD" font-family="'Segoe UI', Ubuntu, sans-serif" font-weight="600" font-size="13px">{html.escape(lang)} <tspan fill="#8DA998" font-weight="400" font-size="12.5px">{pct:.2f}%</tspan></text>
        </g>"""
        )

    legend_joined = "\n".join(legend_items)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="467" height="195" viewBox="0 0 467 195" fill="none" role="img" aria-label="Most Used Languages">
    <style>
        @keyframes fadeInAnimation {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
    </style>
    <defs>
        <mask id="lang-bar-mask">
            <rect x="25" y="55" width="{bar_width:.0f}" height="10" rx="5" fill="white"/>
        </mask>
    </defs>
    <rect x="0.5" y="0.5" rx="8" height="194" width="466" fill="#111E16" stroke="#2D6A4F" stroke-width="1"/>
    <g transform="translate(25, 35)">
        <text x="0" y="0" fill="#52796F" font-family="'Segoe UI', Ubuntu, sans-serif" font-weight="600" font-size="18px" style="animation: fadeInAnimation 0.8s ease-in-out backwards">Most Used Languages</text>
    </g>
    <rect x="25" y="55" width="{bar_width:.0f}" height="10" rx="5" fill="#1B3024"/>
    <g mask="url(#lang-bar-mask)">
{bar_rects}
    </g>
    <g>
{legend_joined}
    </g>
</svg>
"""


def main():
    user = get_json(f"https://api.github.com/users/{USERNAME}")
    display_name = user.get("name") or USERNAME
    followers = int(user.get("followers", 0))

    repos = fetch_all_repos(USERNAME)
    total_stars = 0
    non_fork_repos = 0
    lang_totals = {}

    for repo in repos:
        total_stars += int(repo.get("stargazers_count", 0))
        if not repo.get("fork", False):
            non_fork_repos += 1
            lang_data = get_json(repo["languages_url"])
            for lang, byte_count in lang_data.items():
                lang_totals[lang] = lang_totals.get(lang, 0) + int(byte_count)

    search_commits = fetch_search_count("commits", f"author:{USERNAME}")
    calendar_contribs = fetch_calendar_contributions(USERNAME)
    total_commits = max(search_commits, calendar_contribs)

    total_prs = fetch_search_count("issues", f"author:{USERNAME}+type:pr")
    total_issues = fetch_search_count("issues", f"author:{USERNAME}+type:issue")
    contributed_to = non_fork_repos

    progress = calculate_rank_progress(
        total_commits, total_prs, total_issues, total_stars, followers
    )

    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    stats_svg = render_stats_svg(
        display_name=display_name,
        stars=total_stars,
        commits=total_commits,
        prs=total_prs,
        issues=total_issues,
        contributed_to=contributed_to,
        progress=progress,
    )
    with open(os.path.join(assets_dir, "github-stats.svg"), "w", encoding="utf-8") as f:
        f.write(stats_svg)

    langs_svg = render_top_langs_svg(lang_totals, count=LANGS_COUNT)
    with open(os.path.join(assets_dir, "top-langs.svg"), "w", encoding="utf-8") as f:
        f.write(langs_svg)

    print(
        f"Generated assets/github-stats.svg and assets/top-langs.svg! "
        f"Commits={total_commits}, Stars={total_stars}, Repos={contributed_to}, "
        f"TopLangs={list(lang_totals.keys())}"
    )


if __name__ == "__main__":
    main()

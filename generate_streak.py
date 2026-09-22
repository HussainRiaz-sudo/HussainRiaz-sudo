import urllib.request
import re
from datetime import datetime

url = 'https://github.com/users/HussainRiaz-sudo/contributions'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

# Extract calendar days
day_matches = re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*>.*?(\d+|No)\s+contribution', html, re.DOTALL)
contribs = {}
for d, c in day_matches:
    contribs[d] = 0 if c == 'No' else int(c)

sorted_dates = sorted(contribs.keys())
total_contribs = sum(contribs.values())

first_contrib_date = next((d for d in sorted_dates if contribs[d] > 0), sorted_dates[0])

# Calculate longest streak
longest = 0
longest_start = ''
longest_end = ''
cur_l = 0
cur_l_start = ''

for d in sorted_dates:
    if contribs[d] > 0:
        if cur_l == 0:
            cur_l_start = d
        cur_l += 1
        if cur_l > longest:
            longest = cur_l
            longest_start = cur_l_start
            longest_end = d
    else:
        cur_l = 0

# Calculate current streak ending today or yesterday
today_str = datetime.now().strftime('%Y-%m-%d')
cur_streak = 0
cur_start = ''
cur_end = ''

# Check if today or yesterday has a commit
rev_dates = list(reversed(sorted_dates))
start_idx = 0
# If the latest date in calendar is 0, allow 1 day grace period (yesterday)
if rev_dates and contribs[rev_dates[0]] == 0 and len(rev_dates) > 1 and contribs[rev_dates[1]] > 0:
    start_idx = 1

for d in rev_dates[start_idx:]:
    if contribs[d] > 0:
        cur_streak += 1
        cur_start = d
        if not cur_end:
            cur_end = d
    else:
        break

def format_date(d_str):
    if not d_str:
        return ""
    dt = datetime.strptime(d_str, '%Y-%m-%d')
    return dt.strftime('%b %d, %Y')

def format_range(s_str, e_str):
    if not s_str:
        return "None"
    s_dt = datetime.strptime(s_str, '%Y-%m-%d')
    if not e_str or s_str == e_str:
        return s_dt.strftime('%b %d')
    e_dt = datetime.strptime(e_str, '%Y-%m-%d')
    if s_dt.year == e_dt.year:
        return f"{s_dt.strftime('%b %d')} - {e_dt.strftime('%b %d')}"
    return f"{s_dt.strftime('%b %d, %Y')} - {e_dt.strftime('%b %d, %Y')}"

total_range = f"{format_date(first_contrib_date)} - Present"
current_range = format_range(cur_start, cur_end)
longest_range = format_range(longest_start, longest_end)

svg_template = f"""<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'
            style='isolation: isolate' viewBox='0 0 495 195' width='495px' height='195px' direction='ltr'>
    <style>
        @keyframes currstreak {{
            0% {{ font-size: 3px; opacity: 0.2; }}
            80% {{ font-size: 34px; opacity: 1; }}
            100% {{ font-size: 28px; opacity: 1; }}
        }}
        @keyframes fadein {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}
    </style>
    <defs>
        <clipPath id='outer_rectangle'>
            <rect width='495' height='195' rx='8'/>
        </clipPath>
        <mask id='mask_out_ring_behind_fire'>
            <rect width='495' height='195' fill='white'/>
            <ellipse id='mask-ellipse' cx='247.5' cy='32' rx='13' ry='18' fill='black'/>
        </mask>
    </defs>
    <g clip-path='url(#outer_rectangle)'>
        <g style='isolation: isolate'>
            <rect stroke='#2D6A4F' fill='#111E16' rx='8' x='0.5' y='0.5' width='494' height='194'/>
        </g>
        <g style='isolation: isolate'>
            <line x1='165' y1='28' x2='165' y2='170' vector-effect='non-scaling-stroke' stroke-width='1' stroke='#2D6A4F' stroke-linejoin='miter' stroke-linecap='square' stroke-miterlimit='3'/>
            <line x1='330' y1='28' x2='330' y2='170' vector-effect='non-scaling-stroke' stroke-width='1' stroke='#2D6A4F' stroke-linejoin='miter' stroke-linecap='square' stroke-miterlimit='3'/>
        </g>
        <g style='isolation: isolate'>
            <!-- Total Contributions big number -->
            <g transform='translate(82.5, 48)'>
                <text x='0' y='32' stroke-width='0' text-anchor='middle' fill='#E0E1DD' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='700' font-size='28px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.6s'>
                    {total_contribs}
                </text>
            </g>

            <!-- Total Contributions label -->
            <g transform='translate(82.5, 84)'>
                <text x='0' y='32' stroke-width='0' text-anchor='middle' fill='#52796F' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='400' font-size='14px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.7s'>
                    Total Contributions
                </text>
            </g>

            <!-- Total Contributions range -->
            <g transform='translate(82.5, 114)'>
                <text x='0' y='32' stroke-width='0' text-anchor='middle' fill='#8DA998' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='400' font-size='12px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.8s'>
                    {total_range}
                </text>
            </g>
        </g>
        <g style='isolation: isolate'>
            <!-- Current Streak label -->
            <g transform='translate(247.5, 108)'>
                <text x='0' y='32' stroke-width='0' text-anchor='middle' fill='#52796F' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='700' font-size='14px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.9s'>
                    Current Streak
                </text>
            </g>

            <!-- Current Streak range -->
            <g transform='translate(247.5, 145)'>
                <text x='0' y='21' stroke-width='0' text-anchor='middle' fill='#8DA998' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='400' font-size='12px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.9s'>
                    {current_range}
                </text>
            </g>

            <!-- Ring around number -->
            <g mask='url(#mask_out_ring_behind_fire)'>
                <circle cx='247.5' cy='71' r='40' fill='none' stroke='#2A9D8F' stroke-width='5' style='opacity: 0; animation: fadein 0.5s linear forwards 0.4s'></circle>
            </g>
            <!-- Fire icon -->
            <g transform='translate(247.5, 19.5)' stroke-opacity='0' style='opacity: 0; animation: fadein 0.5s linear forwards 0.6s'>
                <path d='M -12 -0.5 L 15 -0.5 L 15 23.5 L -12 23.5 L -12 -0.5 Z' fill='none'/>
                <path d='M 1.5 0.67 C 1.5 0.67 2.24 3.32 2.24 5.47 C 2.24 7.53 0.89 9.2 -1.17 9.2 C -3.23 9.2 -4.79 7.53 -4.79 5.47 L -4.76 5.11 C -6.78 7.51 -8 10.62 -8 13.99 C -8 18.41 -4.42 22 0 22 C 4.42 22 8 18.41 8 13.99 C 8 8.6 5.41 3.79 1.5 0.67 Z M -0.29 19 C -2.07 19 -3.51 17.6 -3.51 15.86 C -3.51 14.24 -2.46 13.1 -0.7 12.74 C 1.07 12.38 2.9 11.53 3.92 10.16 C 4.31 11.45 4.51 12.81 4.51 14.2 C 4.51 16.85 2.36 19 -0.29 19 Z' fill='#E76F51' stroke-opacity='0'/>
            </g>

            <!-- Current Streak big number -->
            <g transform='translate(247.5, 48)'>
                <text x='0' y='32' stroke-width='0' text-anchor='middle' fill='#E0E1DD' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='700' font-size='28px' font-style='normal' style='animation: currstreak 0.6s linear forwards'>
                    {cur_streak}
                </text>
            </g>

        </g>
        <g style='isolation: isolate'>
            <!-- Longest Streak big number -->
            <g transform='translate(412.5, 48)'>
                <text x='0' y='32' stroke-width='0' text-anchor='middle' fill='#E0E1DD' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='700' font-size='28px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 1.2s'>
                    {longest}
                </text>
            </g>

            <!-- Longest Streak label -->
            <g transform='translate(412.5, 84)'>
                <text x='0' y='32' stroke-width='0' text-anchor='middle' fill='#52796F' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='400' font-size='14px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 1.3s'>
                    Longest Streak
                </text>
            </g>

            <!-- Longest Streak range -->
            <g transform='translate(412.5, 114)'>
                <text x='0' y='32' stroke-width='0' text-anchor='middle' fill='#8DA998' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='400' font-size='12px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 1.4s'>
                    {longest_range}
                </text>
            </g>
        </g>
    </g>
</svg>
"""

with open('assets/streak-stats.svg', 'w', encoding='utf-8') as f:
    f.write(svg_template)

print(f"Generated assets/streak-stats.svg successfully! Total: {total_contribs}, Current: {cur_streak} ({current_range}), Longest: {longest} ({longest_range})")

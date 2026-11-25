"""Refresh CTDG public portfolio graphic from unauthenticated GitHub REST data."""
import collections
import datetime
import html
import json
import pathlib
import urllib.request

OWNER = "colintandyonline"
ROOT = pathlib.Path(__file__).resolve().parents[1]
repos = []
for page in range(1, 101):
    url = f"https://api.github.com/users/{OWNER}/repos?type=owner&per_page=100&page={page}"
    request = urllib.request.Request(url, headers={"Accept":"application/vnd.github+json","User-Agent":"CTDG-public-portfolio"})
    with urllib.request.urlopen(request, timeout=30) as response:
        batch = json.load(response)
    if not isinstance(batch, list):
        raise RuntimeError("Unexpected GitHub response")
    repos.extend(batch)
    if len(batch) < 100:
        break
else:
    raise RuntimeError("Pagination incomplete")
repos = [r for r in repos if r["private"] is False and not r["archived"] and r["owner"]["login"].lower() == OWNER]
originals = [r for r in repos if not r["fork"]]
forks = [r for r in repos if r["fork"]]
languages = collections.Counter(r.get("language") or "Unclassified" for r in originals)
date = datetime.datetime.now(datetime.timezone.utc).strftime("%d %b %Y")
total = len(repos)
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="440" viewBox="0 0 960 440" role="img" aria-labelledby="title desc">',
'<title id="title">CTDG public engineering portfolio</title>',
f'<desc id="desc">{total} public repositories, {len(originals)} original repositories and {len(forks)} research forks. Primary languages are repository classifications, not code volume. Snapshot {date}.</desc>',
'<rect x="1" y="1" width="958" height="438" rx="20" fill="#0b192c" stroke="#254763"/>',
'<g font-family="Arial,sans-serif"><text x="30" y="35" fill="#45d6ec" font-size="12" font-weight="700" letter-spacing="2">CT DIGITAL GROUP / ENGINEERING</text>',
'<text x="30" y="74" fill="#f4f9ff" font-size="29" font-weight="700">Public engineering portfolio</text>',
f'<text x="930" y="35" text-anchor="end" fill="#a7c4db" font-size="12">{date} UTC</text>']
for x, number, label in [(30,total,"PUBLIC REPOSITORIES"),(336,len(originals),"ORIGINAL REPOSITORIES"),(642,len(forks),"UPSTREAM FORKS")]:
    parts.append(f'<rect x="{x}" y="100" width="288" height="83" rx="12" fill="#142b43" stroke="#254763"/><text x="{x+18}" y="142" fill="#65d9f4" font-size="32" font-weight="700">{number}</text><text x="{x+18}" y="165" fill="#b5cee0" font-size="12">{label}</text>')
parts.append('<rect x="30" y="200" width="420" height="195" rx="12" fill="#10253b" stroke="#254763"/><text x="50" y="230" fill="#edf6ff" font-size="16" font-weight="700">Repository composition</text>')
circ = 2 * 3.141592653589793 * 53
arc = circ * len(originals) / max(total,1)
parts.append(f'<circle cx="122" cy="307" r="53" fill="none" stroke="#2476ed" stroke-width="19"/><circle cx="122" cy="307" r="53" fill="none" stroke="#35dbec" stroke-width="19" stroke-dasharray="{arc:.3f} {circ:.3f}" transform="rotate(-90 122 307)"/><text x="122" y="314" fill="#fff" font-size="27" font-weight="700" text-anchor="middle">{total}</text>')
for y, color, label, count in [(290,"#35dbec","Original repositories",len(originals)),(330,"#2476ed","Upstream forks",len(forks))]:
    parts.append(f'<rect x="205" y="{y-10}" width="10" height="10" rx="2" fill="{color}"/><text x="225" y="{y}" fill="#d5e8f7" font-size="13">{label}</text><text x="430" y="{y}" text-anchor="end" fill="#fff" font-size="15">{count}</text>')
parts.append('<rect x="466" y="200" width="464" height="195" rx="12" fill="#10253b" stroke="#254763"/><text x="486" y="230" fill="#edf6ff" font-size="16" font-weight="700">Original repositories / primary language</text>')
ordered = languages.most_common()
if len(ordered) > 4:
    ordered = ordered[:3] + [("Other",sum(n for _,n in ordered[3:]))]
for i,(label,count) in enumerate(ordered):
    y=258+i*33
    width=270*count/max(len(originals),1)
    parts.append(f'<text x="486" y="{y}" fill="#d5e8f7" font-size="12">{html.escape(label)}</text><rect x="610" y="{y-10}" width="270" height="10" rx="5" fill="#203b55"/><rect x="610" y="{y-10}" width="{width:.2f}" height="10" rx="5" fill="#35dbec"/><text x="910" y="{y}" text-anchor="end" fill="#fff" font-size="12">{count}</text>')
parts.append('<text x="30" y="420" fill="#a7c4db" font-size="11">SOURCE: PUBLIC GITHUB REST API / NON-ARCHIVED OWNER REPOSITORIES / REPOSITORY COUNTS</text></g></svg>')
out=ROOT/"assets"/"ctdg-engineering-intelligence.svg"
out.write_text("\n".join(parts)+"\n",encoding="utf-8")
print(f"Public portfolio: {total} repositories, {len(originals)} originals, {len(forks)} forks")

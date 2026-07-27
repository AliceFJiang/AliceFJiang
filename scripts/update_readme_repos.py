import os
import re
import urllib.request
import json
from datetime import datetime, timezone

USERNAME = "AliceFJiang"
README = "README.md"
START = "<!-- REPO-LIST:START -->"
END = "<!-- REPO-LIST:END -->"

FOCUS_KEYWORDS = [
    ("ros", "ROS / robotics notes"),
    ("robot", "Robotics"),
    ("posture", "Computer vision / posture recognition"),
    ("vision", "Computer vision"),
    ("superconductivity", "Scientific ML / materials prediction"),
    ("temperature", "Scientific ML / prediction workflow"),
    ("notebook", "Learning notebooks"),
]


def guess_focus(repo):
    haystack = f"{repo.get('name', '')} {repo.get('description') or ''}".lower()
    for keyword, label in FOCUS_KEYWORDS:
        if keyword in haystack:
            return label
    if repo.get("language"):
        return f"{repo['language']} project"
    return "Project notes"


def fetch_repos():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-readme-updater",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&sort=updated&direction=desc"
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            batch = json.loads(response.read().decode("utf-8"))
        if not batch:
            break
        repos.extend(batch)
        page += 1

    return [repo for repo in repos if not repo.get("fork") and repo.get("name") != USERNAME]


def format_date(value):
    if not value:
        return ""
    dt = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%d")


def build_table(repos):
    rows = [
        "| Repository | Focus | Language | Stars | Last Updated |",
        "|---|---|---:|---:|---:|",
    ]
    for repo in repos[:8]:
        name = repo["name"]
        url = repo["html_url"]
        focus = guess_focus(repo)
        language = repo.get("language") or "-"
        stars = repo.get("stargazers_count", 0)
        updated = format_date(repo.get("updated_at"))
        rows.append(f"| [{name}]({url}) | {focus} | {language} | {stars} | {updated} |")
    return "\n".join(rows)


def main():
    with open(README, "r", encoding="utf-8") as f:
        readme = f.read()

    block = f"{START}\n{build_table(fetch_repos())}\n{END}"
    pattern = re.compile(f"{re.escape(START)}.*?{re.escape(END)}", re.DOTALL)
    updated = pattern.sub(block, readme)

    with open(README, "w", encoding="utf-8", newline="\n") as f:
        f.write(updated)


if __name__ == "__main__":
    main()

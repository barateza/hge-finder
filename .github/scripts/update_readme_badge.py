#!/usr/bin/env python3
"""
Usage:
  python update_readme_badge.py .github/coverage/coverage-badge.json README.md

Replaces the README badge area between these markers:
  <!-- COVERAGE_BADGE_START -->
  <!-- COVERAGE_BADGE_END -->

With a shields endpoint badge pointing to the JSON file. The script attempts to determine
the owner/repo from the GITHUB_REPOSITORY env var when run inside Actions. Otherwise,
it will leave a placeholder that you must edit.

Note: the badge URL points to the RAW file on the 'BADGE_BRANCH' (defaults to 'main').
"""
import sys
from pathlib import Path
import json
import os

def make_badge_markdown(repo, branch, json_path):
    raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{json_path}"
    badge_md = f"[![coverage](https://img.shields.io/endpoint?url={raw_url})](https://github.com/{repo}/actions)"
    return badge_md

def main():
    if len(sys.argv) < 3:
        print("Usage: update_readme_badge.py <badge-json-path> <readme-path>")
        sys.exit(2)
    badge_json = Path(sys.argv[1])
    readme = Path(sys.argv[2])
    if not badge_json.exists():
        print(f"Badge JSON {badge_json} not found")
        sys.exit(1)
    if not readme.exists():
        print(f"README {readme} not found")
        sys.exit(1)

    repo = os.environ.get("GITHUB_REPOSITORY", "")
    branch = os.environ.get("BADGE_BRANCH", "main")
    repo_display = repo if repo else "<OWNER>/<REPO>"
    json_rel_path = str(badge_json).lstrip("./")

    badge_md = make_badge_markdown(repo_display, branch, json_rel_path)

    text = readme.read_text()
    start = "<!-- COVERAGE_BADGE_START -->"
    end = "<!-- COVERAGE_BADGE_END -->"
    if start in text and end in text:
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        new_text = before + start + "\n" + badge_md + "\n" + end + after
        readme.write_text(new_text)
        print("README badge area updated between markers")
    else:
        print(f"Markers not found in README. Please add these markers and re-run:\n{start}\n{end}")
        print("Badge I would insert:")
        print(badge_md)
        sys.exit(1)

if __name__ == "__main__":
    main()
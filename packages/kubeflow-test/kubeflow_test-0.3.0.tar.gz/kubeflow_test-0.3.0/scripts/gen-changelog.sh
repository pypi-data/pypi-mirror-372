#!/bin/bash

set -e

REPO_NAME="kubeflow/sdk"
CHANGELOG_FILE="CHANGELOG.md"

while [[ $# -gt 0 ]]; do
  case $1 in
    --token=*)
      GITHUB_TOKEN="${1#*=}"
      shift
      ;;
    --version=*)
      TARGET_VERSION="${1#*=}"
      shift
      ;;
    --range=*)
      RELEASE_RANGE="${1#*=}"
      shift
      ;;
    -h|--help)
      echo "Usage: $0 --token=TOKEN [--version=VERSION | --range=FROM..TO]"
      exit 0
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "Error: GitHub token required. Use --token=TOKEN or set GITHUB_TOKEN env var"
    exit 1
fi

if [[ -n "$RELEASE_RANGE" ]]; then
    PREVIOUS_VERSION=$(echo "$RELEASE_RANGE" | cut -d'.' -f1)
    CURRENT_VERSION=$(echo "$RELEASE_RANGE" | cut -d'.' -f2)
elif [[ -n "$TARGET_VERSION" ]]; then
    PREVIOUS_VERSION=$(git describe --tags --abbrev=0 "$TARGET_VERSION^" 2>/dev/null || echo "")
    if [[ -z "$PREVIOUS_VERSION" ]]; then
        PREVIOUS_VERSION=$(git rev-list --max-parents=0 HEAD | head -1)
    fi
    CURRENT_VERSION="$TARGET_VERSION"
else
    echo "Error: Must specify --version or --range"
    exit 1
fi

TEMP_SCRIPT=$(mktemp -t changelog_gen.XXXXXX.py)
cat > "$TEMP_SCRIPT" << 'EOF'
import sys
import argparse
import subprocess
import re
from datetime import datetime

try:
    from github import Github
except ImportError:
    print("Error: PyGithub not available")
    sys.exit(1)

def categorize_pr(title):
    title_lower = title.lower().strip()
    match = re.match(r'^([a-z]+)(\([^)]+\))?: ', title_lower)
    if not match:
        return 'misc'

    pr_type = match.group(1)
    if pr_type in ['feat', 'fix', 'chore', 'revert']:
        return pr_type
    return 'misc'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--previous", required=True)
    parser.add_argument("--current", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    github_repo = Github(args.token).get_repo(args.repo)

    # Get commits in range
    if len(args.previous) == 40:  # Initial commit
        commits_output = subprocess.check_output(
            ['git', 'rev-list', '--reverse', f'{args.previous}..{args.current}'],
            text=True
        ).strip()
    else:
        commits_output = subprocess.check_output(
            ['git', 'rev-list', '--reverse', f'{args.previous}..{args.current}'],
            text=True
        ).strip()

    if not commits_output:
        print(f"No commits found between {args.previous} and {args.current}")
        return

    commit_shas = commits_output.split('\n')

    # Get release date
    latest_commit_info = subprocess.check_output(
        ['git', 'show', '-s', '--format=%ci', args.current],
        text=True
    ).strip()
    release_date = datetime.fromisoformat(latest_commit_info.split()[0]).strftime("%Y-%m-%d")

    # Determine release URL
    try:
        subprocess.check_output(['git', 'show-ref', '--tags', args.current], stderr=subprocess.DEVNULL)
        release_url = f"https://github.com/{args.repo}/releases/tag/{args.current}"
    except subprocess.CalledProcessError:
        release_url = f"https://github.com/{args.repo}/tree/{args.current}"

    # Collect PRs and categorize
    pr_categories = {
        'feat': [],
        'fix': [],
        'chore': [],
        'revert': [],
        'misc': []
    }
    pr_set = set()

    for commit_sha in commit_shas:
        try:
            commit = github_repo.get_commit(commit_sha)
            for pr in commit.get_pulls():
                if pr.number in pr_set:
                    continue
                pr_set.add(pr.number)

                category = categorize_pr(pr.title)
                pr_entry = f"- {pr.title} ([#{pr.number}]({pr.html_url})) by [@{pr.user.login}]({pr.user.html_url})"
                pr_categories[category].append(pr_entry)
        except Exception:
            continue

    # Generate changelog content
    changelog_content = [f"## [{args.current}]({release_url}) ({release_date})\n\n"]

    if pr_categories['feat']:
        changelog_content.extend([
            "### New Features\n\n",
            "\n".join(pr_categories['feat']) + "\n\n"
        ])

    if pr_categories['fix']:
        changelog_content.extend([
            "### Bug Fixes\n\n",
            "\n".join(pr_categories['fix']) + "\n\n"
        ])

    if pr_categories['chore']:
        changelog_content.extend([
            "### Maintenance\n\n",
            "\n".join(pr_categories['chore']) + "\n\n"
        ])

    if pr_categories['revert']:
        changelog_content.extend([
            "### Reverts\n\n",
            "\n".join(pr_categories['revert']) + "\n\n"
        ])

    if pr_categories['misc']:
        changelog_content.extend([
            "### Other Changes\n\n",
            "\n".join(pr_categories['misc']) + "\n\n"
        ])

    # Add comparison link if not first release
    if len(args.previous) != 40:
        comparison_url = f"https://github.com/{args.repo}/compare/{args.previous}...{args.current}"
        changelog_content.append(f"**Full Changelog**: {comparison_url}\n\n")

    full_changelog_text = ''.join(changelog_content)

    # Read existing changelog
    try:
        with open(args.output, "r") as f:
            existing_content = f.read()
    except FileNotFoundError:
        existing_content = "# Changelog\n\nAll notable changes to the Kubeflow SDK will be documented in this file.\n\n"

    # Insert new content
    lines = existing_content.split('\n')
    header_end = 0
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith('#') and not line.startswith('All notable'):
            header_end = i
            break
    else:
        header_end = len(lines)

    new_lines = lines[:header_end] + full_changelog_text.rstrip().split('\n') + [''] + lines[header_end:]

    # Write updated changelog
    with open(args.output, "w") as f:
        f.write('\n'.join(new_lines))

    print(f"Changelog updated: {len(pr_set)} PRs processed")

if __name__ == "__main__":
    main()
EOF

# Install and run
uvx --python-preference system --from PyGithub python "$TEMP_SCRIPT" \
    --token="$GITHUB_TOKEN" \
    --repo="$REPO_NAME" \
    --previous="$PREVIOUS_VERSION" \
    --current="$CURRENT_VERSION" \
    --output="$CHANGELOG_FILE"

# Clean up
rm "$TEMP_SCRIPT"

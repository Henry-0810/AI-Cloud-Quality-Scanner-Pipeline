import os
import json
import requests

SARIF_PATH = "sarif-artifacts/codeguru-results.sarif.json"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
API_URL = f"https://api.github.com/repos/henry-0810/{REPO}/issues"


def parse_codeguru_sarif(path):
    with open(path, "r") as f:
        sarif = json.load(f)

    parsed = []
    for run in sarif.get("runs", []):
        for result in run.get("results", []):
            file_path = result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
            start_line = result["locations"][0]["physicalLocation"]["region"]["startLine"]
            rule = result.get("ruleId", "N/A")
            level = result.get("level", "N/A")
            message = result["message"]["text"]

            parsed.append({
                "file": file_path,
                "line": start_line,
                "rule": rule,
                "level": level,
                "message": message,
            })
    return parsed


def format_markdown(findings):
    if not findings:
        return "✅ No CodeGuru Reviewer issues were found."

    md = ["### 🔍 CodeGuru Reviewer Findings\n"]
    grouped = {}

    for f in findings:
        grouped.setdefault(f["file"], []).append(f)

    for file, issues in grouped.items():
        md.append(f"#### 📄 File: `{file}`\n")
        for i in issues:
            md.append(
                f"- Line `{i['line']}` | **{i['level'].upper()}** | **{i['rule']}**\n"
                f"  > {i['message']}\n"
            )
        md.append("\n")

    return "\n".join(md)


def post_github_issue(title, body):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    data = {
        "title": title,
        "body": body
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 201:
        print("✅ GitHub issue created successfully.")
    else:
        print("❌ Failed to create GitHub issue:",
              response.status_code, response.text)


if __name__ == "__main__":
    if not os.path.exists(SARIF_PATH):
        print(f"❌ SARIF file not found at {SARIF_PATH}")
        exit(1)

    findings = parse_codeguru_sarif(SARIF_PATH)
    markdown = format_markdown(findings)
    post_github_issue("CodeGuru Reviewer Report", markdown)

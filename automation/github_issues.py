import os
import json
import requests

SARIF_PATH = "sarif-artifacts/codeguru-results.sarif.json"
SECURITY_JSON_PATH = "codeguru-security-results.json"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
API_URL = f"https://api.github.com/repos/{REPO}/issues"


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


def parse_codeguru_security(path):
    with open(path, "r") as f:
        findings = json.load(f)

    parsed = []
    for finding in findings:
        vuln = finding.get("vulnerability", {}).get("filePath", {})
        parsed.append({
            "file": vuln.get("path", "N/A"),
            "line": vuln.get("startLine", "?"),
            "title": finding.get("title", "Untitled"),
            "severity": finding.get("severity", "Medium"),
            "description": finding.get("description", ""),
            "recommendation": finding.get("remediation", {}).get("recommendation", {}).get("text", ""),
            "reference": finding.get("remediation", {}).get("recommendation", {}).get("url", "")
        })
    return parsed


def format_markdown(reviewer_findings, security_findings):
    md = ["## 🤖 AI-Powered Code Review Report\n"]

    # CodeGuru Reviewer Section
    md.append("### 🔍 CodeGuru Reviewer Findings\n")
    if not reviewer_findings:
        md.append("✅ No issues found by CodeGuru Reviewer.\n")
    else:
        grouped = {}
        for f in reviewer_findings:
            grouped.setdefault(f["file"], []).append(f)

        for file, issues in grouped.items():
            md.append(f"#### 📄 File: `{file}`")
            for i in issues:
                md.append(
                    f"- Line `{i['line']}` | **{i['level'].upper()}** | **{i['rule']}**\n"
                    f"  > {i['message']}"
                )
            md.append("")

    # CodeGuru Security Section
    md.append("\n---\n")
    md.append("### 🔐 CodeGuru Security Findings\n")
    if not security_findings:
        md.append("✅ No security vulnerabilities found.\n")
    else:
        grouped = {}
        for f in security_findings:
            grouped.setdefault(f["file"], []).append(f)

        for file, issues in grouped.items():
            md.append(f"#### 📄 File: `{file}`")
            for i in issues:
                md.append(
                    f"- Line `{i['line']}` | **{i['severity'].upper()}** | **{i['title']}**\n"
                    f"  > {i['description']}\n"
                    f"  👉 _{i['recommendation']}_\n"
                    f"  🔗 [Remediation]({i['reference']})\n"
                )
            md.append("")

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

    if not os.path.exists(SECURITY_JSON_PATH):
        print(f"❌ Security JSON file not found at {SECURITY_JSON_PATH}")
        exit(1)

    reviewer_findings = parse_codeguru_sarif(SARIF_PATH)
    security_findings = parse_codeguru_security(SECURITY_JSON_PATH)

    markdown = format_markdown(reviewer_findings, security_findings)
    post_github_issue(
        "🤖 AI Code Review Report (CodeGuru + Security)", markdown)

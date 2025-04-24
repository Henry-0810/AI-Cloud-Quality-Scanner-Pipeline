import os
import json
import requests

SARIF_PATH = "sarif-artifacts/codeguru-results.sarif.json"
SECURITY_JSON_PATH = "codeguru-security-results.json"
NLP_JSON_PATH = "nlp-results.json"

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


def parse_nlp_results(path):
    with open(path, "r") as f:
        findings = json.load(f)

    parsed = []
    for finding in findings:
        parsed.append({
            "file": finding.get("file", "N/A"),
            "line": finding.get("line", "?"),
            "comment": finding.get("comment", ""),
            "why": finding.get("why", ""),
            "suggestion": finding.get("suggestion", "")
        })
    return parsed


def format_markdown(reviewer_findings, security_findings, nlp_findings):
    md = ["## 🤖 AI-Powered Code Review Report\n"]

    # Generate summary counts
    reviewer_counts = count_by_severity(reviewer_findings, "level")
    security_counts = count_by_severity(security_findings, "severity")

    # Top summary section
    md.append("### 📊 Summary\n")
    md.append("| Category | Critical | High | Medium | Low | Info | Total |")
    md.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    md.append(f"| 🔍 CodeGuru | {reviewer_counts.get('critical', 0)} | {reviewer_counts.get('high', 0)} | {reviewer_counts.get('medium', 0)} | {reviewer_counts.get('low', 0)} | {reviewer_counts.get('info', 0)} | {len(reviewer_findings)} |")
    md.append(f"| 🔐 Security | {security_counts.get('critical', 0)} | {security_counts.get('high', 0)} | {security_counts.get('medium', 0)} | {security_counts.get('low', 0)} | {security_counts.get('info', 0)} | {len(security_findings)} |")
    md.append(
        f"| 💬 NLP Comments | - | - | - | - | {len(nlp_findings)} | {len(nlp_findings)} |")
    md.append("\n")

    # Prioritized findings section
    md.append("### ⚠️ Top Priority Findings\n")
    add_top_findings(md, reviewer_findings, security_findings, 3)

    # CodeGuru Reviewer Section - collapsible
    md.append("<details>")
    md.append(
        f"<summary><h3>🔍 CodeGuru Reviewer Findings ({len(reviewer_findings)})</h3></summary>\n")

    if not reviewer_findings:
        md.append("✅ No issues found by CodeGuru Reviewer.\n")
    else:
        # Group by severity
        severity_groups = group_by_severity(reviewer_findings, "level")

        # Display by severity levels
        for severity in ["critical", "high", "medium", "low", "info"]:
            findings = severity_groups.get(severity, [])
            if findings:
                severity_emoji = get_severity_emoji(severity)
                md.append(
                    f"#### {severity_emoji} {severity.upper()} ({len(findings)})\n")

                # If many findings of this severity, make them collapsible by file
                if len(findings) > 5 and severity not in ["critical", "high"]:
                    # Group by file
                    file_groups = {}
                    for f in findings:
                        file_groups.setdefault(f["file"], []).append(f)

                    for file, issues in file_groups.items():
                        md.append(
                            f"<details><summary>📄 <code>{file}</code> ({len(issues)})</summary>\n")
                        for i in issues:
                            md.append(
                                f"- Line `{i['line']}` | **{i['rule']}**\n"
                                f"  > {i['message']}"
                            )
                        md.append("</details>\n")
                else:
                    # Display directly for important or few findings
                    for f in findings:
                        md.append(
                            f"- **{f['file']}** (Line `{f['line']}`) | **{f['rule']}**\n"
                            f"  > {f['message']}"
                        )
                md.append("")

    md.append("</details>\n")

    # Security Section - collapsible
    md.append("<details>")
    md.append(
        f"<summary><h3>🔐 CodeGuru Security Findings ({len(security_findings)})</h3></summary>\n")

    if not security_findings:
        md.append("✅ No security vulnerabilities found.\n")
    else:
        # Group by severity
        severity_groups = group_by_severity(security_findings, "severity")

        # Display by severity levels
        for severity in ["critical", "high", "medium", "low", "info"]:
            findings = severity_groups.get(severity, [])
            if findings:
                severity_emoji = get_severity_emoji(severity)
                md.append(
                    f"#### {severity_emoji} {severity.upper()} ({len(findings)})\n")

                for i in findings:
                    md.append(
                        f"- **{i['file']}** (Line `{i['line']}`) | **{i['title']}**\n"
                        f"  > {i['description']}\n"
                        f"  👉 _{i['recommendation']}_"
                    )
                    if i['reference']:
                        md.append(f"  🔗 [Remediation]({i['reference']})\n")
                    else:
                        md.append("\n")
                md.append("")

    md.append("</details>\n")

    # NLP Analysis Section - collapsible
    md.append("<details>")
    md.append(
        f"<summary><h3>💬 NLP Comment Insights ({len(nlp_findings)})</h3></summary>\n")

    if not nlp_findings:
        md.append("✅ No bad comments detected by NLP analysis.\n")
    else:
        grouped = {}
        for f in nlp_findings:
            grouped.setdefault(f["file"], []).append(f)

        for file, issues in grouped.items():
            md.append(
                f"<details><summary>📄 <code>{file}</code> ({len(issues)})</summary>\n")
            for i in issues:
                md.append(
                    f"- Line `{i['line']}` | **Comment:** {i['comment']}\n"
                    f"  > {i['why']}\n"
                    f"  👉 _{i['suggestion']}_\n"
                )
            md.append("</details>\n")

    md.append("</details>\n")

    return "\n".join(md)

# Helper functions


def count_by_severity(findings, severity_key):
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        severity = f.get(severity_key, "").lower()
        if severity in ["critical", "error", "warning"]:
            counts["critical"] += 1
        elif severity == "high":
            counts["high"] += 1
        elif severity in ["medium", "note"]:
            counts["medium"] += 1
        elif severity == "low":
            counts["low"] += 1
        else:
            counts["info"] += 1
    return counts


def group_by_severity(findings, severity_key):
    groups = {"critical": [], "high": [], "medium": [], "low": [], "info": []}
    for f in findings:
        severity = f.get(severity_key, "").lower()
        if severity in ["critical", "error", "warning"]:
            groups["critical"].append(f)
        elif severity == "high":
            groups["high"].append(f)
        elif severity in ["medium", "note"]:
            groups["medium"].append(f)
        elif severity == "low":
            groups["low"].append(f)
        else:
            groups["info"].append(f)
    return groups


def get_severity_emoji(severity):
    if severity == "critical":
        return "🔴"
    elif severity == "high":
        return "🟠"
    elif severity == "medium":
        return "🟡"
    elif severity == "low":
        return "🟢"
    else:
        return "📝"


def add_top_findings(md, reviewer_findings, security_findings, limit=3):
    # Combine and sort all critical and high findings
    top_issues = []

    # Add reviewer findings
    reviewer_groups = group_by_severity(reviewer_findings, "level")
    for severity in ["critical", "high"]:
        for finding in reviewer_groups.get(severity, []):
            top_issues.append({
                "type": "CodeGuru",
                "file": finding["file"],
                "line": finding["line"],
                "title": finding["rule"],
                "message": finding["message"],
                "severity": severity
            })

    # Add security findings
    security_groups = group_by_severity(security_findings, "severity")
    for severity in ["critical", "high"]:
        for finding in security_groups.get(severity, []):
            top_issues.append({
                "type": "Security",
                "file": finding["file"],
                "line": finding["line"],
                "title": finding["title"],
                "message": finding["description"],
                "recommendation": finding["recommendation"],
                "severity": severity
            })

    # Sort by severity (critical first)
    top_issues.sort(key=lambda x: 0 if x["severity"] == "critical" else 1)

    # Display top findings
    if top_issues:
        for i, issue in enumerate(top_issues[:limit]):
            severity_emoji = get_severity_emoji(issue["severity"])
            md.append(
                f"{i+1}. {severity_emoji} **[{issue['type']}]** {issue['file']} (Line {issue['line']})")
            md.append(f"   **{issue['title']}**")
            md.append(f"   > {issue['message']}")
            if issue.get("recommendation"):
                md.append(f"   👉 {issue['recommendation']}")
            md.append("")
    else:
        md.append("✅ No critical or high priority issues found.")

    md.append("")


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
    nlp_findings = parse_nlp_results(NLP_JSON_PATH)

    markdown = format_markdown(
        reviewer_findings, security_findings, nlp_findings)
    post_github_issue(
        "🤖 AI Code Review Report (CodeGuru + Security)", markdown)

import boto3
import os
import time
import json
import zipfile
import requests
from pathlib import Path

# === Configuration ===
SOURCE_DIR = "."  # Folder to scan
ZIP_FILE = "source.zip"
RESULT_FILE = "codeguru-security-results.json"
REGION = "us-east-1"

# === AWS Client ===
codeguru = boto3.client("codeguru-security", region_name=REGION)


def zip_source(directory: str, output: str):
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in Path(directory).rglob("*"):
            if path.is_file() and "venv" not in str(path):
                zf.write(path, arcname=path.relative_to(directory))
    print(f"Zipped source to {output}")


def get_upload_url(scan_name: str) -> tuple[str, str, dict]:
    response = codeguru.create_upload_url(scanName=scan_name)
    upload_url = response["s3Url"]
    code_artifact_id = response["codeArtifactId"]
    headers = response["requestHeaders"]
    print(f"Got upload URL and artifact ID: {code_artifact_id}")
    return upload_url, code_artifact_id, headers


def upload_to_presigned_url(upload_url: str, zip_file: str, headers: dict):
    with open(zip_file, "rb") as f:
        response = requests.put(upload_url, data=f, headers=headers)
    if response.status_code != 200:
        raise Exception(
            f"Upload failed: {response.status_code} - {response.text}")
    print("Uploaded ZIP to CodeGuru via pre-signed URL")


def start_scan(code_artifact_id: str, scan_name: str) -> str:
    response = codeguru.create_scan(
        scanName=scan_name,
        resourceId={"codeArtifactId": code_artifact_id},
        scanType="Standard"
    )
    print(f"Scan started with name: {scan_name}")
    return scan_name


def wait_for_results(scan_name: str) -> dict:
    print("Waiting for scan to complete...")
    while True:
        response = codeguru.get_scan(scanName=scan_name)
        state = response["scanState"]
        if state == "Completed":
            print("Scan completed")
            return response
        elif state in ["Failed", "Canceled"]:
            raise Exception(f"Scan failed or was canceled: {state}")
        time.sleep(5)


def fetch_findings(scan_name: str) -> list:
    paginator = codeguru.get_paginator("list_findings")
    findings = []
    for page in paginator.paginate(scanName=scan_name):
        findings.extend(page["findings"])
    print(f"Found {len(findings)} vulnerabilities")
    return findings


def main():
    zip_source(SOURCE_DIR, ZIP_FILE)
    scan_name = f"ai-code-security-scan-{int(time.time())}"
    upload_url, code_artifact_id, headers = get_upload_url(scan_name)
    upload_to_presigned_url(upload_url, ZIP_FILE, headers)
    start_scan(code_artifact_id, scan_name)
    wait_for_results(scan_name)
    findings = fetch_findings(scan_name)

    with open(RESULT_FILE, "w") as f:
        json.dump(findings, f, indent=2)
    print(f"Saved findings to {RESULT_FILE}")


if __name__ == "__main__":
    main()

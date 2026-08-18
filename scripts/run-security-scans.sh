#!/usr/bin/env bash
set -euo pipefail

command -v semgrep >/dev/null || { echo "Semgrep is required"; exit 1; }
command -v trivy >/dev/null || { echo "Trivy is required"; exit 1; }
command -v docker >/dev/null || { echo "Docker is required"; exit 1; }
command -v npm >/dev/null || { echo "npm is required"; exit 1; }

mkdir -p reports

semgrep scan --config auto --json --output reports/sast.semgrep.json app notify

(cd notify && npm install)

trivy fs --scanners vuln --format json --output reports/sca.trivy.json .
docker build -t vulntracker-api:1.0.0 .
trivy image --format json --output reports/container.trivy.json vulntracker-api:1.0.0
trivy config --format json --output reports/iac.trivy.json helm/

echo "Security reports generated under reports/"

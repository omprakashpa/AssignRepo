# Security Automation CI/CD Pipeline

## Overview

This project demonstrates a security-focused CI/CD pipeline that integrates automated security testing into the software development lifecycle.

The pipeline performs application testing and multiple security scans, including:

- Static Application Security Testing (SAST)
- Software Composition Analysis (SCA)
- Container/Image Vulnerability Scanning
- Infrastructure as Code (IaC) Scanning

Security scan results are generated as JSON reports and stored under the `reports/` directory. Security assessment findings, remediation recommendations, and executive-level risk summaries are documented under the `docs/` directory.

---

## Project Structure

```text
.
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   └── models.py
│
├── docs/
│   ├── executive-summary.md
│   ├── findings.md
│   └── remediation-plan.md
│
├── helm/
│   └── vulntracker/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│
├── reports/
│   ├── container.trivy.json
│   ├── iac.trivy.json
│   ├── sast.semgrep.json
│   └── sca.trivy.json
│
├── scripts/
│   ├── run-security-scans.ps1
│   └── run-security-scans.sh
│
├── tests/
│
├── Dockerfile
├── requirements.txt
├── package.json
└── README.md

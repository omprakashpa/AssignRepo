# Executive Summary

## 1. Overview

This project demonstrates an automated DevSecOps security pipeline that integrates security testing into the software development lifecycle.

The pipeline performs multiple security checks across application source code, third-party dependencies, container images, and Infrastructure-as-Code (IaC).

The objective is to identify security issues early in the development process and provide actionable remediation guidance.

---

## 2. Security Controls Implemented

The project includes the following security controls:

| Security Control | Tool | Purpose |
|---|---|---|
| SAST | Semgrep | Identify security issues in application source code |
| SCA | Trivy | Identify vulnerable third-party dependencies |
| Container Scanning | Trivy | Identify vulnerabilities in container images |
| IaC Scanning | Trivy | Identify security misconfigurations in infrastructure configuration |

Security scan results are generated as raw JSON reports and stored under:

```text
reports/

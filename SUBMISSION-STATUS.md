# Submission Status

This package contains the implementation, remediation, Dockerfile, Helm chart, tests, CI workflow, and documentation for the take-home assignment.

The four JSON files under `reports/` are intentionally marked `NOT_RUN` because raw scanner output must be produced by the actual selected tools. They must not be represented as genuine scan results without running the tools. The GitHub Actions workflow is configured to generate fresh reports on CI.

Before final submission, replace the four `NOT_RUN` files with actual JSON output from:
- Semgrep (SAST)
- Trivy filesystem vulnerability scan (SCA)
- Trivy image scan (container)
- Trivy config scan (IaC)

Then confirm the CI workflow is green.

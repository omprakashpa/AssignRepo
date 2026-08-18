# VulnTracker — Security Automation Take-Home

This repository contains the completed application changes, security remediation, containerization and Helm deployment artifacts for the assignment.

## What was implemented

- Shared report links with 24-hour expiration.
- Cryptographically random share tokens; only the SHA-256 token hash is stored.
- Optional bcrypt password protection.
- Ownership checks before creating a share link.
- Public shared-report response excludes the internal `owner_id`.
- SQL parameter binding and owner scoping for search.
- Scan retrieval is owner-scoped.
- JWT validation accepts only the configured algorithm.
- Passwords removed from logs.
- Explicit CORS allow-list.
- Generic error responses without traceback disclosure.
- Non-root Docker image with a health check.
- Helm deployment with external secret retrieval, resource limits, security context and restrictive ingress.
- Updated Python tests for the new feature and security boundaries.

## Assumptions

The share URL is generated from the incoming request host using FastAPI's `request.base_url`, as permitted by the assignment. In a production deployment, trusted proxy/header configuration must be used so an untrusted `Host` header cannot influence generated links.

The prototype continues to use SQLite. A production deployment should use a managed database.

The notification service API interface is unchanged. Its hardcoded outbound service key was moved to an environment variable as a small security hardening change; its unauthenticated administrative endpoints remain a documented residual risk.

## Local setup

### Python API

Python 3.11 is required by the assignment.

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd app
uvicorn main:app --reload
```

Linux/macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd app
uvicorn main:app --reload
```

API: `http://localhost:8000`

Swagger UI: `http://localhost:8000/docs`

For local development, the application generates an ephemeral JWT signing key if `SECRET_KEY` is not set. For production:

```text
APP_ENV=production
SECRET_KEY=<value-from-secret-manager>
```

Never commit the production secret.

### Notification service

```bash
cd notify
npm install
npm start
```

Service: `http://localhost:3001`

## Tests

From the repository root:

```bash
pytest tests/ -v
```

Notification tests:

```bash
cd notify
npm install
npm test
```

## Shared report API

### Create a share link

Authenticated request:

```http
POST /scans/{scan_id}/share
Authorization: Bearer <access-token>
Content-Type: application/json
```

Without password:

```json
{}
```

With password:

```json
{
  "password": "a-strong-share-password"
}
```

Response:

```json
{
  "share_url": "http://localhost:8000/share/<random-token>"
}
```

The raw token is 32 random bytes encoded with URL-safe base64. Only its SHA-256 hash is persisted.

### Access a shared report

```http
GET /share/<token>
```

For password-protected links:

```http
GET /share/<token>?password=a-strong-share-password
```

Links expire 24 hours after creation. Public responses use `Cache-Control: no-store` and do not expose the internal owner ID.

## Docker

Build:

```bash
docker build -t vulntracker-api:1.0.0 .
```

Run:

```bash
docker run --rm -p 8000:8000 -e SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" vulntracker-api:1.0.0
```

Windows PowerShell:

```powershell
$secret = python -c "import secrets; print(secrets.token_urlsafe(32))"
docker run --rm -p 8000:8000 -e SECRET_KEY=$secret vulntracker-api:1.0.0
```

Health check:

```text
http://localhost:8000/health
```

The image uses an exact Python 3.11.15 slim Bookworm tag plus a pinned image digest, runs as a non-root user, disables bytecode writes for a read-only root filesystem, and includes a Python-based `HEALTHCHECK`.

## Helm

The chart is under:

```text
helm/vulntracker/
```

It expects the External Secrets Operator and an existing AWS Secrets Manager secret. The secret store and remote secret name are configurable in `values.yaml`.

The chart uses:

- `ClusterIP` service by default.
- Optional Ingress, disabled by default.
- ExternalSecret for `SECRET_KEY`.
- IRSA-compatible service-account annotation.
- `runAsNonRoot`.
- `allowPrivilegeEscalation: false`.
- All Linux capabilities dropped.
- Read-only root filesystem.
- Resource requests and limits.
- NetworkPolicy restricting inbound traffic to the configured ingress-controller namespace.

Example:

```bash
helm upgrade --install vulntracker ./helm/vulntracker \
  --set externalSecret.remoteKey=prod/vulntracker/api
```

Before production use, review the AWS IAM policy so the service account can read only the required secret.

## Required security scans

The assignment requires four raw JSON reports. They must be generated in the environment where Docker and the selected security tools are available.

Recommended tools:

| Category | Tool | Command |
|---|---|---|
| SAST | Semgrep | `semgrep scan --config auto --json --output reports/sast.semgrep.json app notify` |
| SCA | Trivy filesystem | `trivy fs --scanners vuln --format json --output reports/sca.trivy.json .` |
| Container | Trivy image | `trivy image --format json --output reports/container.trivy.json vulntracker-api:1.0.0` |
| IaC | Trivy config | `trivy config --format json --output reports/iac.trivy.json helm/` |

Run the IaC scan only after the Helm chart is complete.

A Windows PowerShell helper is provided:

```powershell
.\scripts
un-security-scans.ps1
```

It builds the image and runs the four scans. The script intentionally stops if a required command is missing.

### Important

The solution pack was assembled in an environment without Docker and external package/tool network access. Therefore the four JSON files in the pack are marked `NOT_RUN` placeholders rather than fabricated scanner output. Run the commands above and replace those placeholders before submission.

## Documentation

- `docs/findings.md` — prioritised security findings and business impact.
- `docs/remediation-plan.md` — completed fixes and deferred-risk rationale.
- `docs/executive-summary.md` — CISO-oriented summary.

## CI

The workflow runs:

- Python tests.
- Node.js tests.
- Semgrep SAST.
- Trivy filesystem SCA.
- Docker build and Trivy image scan.
- Trivy IaC scan.

Security report artifacts are uploaded for review. CI failure thresholds should be reviewed after the first clean scan so that known baseline findings can be handled intentionally rather than hidden.

## Submission checklist

1. Create a fresh GitHub repository; do not fork the assignment repository.
2. Copy this solution into the fresh repository.
3. Run Python and Node tests locally.
4. Build the Docker image and verify `/health`.
5. Run all four scans and replace the `NOT_RUN` report placeholders.
6. Review `docs/findings.md` against the actual scanner output.
7. Confirm CI is green.
8. Rotate any credentials that were present in the original public starter repository if this were a real environment.

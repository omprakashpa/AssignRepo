# Security Findings

## Assessment scope

The assessment covers the FastAPI service, the notification service, the new shared-report feature, the container build, and the Helm deployment artifacts.

Severity is an application-specific risk assessment, not a direct copy of scanner severity. The highest priority was given to issues that could disclose vulnerability records, bypass authentication/authorization, expose credentials, or allow attacker-controlled network requests.

> **Important execution note:** the solution pack was assembled without network/Docker access in the build environment. The four required raw scanner reports therefore cannot be truthfully represented as completed scan output here. Run the commands in `scripts/run-security-scans.ps1` (or the equivalent README commands) in your environment after building the image and Helm chart. Do not submit placeholder scan output as if it were tool-generated.

## Prioritised findings

| ID | Finding | Source / type | Severity | Business impact | Location | Status |
|---|---|---|---|---|---|---|
| F-01 | Hardcoded JWT signing key and database credentials | Manual + SAST | Critical | Anyone obtaining repository contents can recover credentials or forge application tokens. The repository is public, so the values must be treated as exposed. | Starter `app/config.py` | Fixed in code; rotate exposed values in any real environment |
| F-02 | SQL injection in scan search | Manual + SAST | High | A malicious authenticated user could alter the search query and potentially read data outside the intended search operation. | Starter `app/database.py` | Fixed |
| F-03 | JWT accepts the `none` algorithm | Manual + SAST | High | Weak token validation can undermine the API's authentication boundary. | Starter `app/auth.py` | Fixed |
| F-04 | Passwords written to application logs | Manual + SAST | High | Credentials can leak into log aggregation, SIEM, backups, or developer tooling. | Starter `app/main.py` | Fixed |
| F-05 | Cross-user access to a scan by ID | Manual | High | A user who knows another scan ID could retrieve another user's vulnerability record. | Starter `app/main.py` | Fixed |
| F-06 | Cross-user search results | Manual | High | The search endpoint could return vulnerability records belonging to other users. | Starter `app/database.py` / `app/main.py` | Fixed |
| F-07 | Arbitrary-origin CORS with credentials | Manual | High | A malicious web origin could make authenticated browser requests if a victim's credentials are accepted by the browser. | Starter `app/main.py` | Fixed |
| F-08 | Detailed exception responses expose tracebacks | Manual + SAST | Medium | Internal paths, exception types and implementation details can be disclosed to API callers. | Starter `app/main.py` | Fixed |
| F-09 | Public notification endpoints have no authentication | Manual | High | If the notification service is reachable beyond a trusted private network, attackers could register arbitrary webhook URLs and cause the service to make outbound requests, creating an SSRF-style risk, as well as trigger notifications or delete registrations. | Starter `notify/src/index.js` | Deferred; deployment network isolation is the compensating control |
| F-10 | Hardcoded notification service key | Manual + SAST | High | The key can be recovered from repository contents and reused against downstream webhook calls. | Starter `notify/src/config.js` | Fixed by moving the key to an environment variable; rotate the original exposed value |
| F-11 | Detailed notification-service error responses | Manual | Medium | Internal error details can expose implementation information to callers. | Starter `notify/src/index.js` | Fixed |
| F-12 | Legacy third-party dependencies | SCA | High/Medium depending on actual report | Known dependency vulnerabilities can become remotely exploitable through the API or notification service. | Starter dependency manifests | Deferred until compatibility-tested upgrades; use the generated SCA report for exact CVEs |
| F-13 | Container vulnerabilities/misconfiguration | Container scan | To be confirmed from generated report | OS or Python package vulnerabilities increase the impact of a compromised application process. | Final image | Re-run scan after build |
| F-14 | Helm configuration findings | IaC scan | To be confirmed from generated report | Excessive privileges, exposed services or weak pod settings could expand the blast radius of a compromise. | `helm/` | Hardened by design; re-run scan after chart rendering |

## Security design of the shared-report feature

The new feature uses a 256-bit random URL-safe token and stores only a SHA-256 hash of that token. The raw token is returned once in the generated URL. Each token expires 24 hours after creation.

Optional passwords are stored as bcrypt hashes. The share endpoint is public by design, but it returns a reduced representation that excludes the internal `owner_id`. The link-creation endpoint requires authentication and verifies that the requesting user owns the scan.

The public response also sends `Cache-Control: no-store` and `Referrer-Policy: no-referrer` to reduce accidental caching and referrer leakage.

## Tool choices

- **SAST:** Semgrep
- **SCA:** pip-audit for Python and npm audit for Node.js; the JSON reports are consolidated for review
- **Container:** Trivy image scan
- **IaC:** Trivy config scan against the Helm chart

These tools were selected because they are open-source/free to use, scriptable in CI, and produce machine-readable output.

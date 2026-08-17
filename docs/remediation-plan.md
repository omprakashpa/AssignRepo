# Remediation Plan

## Completed

### F-01 — Hardcoded application credentials

The application no longer embeds a static JWT secret. `SECRET_KEY` is read from the environment. In development, an ephemeral key is generated so a developer can run the prototype without committing a credential. Production startup fails when `APP_ENV=production` and `SECRET_KEY` is absent.

**Residual action:** the values present in the original public repository must be considered compromised. In a real environment, rotate the JWT signing key and any database credentials immediately.

### F-02 — SQL injection

Search now uses a bound SQL parameter and restricts results to the authenticated user's records. Wildcards are escaped so the search term cannot alter the SQL expression.

### F-03 — JWT `none` algorithm

Token decoding now accepts only the configured HS256 algorithm.

### F-04 — Password logging

Login logs contain the username only. Password values are never logged.

### F-05/F-06 — Broken object-level authorization

Scan retrieval and search are scoped to the authenticated user's `owner_id`. Share-link creation uses the same ownership check.

### F-07 — CORS

The application now uses an explicit allow-list from `ALLOWED_ORIGINS` instead of reflecting arbitrary origins. The default is limited to the local prototype origin.

### F-08 — Exception disclosure

Unhandled exceptions are logged server-side while callers receive a generic error message without a traceback.

### F-11 — Notification-service error disclosure

The notification service now returns a generic error response while logging the detailed exception server-side.

## Deferred risks

### F-09 — Notification service authorization

The notification service exposes webhook registration, listing, deletion and event-triggering endpoints without application-level authentication. The assignment states that the notification service requires no changes, so the solution keeps it unchanged.

**Residual risk:** if port 3001 is reachable from an untrusted network, an attacker could manipulate webhook registrations or trigger outbound requests.

**Compensating controls:** the Helm deployment for the API uses a private `ClusterIP` service and a restrictive ingress policy. In a real deployment, the notification service should be isolated in a private namespace/network segment and authenticated with a service-to-service credential.

**Effort:** low to medium. Add service authentication, validate caller identity, and add tests.

### F-10 — Notification service key

The notification service now reads `SERVICE_KEY` from the runtime environment and omits the header when no key is configured. The original value in the public starter repository must still be treated as exposed and rotated in a real environment.

**Residual risk:** the notification endpoint itself still does not authenticate callers, so the outbound service key alone is not an authorization boundary.

**Compensating controls:** keep the notification service private and use authenticated service-to-service communication in production.

**Effort:** low to medium. Add caller authentication and rotate the original key.

### F-11 — Dependency upgrades

Dependency upgrades were not blindly applied because a take-home should not trade one security issue for untested breaking changes. The exact vulnerable packages and fixed versions must come from the generated SCA reports.

**Residual risk:** known vulnerabilities remain until the affected packages are upgraded.

**Compensating controls:** container isolation, restricted ingress, non-root execution, CI scanning, and dependency monitoring.

**Effort:** medium. Upgrade direct dependencies, regenerate lock files where applicable, run both test suites, rebuild the image and repeat the scans.

### F-12 — Container findings

The final image must be scanned after the Docker build. Any remaining high/critical finding should be triaged against reachability, exploit maturity, package role, and available fixed versions.

### F-13 — IaC findings

The Helm chart is hardened with non-root execution, dropped Linux capabilities, no privilege escalation, read-only root filesystem, resource limits, a private service, and restricted ingress. Any scanner finding that remains should be assessed after Helm rendering because some scanners report on templates differently from rendered manifests.

# Executive Summary

## Overall posture

Before the assessment, the service had several weaknesses that could allow an authenticated user to access another user's vulnerability information, manipulate database queries, expose credentials through source code or logs, or weaken authentication controls. The application also lacked hardened deployment controls. After the assessment, the API's authentication and ownership checks were strengthened, the new sharing capability was designed around short-lived high-entropy links, sensitive values were removed from application source, and the deployment artifacts enforce non-root execution, restricted ingress and resource boundaries.

## Top three residual risks

### 1. Notification service trust boundary

The notification service remains an internal prototype and does not authenticate administrative webhook operations. It is intentionally outside the code changes because the assignment says no changes are required there.

**Why it remains:** changing its API contract could exceed the assignment scope.

**Business risk:** if the service is exposed, an attacker could influence where vulnerability events are sent.

**Next step:** put the service on a private network and add authenticated service-to-service requests.

### 2. Dependency vulnerabilities

The starter dependencies are deliberately old and may contain known security issues.

**Why it remains:** upgrading dependencies without compatibility testing can introduce application failures.

**Business risk:** a known vulnerable library may provide an attacker with a path into the application.

**Next step:** upgrade to supported versions, run regression tests, rebuild the image and enforce high/critical SCA gates in CI.

### 3. Prototype data store and secret-management integration

The application still uses a local SQLite database for the prototype. The Helm deployment demonstrates external secret retrieval for the application signing key, but a production service would require a managed database with backups, encryption, access controls and a complete secret lifecycle.

**Why it remains:** the assignment focuses on security automation and deployment artifacts rather than a full production data-platform migration.

**Business risk:** local storage does not provide the durability, availability and operational controls expected for customer vulnerability data.

**Next step:** move to a managed database, encrypt data in transit and at rest, use workload identity for secret access, and establish backup/restore and key-rotation procedures.

## Recommended next steps

1. Rotate every credential present in the original public starter repository, including the notification-service key.
2. Upgrade and lock supported dependency versions after regression testing.
3. Add authenticated service-to-service communication for the notification component.
4. Deploy the API behind a managed ingress/WAF with TLS and rate limiting.
5. Add audit logging for sharing, authentication and administrative actions.
6. Make high/critical security gates mandatory in CI once false-positive handling is agreed.
7. Move the database to a managed production service and test backup/restore procedures.

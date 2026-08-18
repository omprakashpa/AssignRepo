# Security Findings

## Assessment Overview

The repository was assessed using four automated security scanning categories:

- SAST — Semgrep
- SCA — Trivy dependency scanning
- Container Image Scanning — Trivy
- IaC Scanning — Trivy

Findings were prioritized using scanner severity, CVSS where available, exploitability, affected functionality, potential business impact, and manual review.

---

## Prioritized Findings

### F-001 — python-multipart Path Traversal / Arbitrary File Write

| Field | Details |
|---|---|
| Priority | P1 — High |
| Severity | High |
| Scanner | Trivy SCA / Container |
| Component | `python-multipart` |
| Installed Version | `0.0.6` |
| Fixed Version | `0.0.22` |
| CVE | CVE-2026-24486 |
| CWE | CWE-22 |
| CVSS | 8.6 |
| Status | Confirmed scanner finding |
| Source | GitHub Security Advisory |

#### Description

The application contains a vulnerable version of `python-multipart`.

The vulnerability is a path traversal issue that can allow arbitrary file writes when the vulnerable upload configuration uses `UPLOAD_DIR` together with `UPLOAD_KEEP_FILENAME=True`.

An attacker may be able to construct a malicious filename containing path traversal sequences and cause an uploaded file to be written outside the intended upload directory.

#### Security Impact

Successful exploitation could allow an attacker to write files to arbitrary filesystem locations accessible to the application process.

Depending on filesystem permissions and application behavior, this could potentially result in:

- Application compromise
- Modification of application/configuration files
- Further code execution opportunities
- Integrity impact

#### Remediation

Upgrade `python-multipart` to at least:

`0.0.22`

The current scanner also identifies later vulnerabilities affecting this package, therefore upgrading to a current supported version should be preferred rather than stopping at the minimum patched version.

As a temporary mitigation, avoid using:

`UPLOAD_KEEP_FILENAME=True`

with user-controlled filenames.

---

### F-002 — python-multipart Denial of Service via Multipart Header Parsing

| Field | Details |
|---|---|
| Priority | P1 — High |
| Severity | High |
| Scanner | Trivy SCA / Container |
| Component | `python-multipart` |
| Installed Version | `0.0.6` |
| Fixed Version | `0.0.27` |
| CVE | CVE-2026-42561 |
| CWE | CWE-770, CWE-606 |
| CVSS | 7.5 |
| Status | Confirmed scanner finding |

#### Description

The installed `python-multipart` version does not limit the number or size of multipart part headers sufficiently.

An attacker can submit specially crafted multipart requests containing excessive or very large headers, causing excessive CPU consumption during parsing.

#### Security Impact

An unauthenticated attacker could potentially consume application CPU resources and degrade service availability.

Potential impact includes:

- Increased CPU utilization
- Request processing delays
- Worker exhaustion
- Application unavailability

#### Remediation

Upgrade `python-multipart` to at least:

`0.0.27`

Because multiple vulnerabilities affect the currently installed `0.0.6`, upgrading to a current supported version is preferable.

---

### F-003 — python-multipart Denial of Service via Crafted Form-URLencoded Requests

| Field | Details |
|---|---|
| Priority | P1 — High |
| Severity | High |
| Scanner | Trivy SCA / Container |
| Component | `python-multipart` |
| Installed Version | `0.0.6` |
| Fixed Version | `0.0.30` |
| CVE | CVE-2026-53539 |
| CWE | CWE-400, CWE-407 |
| CVSS | 7.5 |
| Status | Confirmed scanner finding |

#### Description

The installed version of `python-multipart` is vulnerable to inefficient processing of specially crafted `application/x-www-form-urlencoded` requests.

A malicious request containing many semicolon-separated fields can cause excessive CPU consumption during parsing.

#### Security Impact

An attacker could potentially send a relatively small number of crafted requests and consume application worker resources.

Potential impact includes:

- CPU exhaustion
- Worker exhaustion
- Increased response latency
- Denial of service

#### Remediation

Upgrade `python-multipart` to at least:

`0.0.30`

A single upgrade to a current supported version should be preferred because the installed version is affected by multiple vulnerabilities.

---

### F-004 — Starlette Multipart Form Denial of Service

| Field | Details |
|---|---|
| Priority | P1 — High |
| Severity | High |
| Scanner | Trivy SCA / Container |
| Component | `starlette` |
| Installed Version | `0.27.0` |
| Fixed Version | `0.40.0` |
| CVE | CVE-2024-47874 |
| CWE | CWE-770 |
| CVSS | 8.7 (CVSS v4), 7.5/8.7 depending on source/vector |
| Status | Confirmed scanner finding |

#### Description

The installed Starlette version does not sufficiently limit the size of multipart form fields without filenames.

An attacker can submit large form fields that cause excessive memory allocation and copying during request processing.

#### Security Impact

This vulnerability can result in significant memory consumption and potentially cause the application process to become unavailable.

Potential impact includes:

- Memory exhaustion
- Application slowdown
- Worker/process termination
- Denial of service

#### Remediation

Upgrade Starlette to at least:

`0.40.0`

Because additional vulnerabilities are also reported against the installed `0.27.0`, the dependency should preferably be upgraded to a current compatible supported release rather than only applying the minimum historical fix.

---

### F-005 — Starlette Windows StaticFiles SSRF / NTLM Credential Exposure

| Field | Details |
|---|---|
| Priority | P2 — High |
| Severity | High |
| Scanner | Trivy SCA / Container |
| Component | `starlette` |
| Installed Version | `0.27.0` |
| Fixed Version | `1.1.0` |
| CVE | CVE-2026-48818 |
| CWE | CWE-918 |
| CVSS | 7.5 |
| Status | Conditional — environment dependent |

#### Description

A vulnerability exists in Starlette's `StaticFiles` handling on Windows.

A specially crafted UNC path can cause an outbound SMB connection before the path is rejected. This can expose NTLMv2 credentials belonging to the service account.

#### Important Manual Validation

This vulnerability specifically affects **Windows** deployments.

The report states that POSIX/Linux systems are not affected by this issue.

Therefore, before treating this as an exploitable application vulnerability, verify:

1. Whether the application runs on Windows.
2. Whether Starlette `StaticFiles` is used.
3. Whether the vulnerable code path is reachable.
4. Whether the service account has credentials that could be exposed through an outbound SMB connection.

#### Remediation

Upgrade Starlette to at least:

`1.1.0`

Also verify application compatibility before upgrading across major/minor framework versions.

---

### F-006 — Starlette Form Limits Bypass / Denial of Service

| Field | Details |
|---|---|
| Priority | P1 — High |
| Severity | High |
| Scanner | Trivy SCA / Container |
| Component | `starlette` |
| Installed Version | `0.27.0` |
| Fixed Version | `1.3.1` |
| CVE | CVE-2026-54283 |
| CWE | CWE-770 |
| CVSS | 7.5 |
| Status | Confirmed scanner finding |

#### Description

Starlette's form parsing limits can be silently ignored for `application/x-www-form-urlencoded` requests.

An application may configure limits expecting resource consumption to be restricted, while specially crafted URL-encoded requests can bypass those limits.

#### Security Impact

An unauthenticated attacker may be able to submit oversized or highly populated form bodies and consume excessive application resources.

Potential impact includes:

- CPU consumption
- Memory/resource exhaustion
- Worker exhaustion
- Denial of service

#### Remediation

Upgrade Starlette to at least:

`1.3.1`

Verify compatibility with the application's FastAPI/Starlette dependency constraints before deployment.

---

### F-007 — Vulnerable `wheel` Package

| Field | Details |
|---|---|
| Priority | P2 — Medium/High |
| Severity | High |
| Scanner | Trivy SCA / Container |
| Component | `wheel` |
| Installed Version | `0.45.1` |
| Fixed Version | `0.46.2` |
| CVE | CVE-2026-24049 |
| CWE | CWE-22, CWE-732 |
| CVSS | 7.1 GHSA/Red Hat |
| Status | Confirmed scanner finding |

#### Description

The installed `wheel` version contains a vulnerability involving file permission handling during wheel archive extraction.

A malicious wheel package can potentially manipulate file permissions during extraction.

#### Security Impact

Successful exploitation requires a malicious package to be processed by the vulnerable functionality.

Potential impact includes:

- Modification of file permissions
- Privilege escalation
- Arbitrary code execution in affected scenarios

The CVSS vector indicates local attack requirements and user interaction, making exploitation less directly exposed than the network-reachable DoS findings above.

#### Remediation

Upgrade `wheel` to at least:

`0.46.2`

Also review whether `wheel` is required at runtime. If it is only needed during image/package build, it should not unnecessarily remain in the production runtime image.

---

## SAST Findings Requiring Manual Validation

### F-008 — Potential Missing CSRF Protection

| Field | Details |
|---|---|
| Priority | P3 — Needs validation |
| Scanner | Semgrep |
| CWE | CWE-352 |
| Location | `notify/src/index.js` |
| Confidence | Low |
| Status | Needs manual validation |

#### Description

Semgrep identified a potential absence of CSRF protection.

The finding alone does not prove that the application is vulnerable. CSRF protection may be implemented elsewhere in the application, at middleware level, through framework configuration, or through an architecture that does not rely on browser cookies for authentication.

#### Manual Validation

Verify:

- Authentication mechanism
- Whether authentication relies on browser cookies
- Whether state-changing endpoints exist
- Whether CSRF tokens are implemented
- Whether SameSite cookie protections are used
- Whether requests are protected through another anti-CSRF mechanism

#### Assessment

Do not classify this as a confirmed vulnerability until manual testing demonstrates an exploitable cross-site state-changing request.

---

### F-009 — Potential Mass Assignment

| Field | Details |
|---|---|
| Priority | P3 — Needs validation |
| Scanner | Semgrep |
| CWE | CWE-915 |
| Location | `notify/src/index.js` |
| Confidence | Low |
| Status | Needs manual validation |

#### Description

Semgrep identified a potential mass-assignment issue.

The finding suggests that user-controlled request properties may potentially be assigned to an application object without sufficiently restricting which properties can be modified.

#### Manual Validation

Review:

- Request body fields
- Object assignment logic
- Allowed/blocked properties
- Authentication and authorization checks
- Whether security-sensitive properties can be supplied by the client

For example, verify whether a user could modify properties such as:

- `role`
- `isAdmin`
- `permissions`
- `ownerId`
- `status`

#### Assessment

This should remain a **potential finding** until the actual data flow is manually confirmed.

---

## IaC Scan Result

### No IaC Security Misconfigurations Detected

| Field | Details |
|---|---|
| Scanner | Trivy |
| Version | 0.74.0 |
| Target | Helm chart |
| Files scanned | 5 |
| Checks passed | 63 |
| Checks failed | 0 |
| Status | Pass |

The following Helm templates were scanned:

- `vulntracker/templates/deployment.yaml`
- `vulntracker/templates/externalsecret.yaml`
- `vulntracker/templates/networkpolicy.yaml`
- `vulntracker/templates/service.yaml`
- `vulntracker/templates/serviceaccount.yaml`

All applicable IaC security checks passed.

This result should **not** be recorded as a vulnerability. It should be reported as a successful security control.

---

## Prioritization Summary

| Priority | Finding | Severity | Status |
|---|---|---|---|
| P1 | python-multipart path traversal / arbitrary file write | High | Confirmed |
| P1 | python-multipart multipart header DoS | High | Confirmed |
| P1 | python-multipart form-urlencoded DoS | High | Confirmed |
| P1 | Starlette multipart DoS | High | Confirmed |
| P1 | Starlette form-limit bypass / DoS | High | Confirmed |
| P2 | Starlette Windows SSRF / NTLM exposure | High | Environment dependent |
| P2 | wheel permission manipulation | High | Confirmed scanner finding |
| P3 | Potential CSRF | Low-confidence | Manual validation required |
| P3 | Potential mass assignment | Low-confidence | Manual validation required |
| — | IaC misconfiguration | — | 0 findings / 63 checks passed |

---

## Overall Assessment

The most significant remediation opportunity is the outdated Python dependency stack, particularly `python-multipart` and `starlette`.

Multiple vulnerabilities are associated with the same outdated dependencies. Therefore, remediation should focus on dependency upgrades rather than attempting to resolve each CVE independently.

The IaC scan produced no failed security checks, while the SAST findings require manual validation before being reported as confirmed vulnerabilities.

Container vulnerabilities should be triaged separately because they represent vulnerabilities in the container's OS/runtime packages and should not be mixed with application dependency findings.

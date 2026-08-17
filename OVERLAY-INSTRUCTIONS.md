
## Overlay usage

This solution is intended to be copied over the interviewer's starter repository. The starter already contains the unchanged notification tests and `package-lock.json`. After copying, run `git diff` and verify that only intended files changed.


1. Clone the starter repository into a fresh repository you own.
2. Copy this solution pack over the cloned working tree.
3. Run `pytest tests/ -v`.
4. Run `cd notify; npm install; npm test`.
5. Build the Docker image.
6. Run `scripts/run-security-scans.ps1` on Windows or `scripts/run-security-scans.sh` on Linux/macOS.
7. Replace the four `NOT_RUN` JSON placeholders with actual raw reports.
8. Review `docs/findings.md` against those reports.
9. Commit and push to your own repository.

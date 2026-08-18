$ErrorActionPreference = "Stop"

if (-not (Get-Command semgrep -ErrorAction SilentlyContinue)) {
    throw "Semgrep is not installed or not in PATH."
}
if (-not (Get-Command trivy -ErrorAction SilentlyContinue)) {
    throw "Trivy is not installed or not in PATH."
}
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is not installed or not in PATH."
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "Node.js/npm is not installed or not in PATH."
}

New-Item -ItemType Directory -Force reports | Out-Null

Write-Host "[1/5] SAST - Semgrep"
semgrep scan --config auto --json --output reports/sast.semgrep.json app notify

Write-Host "[2/5] Install Node dependencies so Trivy can inspect the resolved tree"
Push-Location notify
npm install
Pop-Location

Write-Host "[3/5] SCA - Trivy filesystem"
trivy fs --scanners vuln --format json --output reports/sca.trivy.json .

Write-Host "[4/5] Build and scan container"
docker build -t vulntracker-api:1.0.0 .
trivy image --format json --output reports/container.trivy.json vulntracker-api:1.0.0

Write-Host "[5/5] IaC - Trivy config"
trivy config --format json --output reports/iac.trivy.json helm/

Write-Host ""
Write-Host "Reports generated:"
Get-ChildItem reports\*.json | Select-Object Name, Length

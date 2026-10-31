# Uses the existing Windows Git Credential Manager in memory. Prints no secrets.
param(
    [int]$Limit=100,
    [int]$Offset=0,
    [string]$Output="research/metadata/latest-bulk-review.json"
)
$ErrorActionPreference = "Stop"
$env:GIT_TERMINAL_PROMPT = "0"
$env:GCM_INTERACTIVE = "never"
try {
    $raw = @(("protocol=https","host=github.com","") -join "`n" | git credential fill 2>$null)
    if($LASTEXITCODE -ne 0) { throw "No existing GitHub credential available" }
    $passwordLine = $raw | Where-Object { $_ -like "password=*" } | Select-Object -First 1
    if(-not $passwordLine) { throw "Git credential contains no token" }
    $env:GITHUB_TOKEN = $passwordLine.Substring(9)
    Set-Location (Split-Path -Parent $PSScriptRoot)
    py scripts/metadata_graphql.py --limit $Limit --offset $Offset --output $Output
    exit $LASTEXITCODE
} finally {
    Remove-Item Env:\GITHUB_TOKEN -ErrorAction SilentlyContinue
    Remove-Item Env:\GIT_TERMINAL_PROMPT -ErrorAction SilentlyContinue
    Remove-Item Env:\GCM_INTERACTIVE -ErrorAction SilentlyContinue
}

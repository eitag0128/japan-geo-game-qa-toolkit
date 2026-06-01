param(
    [Parameter(Mandatory = $true)]
    [string]$RepositoryUrl
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".git")) {
    git init -b main
}

git status --short

if (-not (git remote | Select-String -SimpleMatch "origin")) {
    git remote add origin $RepositoryUrl
} else {
    git remote set-url origin $RepositoryUrl
}

git branch -M main
git push -u origin main

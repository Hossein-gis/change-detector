# ============================================================
# Project:      OpenCD Change Detection
# Version:      v1.0
# Created:      2026-07-10
# Purpose:      Build and run Docker container
# Last Updated: 2026-07-10
# ============================================================

param(
    [ValidateSet("online", "offline")]
    [string]$Mode = "online"
)

$ProjectRoot = "D:\3D Query Builder\Change-Detecting"

Set-Location $ProjectRoot

Write-Host "Building with mode: $Mode" -ForegroundColor Cyan

docker compose `
    -f Docker/docker-compose.yml `
    build `
    --build-arg INSTALL_MODE=$Mode

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed" -ForegroundColor Red
    exit 1
}

Write-Host "Running inference..." -ForegroundColor Green

docker compose `
    -f Docker/docker-compose.yml `
    run --rm opencd

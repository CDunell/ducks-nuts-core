\
# ==============================================
# Kafka + Zookeeper Cleanup Script for Windows
# Patch Date: 2025-07-25
# Author: ChatGPT
# ==============================================

$ErrorActionPreference = "SilentlyContinue"

Write-Host "Stopping Kafka and Zookeeper processes..."

# Kill zookeeper and kafka processes
Get-Process | Where-Object { $_.Path -like "*kafka*" -or $_.Path -like "*zookeeper*" } | ForEach-Object {
    try {
        Stop-Process -Id $_.Id -Force
        Write-Host "Stopped process: $($_.Name)"
    } catch {
        Write-Host "Failed to stop $($_.Name): $_"
    }
}

# Remove Kafka installation directory
$kafkaDir = "C:\kafka"
if (Test-Path $kafkaDir) {
    Write-Host "Removing Kafka directory: $kafkaDir"
    Remove-Item -Recurse -Force $kafkaDir
} else {
    Write-Host "Kafka directory not found: $kafkaDir"
}

# Remove downloaded archive
$archive = "$env:TEMP\kafka.tgz"
if (Test-Path $archive) {
    Write-Host "Removing Kafka archive: $archive"
    Remove-Item $archive -Force
}

Write-Host "`n✅ Kafka and Zookeeper cleanup complete."

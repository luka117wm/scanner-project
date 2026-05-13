# run_desktop.ps1 — запуск нативного окна 3D Scanner
# Использование: .\scripts\run_desktop.ps1

Set-Location (Split-Path $PSScriptRoot -Parent)

$venv = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venv) {
    & $venv
} else {
    Write-Warning "venv не найден — используется системный Python"
}

python python\desktop.py

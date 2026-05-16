$ErrorActionPreference = "Stop"

$Root = "C:\Coding"
$Project = Join-Path $Root "projects\bell-dashboard"
$SharedPython = Join-Path $Root "projects\_venvs\closingbell-py312\Scripts\python.exe"
$Python = if (Test-Path -LiteralPath $SharedPython) { $SharedPython } else { "python" }

Set-Location $Project
& $Python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501

@echo off
chcp 65001

set "API_URL=http://localhost:41715/speakers"

echo ==================================================
echo  インストール済みの音声合成モデル一覧
echo ==================================================
echo.

curl -X GET "%API_URL%" ^
  -H "accept: application/json" | powershell -Command "$input | ConvertFrom-Json | ConvertTo-Json -Depth 10 | ForEach-Object { $_ -replace '    ', ' ' }"

echo.
echo.
echo ==================================================

pause
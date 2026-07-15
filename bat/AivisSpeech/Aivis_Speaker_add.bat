@echo off
chcp 65001

rem 設定項目
set "API_URL=http://localhost:41715/aivm_models/install"
set "MODEL_PATH=.\models\にせ.aivmx"

curl -X POST "%API_URL%" ^
  -F "file=@%MODEL_PATH%" ^
  -F "url=" ^
  -i

pause
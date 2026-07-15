@echo off
chcp 65001

rem 設定項目
set "BASE_URL=http://localhost:41715"
set "MODEL_UUID=6d11c6c2-f4a4-4435-887e-23dd60f8b8dd"

curl -X DELETE "%BASE_URL%/aivm_models/%MODEL_UUID%/uninstall" ^
  -i

pause
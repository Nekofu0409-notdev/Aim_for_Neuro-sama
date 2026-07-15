@echo off

cd ..\..\src\voice\TTS_models\AivisSpeech\Windows-x64

start "AivisSpeech" run.exe ^
  --use_gpu ^
  --port 41715
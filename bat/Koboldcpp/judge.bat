@echo off

cd ..\..\models\LLM_server_models\koboldcpp

start "Kobold.cpp" koboldcpp-nocuda.exe ^
  --model "..\..\LLM_models\LFM2.5-1.2B-Instruct-Q4_K_M.gguf" ^
  --contextsize 4096 ^
  --gpulayers -1 ^
  --smartcache ^
  --port 9002 ^
  --host 0.0.0.0 ^
  --gendefaults "{\"max_tokens\":128}" ^
  --usevulkan
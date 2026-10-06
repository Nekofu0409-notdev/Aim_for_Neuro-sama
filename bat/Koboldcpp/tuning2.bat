@echo off

cd ..\..\models\LLM_server_models\koboldcpp

start "Kobold.cpp" koboldcpp-nocuda.exe ^
  --model "..\LLM_models\gemma-4-26B-A4B-it-Japanese-96e-Q4_K_M.gguf" ^
  --contextsize 32768 ^
  --gpulayers -1 ^
  --smartcache ^
  --port 9002 ^
  --multiuser ^
  --host 0.0.0.0 ^
  --gendefaults "{\"max_tokens\":8192}" ^
  --usevulkan
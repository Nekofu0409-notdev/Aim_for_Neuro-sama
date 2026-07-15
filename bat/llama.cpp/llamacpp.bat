@echo off

cd ..\..\LLM_server_models\llama.cpp\llama-b9859-bin-win-cuda-12.4-x64

start "llama.cpp" llama-server.exe ^
  -m "..\models\gemma-4-26B-A4B-it-ultra-uncensored-heretic-Q4_K_M.gguf" ^
  -c 16384 ^
  -n 4096 ^
  -ngl 0 ^
  -b 2048 ^
  -ub 512 ^
  --no-kv-offload ^
  --mlock ^
  --port 9001 ^
  --host 0.0.0.0
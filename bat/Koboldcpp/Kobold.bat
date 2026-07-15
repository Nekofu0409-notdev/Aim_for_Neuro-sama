@echo off

cd ..\..\src\llm\LLM_server_models\koboldcpp

start "Kobold.cpp" koboldcpp.exe ^
  --model "..\LLM_models\gemma-4-26B-A4B-it-ultra-uncensored-heretic-Q4_K_M.gguf" ^
  --contextsize 16384 ^
  --gpulayers 0 ^
  --smartcache ^
  --port 9001 ^
  --multiuser ^
  --host 0.0.0.0 ^
  --gendefaults "{\"max_tokens\":4096}"
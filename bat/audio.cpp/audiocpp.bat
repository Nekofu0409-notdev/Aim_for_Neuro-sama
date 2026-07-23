@echo off

cd ..\..\src\voice\stt_src\STT_models\audio_cpp

start "audio.cpp" audiocpp-windows-cuda-fast-e12fc74\audiocpp_server.exe ^
  --config server.json
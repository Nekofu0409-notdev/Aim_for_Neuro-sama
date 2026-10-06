@echo off

cd ..\..\models\STT_models\audio_cpp

start "audio.cpp" audiocpp-vulkan\audiocpp_server.exe ^
  --config server.json
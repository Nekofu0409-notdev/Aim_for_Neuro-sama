@echo on

cd ..\..\src\voice\stt_src\STT_models\audio_cpp

audiocpp-windows-cuda-fast-e12fc74\audiocpp_gguf.exe ^
  --input .\models\qwen3-asr\model.safetensors ^
  --root .\models\qwen3-asr\safetensors ^
  --output .\models\qwen3-asr\qwen3-asr-1.7B-q4_k.gguf ^
  --type q4_k ^
  --overwrite

pause
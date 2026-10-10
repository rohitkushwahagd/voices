#!/bin/bash
# One-step voice setup for a fresh workspace.
#   bash setup.sh            -> English + Kokoro (fast, ~1-2 min)
#   bash setup.sh --hindi    -> also AI4Bharat Hindi (~1.6 GB of models + PyTorch, ~8-10 min)
#
# Afterwards, point the animation-studio voice engine at one voice by putting its shim first on PATH
# and setting PIPER_MODEL (the engine only checks that it is set):
#   export PATH=~/voice-library/use/kokoro:$PATH PIPER_MODEL=kokoro KOKORO_VOICE=am_michael
#   export PATH=~/voice-library/use/piper-ryan:$PATH PIPER_MODEL=~/voice-library/piper/en-us-ryan-high/en-us-ryan-high.onnx
#   export PATH=~/voice-library/use/hindi:$PATH PIPER_MODEL=hindi HINDI_SPEAKER=male
set -euo pipefail
REPO=rohitkushwahagd/voices
TAG=v1
HOME_DIR=${VOICES_HOME:-$HOME/voice-library}
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$HOME_DIR"/{piper,kokoro,ai4bharat,use/kokoro,use/piper-ryan,use/piper-lessac,use/hindi}
cd "$HOME_DIR"

get() { gh release download "$TAG" -R "$REPO" -p "$1" -D "$HOME_DIR/dl" --clobber; }
mkdir -p dl

echo "== Piper (English) + Kokoro (English, Hindi and 7 more languages)"
get 'piper-*.tar.gz'; for f in dl/piper-*.tar.gz; do tar xzf "$f" -C piper; done
get 'kokoro-v1.0.onnx'; get 'kokoro-v1.0.int8.onnx'; get 'voices-v1.0.bin'; mv dl/kokoro-v1.0*.onnx dl/voices-v1.0.bin kokoro/
pip install -q --break-system-packages piper-tts kokoro-onnx soundfile 2>&1 | grep -v WARNING || true

# the shims: each folder holds a `piper` the animation engine will call
cp "$HERE"/bin/kokoro_tts.py "$HERE"/bin/hindi_tts.py "$HOME_DIR"/
printf '#!/bin/bash\n[ "$1" = "--help" ] && exit 0\nexec python3 %s/kokoro_tts.py "$@" 2>/dev/null\n' "$HOME_DIR" > use/kokoro/piper
PIPER_BIN=$(command -v piper)
printf '#!/bin/bash\nexec %s --length-scale 1.12 --sentence-silence 0.4 "$@"\n' "$PIPER_BIN" > use/piper-ryan/piper
cp use/piper-ryan/piper use/piper-lessac/piper
printf '#!/bin/bash\n[ "$1" = "--help" ] && exit 0\nexec python3 %s/hindi_tts.py "$@" 2>/dev/null\n' "$HOME_DIR" > use/hindi/piper
chmod +x use/*/piper

if [ "${1:-}" = "--hindi" ]; then
  echo "== AI4Bharat Hindi (male + female)"
  get 'ai4bharat-hi-*.tar'; for f in dl/ai4bharat-hi-*.tar; do tar xf "$f" -C ai4bharat; done
  mkdir -p ai4bharat/models/v1 && ln -sfn "$HOME_DIR/ai4bharat/hi" ai4bharat/models/v1/hi
  # versions that work together (PyTorch from PyPI; download.pytorch.org is blocked by the proxy)
  pip install -q --break-system-packages coqui-tts torch torchaudio torchcodec "transformers>=4.57,<5" 2>&1 | grep -v WARNING || true
fi
rm -rf dl
echo "== Voices ready in $HOME_DIR"

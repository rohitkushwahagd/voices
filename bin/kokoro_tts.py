#!/usr/bin/env python3
"""Piper-compatible shim for Kokoro (kokoro-onnx).

Reads text on stdin and writes a WAV to --output_file, so the animation-studio voice engine can use it
as if it were `piper`. Choose the voice with env vars:
  KOKORO_VOICE  e.g. am_michael (default), am_fenrir, bm_george, af_heart, hm_omega, hm_psi, hf_alpha, hf_beta
  KOKORO_LANG   e.g. en-us, en-gb, hi (default: picked from the voice prefix)
  KOKORO_SPEED  default 0.92 (a little slower than normal, for calm narration)
  KOKORO_MODEL  kokoro-v1.0.onnx (default) or kokoro-v1.0.int8.onnx (smaller, slightly lower quality)
  VOICES_HOME   where setup.sh put the files (default ~/voice-library)
"""
import os, sys, warnings
warnings.filterwarnings('ignore')
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

home = os.environ.get('VOICES_HOME', os.path.expanduser('~/voice-library'))
args = sys.argv[1:]
out = args[args.index('--output_file') + 1] if '--output_file' in args else args[args.index('-f') + 1]
voice = os.environ.get('KOKORO_VOICE', 'am_michael')
lang = os.environ.get('KOKORO_LANG') or {'a': 'en-us', 'b': 'en-gb', 'h': 'hi', 'e': 'es', 'f': 'fr-fr', 'i': 'it', 'p': 'pt-br', 'j': 'ja', 'z': 'cmn'}.get(voice[0], 'en-us')
speed = float(os.environ.get('KOKORO_SPEED', '0.92'))
model = os.environ.get('KOKORO_MODEL', 'kokoro-v1.0.onnx')
k = Kokoro(os.path.join(home, 'kokoro', model), os.path.join(home, 'kokoro', 'voices-v1.0.bin'))
text = sys.stdin.read().strip()
# speak sentence by sentence with a short breath between them
import re
sents = [s.strip() for s in re.split(r'(?<=[.!?।])\s+', text) if s.strip()]
parts, sr = [], 24000
for s in sents:
    a, sr = k.create(s, voice=voice, speed=speed, lang=lang)
    parts += [np.asarray(a, dtype=np.float32), np.zeros(int(0.4 * sr), np.float32)]
sf.write(out, np.concatenate(parts[:-1]) if parts else np.zeros(sr, np.float32), sr)

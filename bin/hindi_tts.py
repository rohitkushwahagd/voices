#!/usr/bin/env python3
"""Piper-compatible shim for AI4Bharat's Hindi FastPitch + HiFiGAN (Coqui TTS).

Reads Hindi (Devanagari) text on stdin and writes a WAV to --output_file.
  HINDI_SPEAKER  male (default) or female
  VOICES_HOME    where setup.sh put the files (default ~/voice-library)
Write English words in Devanagari (इंटरनेट, नॉर्मल): this model only reads Hindi script.
"""
import os, sys, warnings
warnings.filterwarnings('ignore')
home = os.environ.get('VOICES_HOME', os.path.expanduser('~/voice-library'))
args = sys.argv[1:]
out = os.path.abspath(args[args.index('--output_file') + 1])
text = sys.stdin.read().strip()
os.chdir(os.path.join(home, 'ai4bharat'))  # its config expects models/v1/hi/... relative to here
import numpy as np
from TTS.utils.synthesizer import Synthesizer
s = Synthesizer(tts_checkpoint='hi/fastpitch/best_model.pth', tts_config_path='hi/fastpitch/config.json',
                vocoder_checkpoint='hi/hifigan/best_model.pth', vocoder_config='hi/hifigan/config.json',
                tts_speakers_file='hi/fastpitch/speakers.pth', use_cuda=False)
parts = []
for sent in [p.strip() for p in text.replace('।', '।|').split('|') if p.strip()]:
    parts += [np.asarray(s.tts(sent, speaker_name=os.environ.get('HINDI_SPEAKER', 'male')), dtype=np.float32),
              np.zeros(int(0.4 * s.output_sample_rate), np.float32)]
s.save_wav(np.concatenate(parts[:-1]), out)

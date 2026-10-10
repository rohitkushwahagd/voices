#!/usr/bin/env python3
"""Piper-compatible router: lets every dialogue line pick its own voice (for multi-character films).

The animation-studio engine calls `piper --model <spec> --output_file out.wav` with the text on stdin,
where <spec> is the line's `voice` (or PIPER_MODEL when the line has none). Spec format:

    hi:male | hi:female                    AI4Bharat Hindi (needs setup.sh --hindi)
    kokoro:<voice>                         Kokoro, e.g. kokoro:hm_omega, kokoro:hf_alpha, kokoro:am_michael
    piper:ryan | piper:lessac              Piper English

Optional modifiers after the voice, joined by ':' (any order):
    pitch=<semitones>   e.g. pitch=-2 (deeper, heavier) or pitch=3 (lighter); keeps the speed
    speed=<factor>      e.g. speed=1.1 (faster) or speed=0.9 (slower)
    vol=<factor>        e.g. vol=1.2

Examples:  hi:male:pitch=-2:speed=0.95   (Pappu)   hi:female:pitch=1   (Amma)   kokoro:hm_psi:pitch=3 (Chintu)
"""
import os, sys, subprocess, shutil
home = os.environ.get('VOICES_HOME', os.path.expanduser('~/voice-library'))
args = sys.argv[1:]
out = os.path.abspath(args[args.index('--output_file') + 1])
spec = args[args.index('--model') + 1] if '--model' in args else os.environ.get('PIPER_MODEL', 'hi:male')
text = sys.stdin.read()
parts = spec.split(':')
eng = parts[0]
voice = parts[1] if len(parts) > 1 and '=' not in parts[1] else ''
mods = dict(p.split('=', 1) for p in parts[1:] if '=' in p)

raw = out + '.raw.wav'
env = dict(os.environ)
if eng == 'hi':
    env['HINDI_SPEAKER'] = voice or 'male'
    cmd = ['python3', os.path.join(home, 'hindi_tts.py'), '--output_file', raw]
elif eng == 'kokoro':
    env['KOKORO_VOICE'] = voice or 'hm_omega'
    cmd = ['python3', os.path.join(home, 'kokoro_tts.py'), '--output_file', raw]
elif eng == 'piper':
    model = {'ryan': 'en-us-ryan-high', 'lessac': 'en-us-lessac-medium'}.get(voice or 'ryan', voice)
    real = shutil.which('piper', path=os.pathsep.join(d for d in os.environ.get('PATH', '').split(os.pathsep) if '/use/' not in d))  # skip our own shims
    cmd = [real, '--model', os.path.join(home, 'piper', model, model + '.onnx'), '--output_file', raw, '--length-scale', '1.12', '--sentence-silence', '0.4']
else:
    sys.exit(f'voice_router: unknown engine in spec "{spec}"')
subprocess.run(cmd, input=text, text=True, env=env, check=True, stderr=subprocess.DEVNULL)

# pitch / speed / volume through ffmpeg (rubberband keeps formant-ish quality; fall back to asetrate)
pitch = float(mods.get('pitch', 0)); speed = float(mods.get('speed', 1)); vol = float(mods.get('vol', 1))
if pitch == 0 and speed == 1 and vol == 1:
    os.replace(raw, out)
else:
    sr = int(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=sample_rate', '-of', 'csv=p=0', raw], capture_output=True, text=True).stdout.strip() or 22050)
    k = 2 ** (pitch / 12)
    filt = f'asetrate={int(sr * k)},aresample={sr},atempo={max(0.5, min(2.0, speed / k)):.4f},volume={vol}'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', filt, out], check=True)
    os.remove(raw)

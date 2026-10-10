# voices

Rohit's offline narrator voices for the animated psychology videos (animation-studio + faceless-psychology-video skills).
The voice files live on two branches, split into 90 MB parts because GitHub's file limit is 100 MB:
- `voices-en`: Piper and Kokoro, about 580 MB.
- `voices-hi`: AI4Bharat Hindi, about 1.6 GB.

`main` holds only the setup script and shims, so cloning it is instant. `setup.sh` rejoins the parts and checks every file's SHA-256.

## Setup in a new Claude workspace

```bash
git clone --depth 1 https://github.com/rohitkushwahagd/voices ~/voices-repo
bash ~/voices-repo/setup.sh           # English: Piper + Kokoro (~1-2 min)
bash ~/voices-repo/setup.sh --hindi   # + AI4Bharat Hindi (~8-10 min)
```

Then pick a voice for the animation engine (it calls whatever `piper` is first on PATH):

| Use | Command |
|---|---|
| Kokoro, any voice | `export PATH=~/voice-library/use/kokoro:$PATH PIPER_MODEL=kokoro KOKORO_VOICE=am_michael` |
| Piper Ryan (calm US male) | `export PATH=~/voice-library/use/piper-ryan:$PATH PIPER_MODEL=~/voice-library/piper/en-us-ryan-high/en-us-ryan-high.onnx` |
| Piper Lessac (neutral US) | `export PATH=~/voice-library/use/piper-lessac:$PATH PIPER_MODEL=~/voice-library/piper/en-us-lessac-medium/en-us-lessac-medium.onnx` |
| AI4Bharat Hindi | `export PATH=~/voice-library/use/hindi:$PATH PIPER_MODEL=hindi HINDI_SPEAKER=male` (or `female`) |

In a song.js, set the same values on `process.env` before `Voice.speak(...)`.

### Several characters in one film (a voice per line)
Use the router and give every line its own `voice` spec:
```js
process.env.PATH = `${process.env.HOME}/voice-library/use/router:${process.env.PATH}`;
process.env.PIPER_MODEL = 'hi:male'; // used by lines without a voice
Voice.speak([
  { at: 0.5, who: 'P', voice: 'hi:male:pitch=-2:speed=0.95', text: 'नमस्ते दोस्तों!' },   // Pappu
  { at: 3.0, who: 'A', voice: 'hi:female:pitch=1', text: 'पप्पू! दूध पी!' },             // Amma
  { at: 5.5, who: 'C', voice: 'kokoro:hm_psi:pitch=3:speed=1.05', text: 'भैया!' },       // Chintu
], { out, length });
```
Specs are `hi:male|female`, `kokoro:<voice>` and `piper:ryan|lessac`. Each can take optional modifiers:
- `:pitch=<semitones>`
- `:speed=<factor>`
- `:vol=<factor>`

`who` drives each character's lip-sync (`Subs.mouth(VO, t, 'P')`).

## What's stored (after setup.sh rejoins the parts)

| File | Voice(s) | Size |
|---|---|---|
| `piper-en-us-ryan-high.tar.gz` | Piper Ryan, calm US male (used in the English pilot) | 106 MB |
| `piper-en-us-lessac-medium.tar.gz` | Piper Lessac, neutral US | 58 MB |
| `kokoro-v1.0.onnx` + `voices-v1.0.bin` | Kokoro, all 54 voices (US/UK English, Hindi, Spanish, French, Italian, Portuguese, Japanese, Chinese) | 326 + 28 MB |
| `kokoro-v1.0.int8.onnx` | Kokoro, smaller quantized model (`KOKORO_MODEL=kokoro-v1.0.int8.onnx`) | 92 MB |
| `ai4bharat-hi-fastpitch.tar` + `ai4bharat-hi-hifigan.tar` | AI4Bharat Hindi male + female (used in the Hindi pilot) | 637 + 1016 MB |
| `english-voices.mp3`, `hindi-voices.mp3` | Comparison clips of the main voices | <1 MB |

**Kokoro voices worth trying:**
- English narrators: `am_michael`, `am_fenrir`, `am_onyx` (US male); `bm_george`, `bm_lewis` (UK male); `af_heart`, `af_bella` (US female).
- Hindi: `hm_omega`, `hm_psi` (male); `hf_alpha`, `hf_beta` (female).

## Notes
- **Hindi script.** AI4Bharat reads only Devanagari, so write English words in Hindi script. Kokoro Hindi also expects Devanagari.
- **PyTorch for the Hindi model.** AI4Bharat needs PyTorch, which `setup.sh --hindi` installs from PyPI because the PyTorch download site is blocked in Claude workspaces. Coqui TTS needs `transformers` 4.57–4.x and `torchcodec`.
- **Licences.**
  - Piper voices are MIT.
  - Kokoro is Apache-2.0.
  - AI4Bharat Indic-TTS is MIT for code; check the model card before commercial use.

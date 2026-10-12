# Downloadable files

Generated from `catalogue.json`; regenerate with `uv run python scripted/src/catalogue_readme.py`.

All files are PCM24 at 48000 Hz, peak -12 dBFS.
Every channel carries the same simultaneous signal. Choose stereo unless your source routes eight channels.

| Signal | Channels | Duration | Download |
|---|---:|---:|---|
| reference-400hz | 2 | 30 s | [reference-400hz-2ch-48k-v0.1.0.wav](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/reference-400hz-2ch-48k-v0.1.0.wav) |
| reference-400hz | 8 | 30 s | [reference-400hz-8ch-48k-v0.1.0.wav](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/reference-400hz-8ch-48k-v0.1.0.wav) |
| timing-probe | 2 | 4 s | [timing-probe-2ch-48k-v0.1.0.wav](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/timing-probe-2ch-48k-v0.1.0.wav) |
| timing-probe | 8 | 4 s | [timing-probe-8ch-48k-v0.1.0.wav](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/timing-probe-8ch-48k-v0.1.0.wav) |
| complete-characterisation | 2 | 10 s | [complete-characterisation-2ch-48k-v0.1.0.wav](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/complete-characterisation-2ch-48k-v0.1.0.wav) |
| complete-characterisation | 8 | 10 s | [complete-characterisation-8ch-48k-v0.1.0.wav](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/complete-characterisation-8ch-48k-v0.1.0.wav) |

## Complete sequence

| Section | From | To |
|---|---:|---:|
| lead | 0 s | 0.5 s |
| tone | 0.5 s | 6 s |
| gap | 6 s | 6.25 s |
| timing | 6.25 s | 9.75 s |
| tail | 9.75 s | 10 s |

The tone includes guard silence and shaped ramps; measure the steady interior.
The steady sine RMS is approximately 3.01 dB below its peak, before any analogue playback gain.
The source equipment determines the analogue output voltage. Use the meter reading for voltage calibration.

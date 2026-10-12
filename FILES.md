# Downloadable files

WAV references for measuring audio levels, distortion, relative delay and polarity.
See the [waveform previews and usage guide](README.md#waveforms) to choose a signal.

All files are 24-bit PCM at 48 kHz, peak -12 dBFS.
Every channel carries the same simultaneous signal. Choose stereo unless your player and interface need eight channels.

| Signal | Channels | Duration | Download |
|---|---:|---:|---|
| 400 Hz reference tone | 2 | 30 s | [reference-400hz-2ch-48k-v0.1.0.wav](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/reference-400hz-2ch-48k-v0.1.0.wav) |
| 400 Hz reference tone | 8 | 30 s | [reference-400hz-8ch-48k-v0.1.0.wav](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/reference-400hz-8ch-48k-v0.1.0.wav) |
| Timing and polarity probe | 2 | 4 s | [timing-probe-2ch-48k-v0.1.0.wav](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/timing-probe-2ch-48k-v0.1.0.wav) |
| Timing and polarity probe | 8 | 4 s | [timing-probe-8ch-48k-v0.1.0.wav](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/timing-probe-8ch-48k-v0.1.0.wav) |
| Complete characterisation sequence | 2 | 10 s | [complete-characterisation-2ch-48k-v0.1.0.wav](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/complete-characterisation-2ch-48k-v0.1.0.wav) |
| Complete characterisation sequence | 8 | 10 s | [complete-characterisation-8ch-48k-v0.1.0.wav](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/complete-characterisation-8ch-48k-v0.1.0.wav) |

## Complete sequence

| Section | From | To |
|---|---:|---:|
| Opening silence | 0 s | 0.5 s |
| 400 Hz tone (including ramps) | 0.5 s | 6 s |
| Silence between signals | 6 s | 6.25 s |
| Timing and polarity probes | 6.25 s | 9.75 s |
| Closing silence | 9.75 s | 10 s |

The tone includes guard silence and shaped ramps; measure the steady interior.
The steady sine RMS is approximately 3.01 dB below its peak, before any analogue playback gain.
The source equipment determines the analogue output voltage. Use the meter reading for voltage calibration.

This guide is generated from [the catalogue](catalogue.json).
For regeneration instructions, see [Updating the collection](CONTRIBUTING.md#update-the-file-guide-and-plots).

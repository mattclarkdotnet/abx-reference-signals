# Audio reference signals

WAV files for measuring audio levels, distortion, relative delay and polarity.

## Download

<!-- BEGIN SIGNAL DOWNLOADS -->

| Signal | Duration | Stereo | 8-channel |
|---|---:|---|---|
| 400 Hz reference tone | 30 s | [Download WAV](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/reference-400hz-2ch-48k-v0.1.0.wav) | [Download WAV](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/reference-400hz-8ch-48k-v0.1.0.wav) |
| Timing and polarity probe | 4 s | [Download WAV](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/timing-probe-2ch-48k-v0.1.0.wav) | [Download WAV](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/timing-probe-8ch-48k-v0.1.0.wav) |
| Complete characterisation sequence | 10 s | [Download WAV](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/complete-characterisation-2ch-48k-v0.1.0.wav) | [Download WAV](https://github.com/mattclarkdotnet/abx-reference-signals/releases/download/reference-v0.1.0/complete-characterisation-8ch-48k-v0.1.0.wav) |

<!-- END SIGNAL DOWNLOADS -->

All files are **48 kHz, 24-bit PCM WAV**, with a peak level of **−12 dBFS**.
Stereo and eight-channel versions carry identical, time-aligned signals on every
channel.

[File details and sequence timings](FILES.md) · [Release files](https://github.com/mattclarkdotnet/abx-reference-signals/releases/tag/reference-v0.1.0) · [SHA-256 checksums](SHA256SUMS)

## Waveforms

The plots show one channel, with amplitude relative to digital full scale.

### 400 Hz reference tone

A 30-second sine wave with a smooth, bandwidth-limited start and finish. Use the
steady section for output-voltage, level and distortion measurements.

![400 Hz reference tone: full timeline, smooth onset and offset, and a close-up of the sine wave.](docs/waveforms/reference-400hz.png)

### Timing and polarity probe

A four-second sequence of one-millisecond, cosine-windowed 1 kHz bursts, repeated
every 250 ms. Use the bursts to compare arrival times and polarity.

![Timing and polarity probe: repeated bursts across four seconds and the sample waveform of one burst.](docs/waveforms/timing-probe.png)

### Complete characterisation sequence

A ten-second sequence combining the 400 Hz tone and timing probes for level,
distortion, delay and polarity measurements in one playback. See the
[section timings](FILES.md#complete-sequence).

![Complete characterisation: ten-second tone-and-probe sequence with a close-up of the transition through silence.](docs/waveforms/complete-characterisation.png)

## Using the signals

For comparing two devices under test (DUTs), use the same source arrangement as
for listening. **Play the test signal through both DUTs simultaneously.**

Measure output voltage during the steady section of the 400 Hz tone. For relative
delay and polarity, capture the two outputs simultaneously.

## Further documentation

- [Generate files from the saved recordings](scripted/README.md)
- [Make fresh REW recordings](rew/README.md)
- [Validation and measured results](validation/README.md)
- [Update or publish the collection](CONTRIBUTING.md)

## Licence

Audio: [CC0 1.0](LICENSE-CC0). Code and documentation: [MIT](LICENSE-MIT).
See [LICENSE](LICENSE) for details.

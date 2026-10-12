# Reference signals

A portable collection of reproducible audio references, published in
[abx-reference-signals](https://github.com/mattclarkdotnet/abx-reference-signals).
It is also retained as a self-contained directory in the ABX controller project.
The retained files pass the numerical qualification described below.

The initial delivery uses 24-bit, 48 kHz PCM WAV: a bandwidth-limited 400 Hz
reference tone, a timing/polarity probe, and a ten-second sequence combining the
two for DUT characterisation. Stereo channels carry the same simultaneous signal;
eight-channel variants support the selected USB source arrangement. See the
generated [file guide](FILES.md), [catalogue](catalogue.json) and [checksums](SHA256SUMS).

Play the test signal through both DUTs simultaneously. Playback belongs to the
user's source system. The controller observes the DUT outputs; these tools neither
control DUT playback nor turn the phone into the audio source. For absolute
voltage calibration, the meter reading is the reference, not a digital file level.

## Waveforms

These plots use the actual samples in the published WAVs. All channels in both
the stereo and eight-channel versions carry the same waveform, so each plot
applies to both downloads. Amplitude is relative to digital full scale; overviews
show the minimum and maximum samples in each plotted interval, preserving brief
peaks. Close-ups labelled “samples” show the waveform itself.

### 400 Hz reference tone

A 30-second steady tone with a smooth, bandwidth-limited start and finish. Use it
for voltage calibration or standalone level and distortion measurements.

![400 Hz reference tone: full timeline, smooth onset and offset, and a close-up of the sine wave.](docs/waveforms/reference-400hz.png)

### Timing and polarity probe

A four-second train of short probes, repeated every 250 ms. Each probe is a
one-millisecond, cosine-windowed 1 kHz burst, returning to silence between probes.
The close-up shows its positive and negative lobes.

![Timing and polarity probe: repeated bursts across four seconds and the sample waveform of one burst.](docs/waveforms/timing-probe.png)

### Complete DUT characterisation

One ten-second file combines the tone for levels and distortion with the probes
for delay and polarity. It starts with 0.5 seconds of silence, followed by
5.5 seconds of tone, a 0.25-second gap, 3.5 seconds of probes and a 0.25-second tail.

![Complete characterisation: ten-second tone-and-probe sequence with a close-up of the transition through silence.](docs/waveforms/complete-characterisation.png)

## Layout

- `rew/`: REW API tools, generation recipes and unmodified virtual-device captures.
- `scripted/`: subsequent signal processing, channel expansion and composition.
- `validation/`: file qualification tools and reports tied to the checked files.
- `docs/waveforms/`: PNG illustrations generated from the published PCM files.

The generation method determines the directory. An API script that asks REW to
generate samples still produces a REW original. Shaping or combining that result
produces a scripted derivative with explicit source provenance.

## Environment

Install uv, then run from this directory:

```sh
uv sync --locked
uv run python -m unittest discover -s rew/tests
uv run python scripted/src/generate.py
uv run python validation/src/validate.py
uv run python -m unittest discover -s validation/tests
uv run python scripted/src/catalogue_readme.py
```

To rebuild the 2000-pixel-wide README images from the retained WAVs:

```sh
uv run --locked --group docs python scripted/src/plot_waveforms.py
```

The plotting script checks the catalogue hashes and confirms that all channel
variants share identical samples before drawing a single plot for each waveform.
It does not regenerate or modify the audio.

The Python pin and lockfile live here so the directory can be used independently
of the controller workspace. REW generation needs the documented REW installation,
its local API and BlackHole 2ch; see [REW instructions](rew/README.md).

NumPy provides array operations, SciPy provides established signal filtering and
spectral analysis, sounddevice uses PortAudio for explicit virtual-device capture,
and soundfile uses libsndfile for WAV decoding/encoding. These host-only libraries
avoid custom DSP, audio-driver and container implementations; none is bundled in
firmware. Their exact dependencies are resolved in `uv.lock`.
The optional `docs` dependency group adds Matplotlib for standard scientific
plotting and PNG output; it is only needed to rebuild the README illustrations.

## Publication

Publish qualified WAVs, catalogue and checksums as versioned GitHub Release assets.
Keep the files and their generating sources in this directory too. Release tags
must identify the matching recipes, code and validation reports. Direct download
links use an explicit tag, work without signing in and preserve the qualified
file hashes. Publication uses the repository and tag in the generation recipe.
After upload, run `uv run python validation/src/verify_downloads.py` to check every
asset anonymously against the retained bytes.

Audio is [CC0 1.0](LICENSE-CC0). Code, recipes, metadata and documentation are
[MIT licensed](LICENSE-MIT). See [LICENSE](LICENSE) for the scope of each licence.

## REW capture

The installed REW 5.40 Beta 101 / API 0.9.0 exposes signal configuration and
Play/Stop, but no generator WAV export in its served API description or command
list. We instead control REW's generator through the API and record BlackHole's
virtual input. Source captures use float32 WAV to preserve the captured samples;
published derivatives are 24-bit PCM. Capture latency/start phase may vary, so
REW reproduction checks signal equivalence rather than promising identical bytes.
Every retained capture and deterministic derivative has its own content hash.

## Qualification and limits

The validator measures the decoded published PCM, including the entire tone's
onset and offset without an analysis window. The recipe requires at least 100 dB
rejection outside 200–600 Hz and harmonics 2–9 below −110 dBR. Results tied to each
file hash live in [validation/reports/signals.json](validation/reports/signals.json).
These are numerical rejection limits: no finite-duration file has literally zero
energy at every frequency outside its passband.

An independent REW recapture passed the same spectral/format requirements.
Regenerating from the retained captures produces identical WAV bytes under the
pinned environment. Raw captures include startup audio and padding; the scripted
recipe deliberately selects settled material and preserves shaped filter tails.

The collection defines source signals, not the precision of a DAC, DUT, ADC or
meter. The ABX host tests pass the actual files through acquisition mocks and the
production estimators, completing the ten-second sequence in 7.14 seconds with
20 ms routing/settling and fresh 20 ms captures. This is software timing evidence;
physical acquisition performance remains to be qualified on the real hardware.

# Rebuild the reference files

The repository includes the original REW recordings, so you can rebuild the WAVs
without installing REW, an audio driver or any ABX controller software. The scripts
add smooth ramps, filter the reference tone, assemble the combined sequence and
write stereo and eight-channel files.

## Set up the tools

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and
[Git](https://git-scm.com/downloads), then open a terminal:

```sh
git clone https://github.com/mattclarkdotnet/abx-reference-signals.git
cd abx-reference-signals
uv sync --locked
```

Alternatively, download and unpack the repository ZIP from GitHub, then run
`uv sync --locked` in its top-level directory. All commands below run from that
same directory.

uv creates the Python environment and installs the packages in `uv.lock`,
downloading Python if needed. The project supports Python 3.12 or newer and
selects the 3.12 series by default. To try another supported Python version, use
uv's [`--python` option](https://docs.astral.sh/uv/concepts/python-versions/).
The [release baseline](../README.md#release-generation-baseline) records what was
actually used; other versions need validation rather than an assumption of
identical output.

NumPy and SciPy provide numerical processing and filtering; soundfile reads and
writes WAVs. sounddevice is used only when making fresh recordings. The optional
`docs` dependency group adds Matplotlib to rebuild the waveform illustrations.

## Rebuild and check

Run these commands in a fresh clone or working copy: they rewrite generated WAVs,
the catalogue, checksums and validation report in that copy.

```sh
uv run --locked python scripted/src/generate.py
uv run --locked python validation/src/validate.py
```

The six output WAVs are in `scripted/files/`; measurements are written to
`validation/reports/signals.json`. To compare the rebuilt files with a release,
keep that release's `SHA256SUMS` separately before running the generator, which
creates a new checksum file. See [validation instructions](../validation/README.md)
for the distinction between matching release bytes and passing the signal checks.

To record new source material first, follow [Fresh REW captures](../rew/README.md).
That workflow keeps a new capture in a separate directory and builds it with
`--root`, leaving the release's source recordings intact.

## What the processing does

[recipes/reference-v1.json](recipes/reference-v1.json) defines durations, levels,
channel variants and the reference tone's numerical spectral limits.

The 400 Hz tone is taken from a settled part of the REW recording. Guard silence
and cosine ramps are added, then a Kaiser-windowed finite impulse response (FIR)
band-pass filter limits its spectrum. The guard intervals retain the filter tails.
The validator includes the whole onset and offset when checking out-of-band
energy, and measures harmonics in the steady part.

Timing sections retain complete REW bursts and are cut between them. The
ten-second sequence uses shorter tone and probe sections. After shaping, peaks
are normalised to −12 dBFS and samples are rounded to 24-bit PCM. Channel expansion
copies the same samples to every channel; the player controls their routing.

Rebuilding from the saved recordings reproduced identical WAV bytes in the release
baseline. Fresh REW recordings may differ in start phase or capture latency, so
they are assessed against the same signal requirements, not a promise of identical
bytes. Every new output still has a checksum identifying its particular contents.

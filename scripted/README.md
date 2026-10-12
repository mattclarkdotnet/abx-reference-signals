# Generate files from the saved recordings

The scripts shape the included REW recordings, assemble the combined sequence
and write stereo and eight-channel WAVs.

## Set up the tools

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and
[Git](https://git-scm.com/downloads), then run:

```sh
git clone https://github.com/mattclarkdotnet/abx-reference-signals.git
cd abx-reference-signals
uv sync --locked
```

Alternatively, unpack the repository ZIP and run `uv sync --locked` in its
top-level directory. Run all subsequent commands from that directory.

uv sets up Python and the packages in `uv.lock`. The scripts require Python 3.12
or newer; `.python-version` selects the 3.12 series by default. Use uv's
[`--python` option](https://docs.astral.sh/uv/concepts/python-versions/) to select
another version.

## Release generation baseline

Environment used to generate and check release **v0.1.0**:

| Component | Release baseline |
|---|---|
| Room EQ Wizard | 5.40 Beta 101, API 0.9.0 |
| Virtual audio driver | BlackHole 2ch 0.7.1 |
| Python | CPython 3.12.11 |
| Operating system for fresh captures | macOS 27.2 |

The [REW capture guide](../rew/README.md) covers fresh recordings and selecting a
REW build. Run the same validation checks when using another tool version.

## Generate and check

These commands write the WAVs, catalogue, checksums and validation report in your
working copy. Save the release's `SHA256SUMS` separately first if you want to
compare the generated files with that release.

```sh
uv run --locked python scripted/src/generate.py
uv run --locked python validation/src/validate.py
```

Outputs are in `scripted/files/`; measurements are in
`validation/reports/signals.json`. See [validation instructions](../validation/README.md)
for checksums, signal requirements and tests.

## Signal processing

[recipes/reference-v1.json](recipes/reference-v1.json) defines durations, levels,
channel variants and spectral limits.

The reference tone uses a settled section of the REW sine recording, with guard
silence and cosine ramps. A Kaiser-windowed finite impulse response (FIR)
band-pass filter limits its spectrum; the guard intervals retain the filter tails.
Validation includes the whole onset and offset when checking out-of-band energy
and measures harmonics in the steady section.

Timing sections retain complete REW bursts and are cut between them. The
combined sequence uses shorter tone and probe sections. Peaks are normalised to
−12 dBFS, samples are rounded to 24-bit PCM, and the same samples are copied to
every channel.

Rebuilding the saved recordings with the release baseline reproduces the release
checksums. Fresh recordings can vary in start phase and capture latency; validate
them against the signal requirements.

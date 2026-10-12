# Check the reference files

## Verify release checksums

Download `SHA256SUMS` alongside the six WAVs from the same release. Run this in
the download directory on macOS:

```sh
shasum -a 256 -c SHA256SUMS
```

On Linux, use `sha256sum -c SHA256SUMS`.

## Measure the saved audio

Set up the [Python environment](../scripted/README.md#set-up-the-tools), then run
from the repository's top-level directory:

```sh
uv run --locked python validation/src/validate.py
```

The validator checks format, sample rate, duration, channel equality, peak level,
boundaries, frequency, harmonics, out-of-band energy, probe spacing and catalogue
hashes. It writes measurements to `validation/reports/signals.json` and reports
any failed requirement. Add `--root PATH` to check a separate generation directory.

The reference tone must meet these spectral limits:

- At least 100 dB rejection outside 200–600 Hz, measured over the complete tone,
  including its start and finish.
- Steady-state harmonics 2–9 combined below −110 dBR, relative to the fundamental.

The [design background](../DESIGN.md#a-stable-level-reference) explains how these
limits support the intended level and distortion measurements.

For byte-for-byte reproduction, also compare the generated WAVs with the original
release's checksums. The generator writes a new `SHA256SUMS`, so keep the original
checksum file separately.

## Run the script tests

```sh
uv run --locked python -m unittest discover -s rew/tests
uv run --locked python -m unittest discover -s validation/tests
```

The tests use simulated API/audio responses and saved samples. They cover invalid
responses, version mismatches, missing devices, capture errors, altered files,
abrupt tone gating, missing probes and reproduction from saved recordings.

## Release reports

- [signals.json](reports/signals.json): measurements of the published WAVs.
- [reproduction.json](reports/reproduction.json): independent REW recapture measurements.
- [rew-api-5.40-beta101.json](reports/rew-api-5.40-beta101.json): API operations available in the release baseline.
- [hosted.json](reports/hosted.json): public-download checksum verification.

To repeat the download check:

```sh
uv run --locked python validation/src/verify_downloads.py
```

This fetches the URLs in `catalogue.json` anonymously and compares them with the
local files.

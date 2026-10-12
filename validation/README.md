# Check the reference files

These tools check the audio stored in the WAV files. They do not measure the
accuracy of a DAC, amplifier, audio input or meter.

## Check a downloaded release

Download `SHA256SUMS` alongside the six WAVs from the same release. In that download
directory, check that the files are unchanged. On macOS:

```sh
shasum -a 256 -c SHA256SUMS
```

On Linux, the equivalent command is `sha256sum -c SHA256SUMS`. This checks file
identity against the release; it does not measure signal quality.

## Measure the saved audio

First follow the [environment setup](../scripted/README.md#set-up-the-tools).
From the repository's top-level directory, run:

```sh
uv run --locked python validation/src/validate.py
```

The validator checks format, sample rate, duration, channel equality, peak level,
file and section boundaries, frequency, harmonics, out-of-band energy, probe
spacing and catalogue hashes. It prints the measurements and writes
`validation/reports/signals.json`. A failure stops with an explanation of the
failed requirement. For a separate generation directory, add `--root` followed
by its path.

For the reference tone, the recipe requires at least 100 dB rejection outside
200–600 Hz over the complete waveform, including its start and finish, without
an analysis window. Steady-state harmonics 2–9 combined must be below −110 dBR
(decibels relative to the fundamental). These are numerical limits: a
finite-duration waveform cannot have literally zero energy at every frequency
outside its passband.

Validation checks each file against its accompanying catalogue. After generating
new files, that catalogue contains new hashes. Passing validation therefore means
the new files meet the requirements; to establish byte-for-byte reproduction,
also compare with the original release's separately saved checksums.

## Run the script tests

```sh
uv run --locked python -m unittest discover -s rew/tests
uv run --locked python -m unittest discover -s validation/tests
```

These local tests use simulated API/audio responses and saved sample data; they
do not require REW or audio hardware. They cover invalid API responses, a REW
version differing from the selected recipe, missing capture devices, dropped
samples, invalid audio, altered files, abrupt tone gating, missing probes and
rebuilding from saved recordings.

## Read the release reports

- [signals.json](reports/signals.json): measurements of the published WAVs,
  identified by their hashes.
- [reproduction.json](reports/reproduction.json): an independent fresh REW capture
  assessed against the same requirements. Its hashes describe that run.
- [rew-api-5.40-beta101.json](reports/rew-api-5.40-beta101.json): the REW API
  operations inspected for the release baseline. An API inventory alone does
  not establish signal quality.
- [hosted.json](reports/hosted.json): checks that the public downloads match the
  local release files.

To repeat the public-download check, run:

```sh
uv run --locked python validation/src/verify_downloads.py
```

This downloads the URLs in `catalogue.json` without authentication and compares
the responses with the local files. It requires an internet connection.

# Qualification evidence

Reports belong here; waveform definitions and generation parameters belong in
their recipes. A capability inspection does not establish signal quality.

`reports/rew-api-5.40-beta101.json` records the actual installed REW API surface
inspected for ABX-F022. Reproduce it with the command in `rew/README.md`.
`reports/signals.json` measures the retained deliverable WAVs; `reproduction.json`
records a separate REW capture run assessed against the same limits. Its hashes
identify that independent run, not the deliverables in the catalogue.

From the collection root, run:

```sh
uv run python validation/src/validate.py
uv run python -m unittest discover -s rew/tests
uv run python -m unittest discover -s validation/tests
```

Checks cover exact format/rate/frame count, identical channels, peak, file and
section boundaries, steady frequency/harmonics, whole-tone out-of-band energy,
probe spacing and content hashes. Negative tests reject abrupt tone gating,
missing probes, short source captures, altered source/export bytes, wrong REW
version, missing virtual devices, dropped samples, silent/clipped/nonfinite audio
and unequal channels. Generation and validation require no controller code.

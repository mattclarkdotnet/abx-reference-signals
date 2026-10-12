# Shaped files and sequences

Run from the collection directory after REW capture:

```sh
uv run python scripted/src/generate.py
uv run python validation/src/validate.py
```

The authoritative recipe is `recipes/reference-v1.json`. It defines durations,
levels, channel variants and the numerical reference-tone spectral mask. Published
files are PCM24, rounded to the nearest sample value. The long tone is 30 seconds;
the combined sequence is ten seconds. Every channel contains the same simultaneous
signal. Eight-channel files require the user's player to route the desired channels.

The tone is taken from the settled REW capture, given guard silence and cosine
ramps, then band-pass filtered with a Kaiser FIR. Guard intervals retain both
filter tails. The complete onset/offset must have at least 100 dB rejection outside
200–600 Hz; the steady section's harmonics 2–9 must total below −110 dBR. Exact
parameters and file section boundaries are in the recipe and generated catalogue.

Timing sections retain complete REW bursts and are cut between them. The combined
file uses shortened tone and probe sections. Digital peaks are normalised to
−12 dBFS after shaping; this is not a promise of an analogue output voltage.

Generation produces files and a catalogue but does not by itself qualify them.
The validator reads the actual PCM, and controller tests must additionally pass
those samples through the production acquisition estimators and workflow.

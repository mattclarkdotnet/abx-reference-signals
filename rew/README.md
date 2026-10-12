# REW API tools

REW is the reference signal implementation. The intended workflow generates and
captures its virtual audio output under API control, with the scripts and recipes
retained here. The path is REW → BlackHole 2ch → sounddevice capture → float32 WAV.
No microphone, physical output or OS default audio device is used.

## Inspect an installation

Start a dedicated REW instance using its documented API options. For the current
macOS installation:

```sh
open -n -a /Applications/REW/REW.app --args -api -port 4736 -nogui
```

From the collection directory:

```sh
uv run python rew/src/inspect_api.py --base-url http://127.0.0.1:4736 \
  --output validation/reports/rew-api.json
```

This issues GET requests only. It records the version, served API fingerprint,
generator endpoints, available commands and export-related operations for review.
A successful inspection means the API was read; it does **not** mean WAV export
is supported or a signal has passed validation. Report files are written only
after all requests and response-shape checks succeed.

The selected port must belong to the intended instance. REW can choose a different
port if the requested one is occupied. No script should stop an instance it did
not start. For a dedicated instance started as above, shut it down after inspection
using the documented application command:

```sh
curl --fail -H 'Content-Type: application/json' \
  --data '{"command":"Shutdown"}' http://127.0.0.1:4736/application/command
```

See the [REW API documentation](https://www.roomeqwizard.com/betahelp/help/html/api.html).

## Generate source captures

The checked installation reports `5.40 Beta 101 API 0.9.0`; its generator command
list is `Play`, `Stop`. The full served API has no generator file-export endpoint,
so direct API export is replaced by virtual-device capture.

Install BlackHole 2ch, then restart the dedicated REW instance so it sees the new
device. The driver must be available to REW and PortAudio. From this directory's
parent, run:

```sh
uv run python rew/src/capture.py
```

The recipe in `recipes/capture.json` sets every relevant generator option and
captures a long 400 Hz sine and repeated timing bursts. This is generation on
the developer machine, separate from playback through DUTs. Float32 source WAVs
retain the complete capture, including startup padding; downstream scripts make
the shaped PCM24 reference files. The script refuses to overwrite retained files.
Use `--output` for an independent reproduction and compare signal measurements.

Qualified capture environment: macOS 27.2, BlackHole 2ch 0.7.1, the REW version
in the recipe, and the Python/PortAudio packages resolved by `uv.lock` and the
capture sidecars. macOS Microphone permission is also required for recording a
virtual input: enable it for the terminal/host application running this command
and restart that application after changing permission. No physical input is used.
If a capture is interrupted by forcibly closing the host, stop the dedicated
generator through `/generator/command` with `{"command":"Stop"}` before retrying.

REW requires whole milliseconds for this burst setting. The retained recipe uses
a 1 kHz, 1 ms cosine-windowed burst every 250 ms. The first second of the raw burst
capture can contain the preceding generator's drain; the derivative selects
settled repeated bursts after it and cuts halfway between bursts.

Generation scripts must set all relevant options, read back effective settings,
wait for completed capture, and validate samples. A dropped sample, conversion,
wrong device, clipping or unequal stereo channels invalidates the capture. Retain
unmodified REW outputs separately from later shaping, expansion or composition.

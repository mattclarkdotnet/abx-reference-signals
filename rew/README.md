# Make fresh source recordings with REW

The capture script controls [Room EQ Wizard (REW)](https://www.roomeqwizard.com/)
through its API and records its sine and burst generators through a virtual
audio device:

**REW → BlackHole 2ch → Python recorder → float32 WAV**

## Install the capture tools

1. Install **REW** from its [download page](https://www.roomeqwizard.com/), choosing
   a build with the [documented API](https://www.roomeqwizard.com/betahelp/help/html/api.html).
   The REW site also links to beta downloads.
2. Install **BlackHole 2ch** using its
   [installation instructions](https://github.com/ExistentialAudio/BlackHole#installation-instructions).
   Complete any requested restart, then restart REW so it sees the device.
3. Set up the [uv/Python environment](../scripted/README.md#set-up-the-tools).
4. In macOS **Privacy & Security → Microphone**, allow the terminal or application
   running the recorder to record audio. This permission covers virtual inputs.
   Restart that application after changing the permission.

See the [release baseline](../scripted/README.md#release-generation-baseline) for
the versions used. The supplied recorder uses macOS/CoreAudio and selects
`BlackHole 2ch`, with two input channels at 48 kHz. Another platform or loopback
driver requires adapting its device selection and stream settings.

## Start and inspect REW

Run commands from the repository's top-level directory. Start a dedicated REW
instance with its API on port 4736:

```sh
open -n -a REW.app --args -api -port 4736 -nogui
```

If macOS cannot find the application by name, replace `REW.app` with its installed
path. If the port is occupied, REW may choose another; use the actual port in
`--base-url` below. See [REW's API guide](https://www.roomeqwizard.com/betahelp/help/html/api.html)
for startup options.

```sh
uv run --locked python rew/src/inspect_api.py \
  --base-url http://127.0.0.1:4736 \
  --output reproduction/rew-api.json
```

The report records the REW version and available API operations.

## Choose a capture recipe

Copy the recipe:

```sh
cp rew/recipes/capture.json reproduction/capture.json
```

Set `rew_version` in `reproduction/capture.json` to the `rew_version` value in
your inspection report. The script checks this value and the effective generator
settings before recording.

The recipe specifies a long 400 Hz sine and repeated 1 kHz, one-millisecond
cosine-windowed bursts every 250 ms.

## Record and generate files

```sh
uv run --locked python rew/src/capture.py \
  --base-url http://127.0.0.1:4736 \
  --recipe reproduction/capture.json \
  --output reproduction/rew/files
```

The script records both signals as float32 WAVs, with JSON files containing their
settings and hashes. It refuses to overwrite existing recordings; choose a fresh
output directory for each run.

Copy the processing recipe, then generate and validate the reference files:

```sh
mkdir -p reproduction/scripted/recipes
cp scripted/recipes/reference-v1.json reproduction/scripted/recipes/
uv run --locked python scripted/src/generate.py --root reproduction
uv run --locked python validation/src/validate.py --root reproduction
```

WAVs are written to `reproduction/scripted/files/`, with measurements in
`reproduction/validation/reports/signals.json`. For publication, set the version,
repository and release tag in the copied processing recipe; see
[publication instructions](../CONTRIBUTING.md#publish-a-release).

## Stop the dedicated instance

```sh
curl --fail -H 'Content-Type: application/json' \
  --data '{"command":"Shutdown"}' http://127.0.0.1:4736/application/command
```

If recording is interrupted, stop the generator before retrying:

```sh
curl --fail -H 'Content-Type: application/json' \
  --data '{"command":"Stop"}' http://127.0.0.1:4736/generator/command
```

If a capture contains silence, check recording permission and that both REW and
the recorder can see BlackHole 2ch.

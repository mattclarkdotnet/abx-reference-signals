# Make fresh source recordings with REW

[Room EQ Wizard (REW)](https://www.roomeqwizard.com/) supplies the sine and burst
generators used as the reference implementation for this collection. A script
controls its generator through the local API and records its output through a
virtual audio device:

**REW → audio loopback driver → Python recorder → float32 WAV**

This is an optional way to reproduce the source material. To use the published
WAVs, just [download them](../README.md#download). To rebuild from the recordings
already included in the repository, use the [rebuild instructions](../scripted/README.md).

## Install the capture tools

1. Install **REW** from its [download page](https://www.roomeqwizard.com/), choosing
   a build with the [documented API](https://www.roomeqwizard.com/betahelp/help/html/api.html).
   The release baseline used a beta build; the REW site links to beta downloads.
   REW is a separate application and is not installed by the Python setup.
2. For the supplied macOS capture script, install **BlackHole 2ch**, a virtual
   driver that passes audio between applications. Follow its
   [installation instructions](https://github.com/ExistentialAudio/BlackHole#installation-instructions),
   including any requested restart, then restart REW so it sees the device.
3. Set up the repository's **uv/Python environment** using the
   [rebuild setup instructions](../scripted/README.md#set-up-the-tools).
4. In macOS **Privacy & Security → Microphone**, allow the terminal or application
   running the recorder to record audio. This permission also covers virtual
   inputs. Restart that application after changing the permission.

The [release generation baseline](../README.md#release-generation-baseline) lists
the REW, BlackHole and Python versions used for the latest release. Exact versions
are recorded for reproducibility, not as general installation requirements.
The current recorder uses macOS/CoreAudio and explicitly selects `BlackHole 2ch`;
it does not select the system's default device. Another platform or loopback driver
requires adapting that recorder's device selection and stream settings.

## Start and inspect REW

Run commands from the repository's top-level directory. On macOS, start a
dedicated REW instance with its API on port 4736:

```sh
open -n -a REW.app --args -api -port 4736 -nogui
```

If macOS cannot find the application by name, replace `REW.app` with its installed
path. Port 4736 is an example chosen for these scripts, not REW's default. REW may
choose another port if it is occupied; use the actual port in `--base-url` below.
See [REW's API guide](https://www.roomeqwizard.com/betahelp/help/html/api.html) for
startup options and enabling the API from its preferences.

```sh
uv run --locked python rew/src/inspect_api.py \
  --base-url http://127.0.0.1:4736 \
  --output reproduction/rew-api.json
```

The report records the version and available API operations without starting
playback. In the release baseline, the API supported generator configuration and
Play/Stop but offered no generator WAV-export operation. That is why these scripts
record the virtual audio output rather than request an exported WAV.

## Choose a capture recipe

Make a local copy of the recipe:

```sh
cp rew/recipes/capture.json reproduction/capture.json
```

The capture script checks that `rew_version` in this recipe matches the version
reported by REW. When using a different build, set `rew_version` in
`reproduction/capture.json` to the `rew_version` value from your inspection report.
This records the build you are actually testing; it does not establish API or
signal compatibility. The script also checks the effective generator settings,
and the resulting files must pass validation. Keep the release recipe unchanged.

No BlackHole patch-version check is imposed. Its selected device must expose two
input channels at 48 kHz without conversion. The supplied recipe defines a long
400 Hz sine and repeated 1 kHz, one-millisecond cosine-windowed bursts every
250 ms; the later processing script selects settled sections of these recordings.

## Record and build

```sh
uv run --locked python rew/src/capture.py \
  --base-url http://127.0.0.1:4736 \
  --recipe reproduction/capture.json \
  --output reproduction/rew/files
```

The script configures both output channels, checks the settings, starts REW's
generator, records each signal and stops playback. It saves unmodified float32
WAVs plus JSON files describing the actual settings and content hashes. It rejects
dropped samples, silence, clipping and unequal channels, and refuses to overwrite
an existing capture. Choose another output directory for a second attempt.

To turn the new recordings into playable reference files, copy the processing
recipe into the new working directory and run the generator and validator:

```sh
mkdir -p reproduction/scripted/recipes
cp scripted/recipes/reference-v1.json reproduction/scripted/recipes/
uv run --locked python scripted/src/generate.py --root reproduction
uv run --locked python validation/src/validate.py --root reproduction
```

The new files are in `reproduction/scripted/files/`, with their measurements in
`reproduction/validation/reports/signals.json`. The copied recipe retains the
original release download URLs; for a new public collection, update its version,
repository and release tag before publishing. [Contributor instructions](../CONTRIBUTING.md)
describe that step.

Raw recordings include startup padding and may contain audio draining from the
previous generator setting. The processing script excludes the first second of
active sine material and the first second of the burst recording, then retains
whole probes. Fresh recordings need to meet the numerical requirements; their
bytes need not match the release recordings.

## Stop the dedicated instance

After capture, close the REW instance started for this work:

```sh
curl --fail -H 'Content-Type: application/json' \
  --data '{"command":"Shutdown"}' http://127.0.0.1:4736/application/command
```

If the recorder was interrupted before it could stop playback, stop the generator
first using `/generator/command` with `{"command":"Stop"}`. If no signal is
captured, check recording permission and that both REW and the recorder can see
BlackHole 2ch; changing the system's default output is not needed.

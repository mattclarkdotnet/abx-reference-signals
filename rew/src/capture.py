"""Generate with the REW API and retain unmodified virtual-device captures."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
from threading import Event
import time

import numpy as np
import sounddevice as sd
import soundfile as sf

from inspect_api import Api, InspectionError

ROOT = Path(__file__).resolve().parents[2]


def get(api, path):
    return api.read(path)[0]


def set_value(api, path, value, method="POST"):
    return api.request(path, value, method)[0]


def wait_for(api, path, expected, timeout=10):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = get(api, path)
        if value == expected:
            return value
        time.sleep(0.05)
    raise InspectionError(f"{path}: did not become {expected!r}; last value was {value!r}")


def select_loopback(name):
    # Exact explicit virtual device only. Never use an OS default or microphone.
    if name != "BlackHole 2ch":
        raise InspectionError("This capture recipe is qualified only for BlackHole 2ch")
    matches = [(i, d) for i, d in enumerate(sd.query_devices()) if d["name"] == name]
    if len(matches) != 1 or matches[0][1]["max_input_channels"] != 2:
        raise InspectionError("Install BlackHole 2ch and restart the audio applications before capture")
    return matches[0][0]


def capture_samples(api, device, frames, sample_rate):
    """Capture a bounded float32 stream; any dropped samples invalidate the run."""
    samples = np.empty((frames, 2), dtype=np.float32)
    offset = 0
    failed = False
    complete = Event()

    def receive(data, count, _timestamps, status):
        nonlocal offset, failed
        if status:
            failed = True
            raise sd.CallbackAbort
        take = min(count, frames - offset)
        samples[offset:offset + take] = data[:take]
        offset += take
        if offset == frames:
            raise sd.CallbackStop

    options = sd.CoreAudioSettings(change_device_parameters=True, fail_if_conversion_required=True)
    stream = sd.InputStream(
        device=device, samplerate=sample_rate, channels=2, dtype="float32",
        callback=receive, finished_callback=complete.set, extra_settings=options,
    )
    try:
        with stream:
            set_value(api, "/generator/command", {"command": "Play"})
            if not complete.wait(frames / sample_rate + 10):
                raise InspectionError("Virtual-device capture timed out")
    finally:
        set_value(api, "/generator/command", {"command": "Stop"})
    if failed or offset != frames:
        raise InspectionError("Capture lost samples or ended early; no file retained")
    if not np.isfinite(samples).all() or np.max(np.abs(samples)) >= 1:
        raise InspectionError("Capture contains invalid or clipped samples")
    if np.max(np.abs(samples)) < 0.01:
        raise InspectionError("No usable signal reached the virtual device")
    if not np.array_equal(samples[:, 0], samples[:, 1]):
        raise InspectionError("The captured stereo channels are not identical and aligned")
    return samples


def generate(api, recipe, output, selection=None):
    device = select_loopback(recipe["device"])
    version = get(api, "/version")["message"]
    if version != recipe["rew_version"]:
        raise InspectionError(f"Recipe requires {recipe['rew_version']}; found {version}")
    if get(api, "/generator/status").get("playing"):
        raise InspectionError("REW is already playing; use a dedicated idle instance")
    if recipe["device"] not in get(api, "/audio/java/output-devices"):
        raise InspectionError("REW cannot see BlackHole 2ch; restart the dedicated REW instance")
    set_value(api, "/audio/java/output-device", {"device": recipe["device"]})
    wait_for(api, "/audio/java/output-device", {"device": recipe["device"]})
    set_value(api, "/audio/samplerate", {"value": recipe["sample_rate"], "unit": "Hz"})
    rate = get(api, "/audio/samplerate")
    if rate.get("value") != recipe["sample_rate"]:
        raise InspectionError(f"REW did not accept the sample rate: {rate}")
    set_value(api, "/audio/java/output-channel", {"channel": "L+R"})
    wait_for(api, "/audio/java/output-channel", {"channel": "L+R"})
    set_value(api, "/generator/invert-second-output", False)
    set_value(api, "/generator/level", recipe["level"])
    # Shared generator options must not inherit dither/distortion from past use.
    set_value(api, "/generator/signals/sine/configuration", recipe["captures"][0]["configuration"])
    output.mkdir(parents=True, exist_ok=True)
    for entry in recipe["captures"]:
        if selection is not None and entry["id"] != selection:
            continue
        destination = output / f"{entry['id']}.wav"
        if destination.exists() or destination.with_suffix(".json").exists():
            raise InspectionError(f"Refusing to replace a retained capture: {destination}")
        set_value(api, "/generator/signal", {"signal": entry["signal"]})
        set_value(api, "/generator/signal/configuration", entry["configuration"])
        effective = get(api, "/generator/signal/configuration")
        for key, expected in entry["configuration"].items():
            if effective.get(key) != expected:
                raise InspectionError(f"REW changed {key}: expected {expected!r}, got {effective.get(key)!r}")
        # Recheck the output immediately before playback; never rely on OS defaults.
        wait_for(api, "/audio/java/output-device", {"device": recipe["device"]})
        print(f"Capturing {entry['id']} through {recipe['device']}…", flush=True)
        samples = capture_samples(api, device, entry["capture_seconds"] * recipe["sample_rate"], recipe["sample_rate"])
        # Float source archive preserves every captured sample. Published derivatives are PCM24.
        sf.write(destination, samples, recipe["sample_rate"], subtype="FLOAT")
        provenance = {
            "generator": "REW", "rew_version": version,
            "recipe": entry, "effective_configuration": effective,
            "level": get(api, "/generator/level"), "device": recipe["device"],
            "sample_rate": recipe["sample_rate"], "frames": len(samples), "channels": 2,
            "capture_format": "float32", "portaudio": sd.get_portaudio_version()[1],
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        }
        destination.with_suffix(".json").write_text(json.dumps(provenance, indent=2) + "\n")
        print(f"Retained {destination}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:4736")
    parser.add_argument("--recipe", type=Path, default=ROOT / "rew/recipes/capture.json")
    parser.add_argument("--output", type=Path, default=ROOT / "rew/files")
    parser.add_argument("--signal", choices=["sine-400hz", "timing-burst"])
    args = parser.parse_args()
    try:
        generate(Api(args.base_url), json.loads(args.recipe.read_text()), args.output, args.signal)
    except (InspectionError, OSError, ValueError, sd.PortAudioError) as exc:
        print(f"REW capture failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Compose bounded, shaped reference files from retained REW captures."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import signal
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_capture(path, rate):
    provenance = json.loads(path.with_suffix(".json").read_text())
    if digest(path) != provenance["sha256"]:
        raise ValueError(f"Source capture hash changed: {path}")
    data, actual_rate = sf.read(path, dtype="float64", always_2d=True)
    if actual_rate != rate or data.shape[1] != 2 or not np.isfinite(data).all():
        raise ValueError(f"Invalid capture format: {path}")
    if not np.array_equal(data[:, 0], data[:, 1]):
        raise ValueError(f"Unequal capture channels: {path}")
    return data[:, 0], provenance


def active_start(data):
    points = np.flatnonzero(np.abs(data) > 0.01)
    if not len(points):
        raise ValueError("Source capture has no signal")
    return int(points[0])


def shaped_tone(raw, seconds, rate, config):
    length = round(seconds * rate)
    # One second after first activity excludes REW/device startup from the source.
    start = active_start(raw) + rate
    source = raw[start:start + length].copy()
    if len(source) != length:
        raise ValueError("Reference capture is too short")
    guard = round(config["guard_seconds"] * rate)
    ramp = round(config["ramp_seconds"] * rate)
    envelope = np.ones(length)
    envelope[:guard] = 0
    envelope[-guard:] = 0
    fade = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, ramp))
    envelope[guard:guard + ramp] = fade
    envelope[-guard-ramp:-guard] = fade[::-1]
    low_stop, high_stop = config["stopband_edges_hz"]
    low_pass, high_pass = config["passband_hz"]
    width = min(low_pass - low_stop, high_stop - high_pass)
    taps, beta = signal.kaiserord(config["filter_rejection_db"], width / (rate / 2))
    taps |= 1
    if taps // 2 >= guard:
        raise ValueError("Tone guard cannot contain the complete filter tail")
    kernel = signal.firwin(
        taps, [(low_stop + low_pass) / 2, (high_stop + high_pass) / 2],
        window=("kaiser", beta), pass_zero=False, fs=rate,
    )
    # Centred FIR convolution; guard silence retains both finite filter tails.
    return signal.fftconvolve(source * envelope, kernel, mode="same")


def timing_section(raw, seconds, rate):
    # Cut halfway between repeated 250 ms probes, never through the burst.
    # REW's previous output can drain after Stop. Ignore the first second of
    # the unmodified capture before finding a settled repeated probe.
    start = rate + active_start(raw[rate:]) + round(0.125 * rate)
    length = round(seconds * rate)
    result = raw[start:start + length].copy()
    if len(result) != length:
        raise ValueError("Timing capture is too short")
    if np.max(np.abs(np.concatenate([result[:100], result[-100:]]))) > 1e-6:
        raise ValueError("Timing section boundaries are not silent")
    return result


def normalise(data, peak_dbfs):
    maximum = float(np.max(np.abs(data)))
    if not 0 < maximum < 1:
        raise ValueError("Invalid source peak")
    return data * (10 ** (peak_dbfs / 20) / maximum)


def build(root=ROOT):
    recipe_path = root / "scripted/recipes/reference-v1.json"
    config = json.loads(recipe_path.read_text())
    rate = config["sample_rate"]
    sine_path = root / "rew/files/sine-400hz.wav"
    probe_path = root / "rew/files/timing-burst.wav"
    sine, _ = load_capture(sine_path, rate)
    probe, _ = load_capture(probe_path, rate)
    tone = normalise(shaped_tone(sine, config["reference_seconds"], rate, config["tone"]), config["peak_dbfs"])
    timing = normalise(timing_section(probe, config["timing_seconds"], rate), config["peak_dbfs"])
    sections = config["sequence_seconds"]
    parts = [
        np.zeros(round(rate * sections["lead"])),
        normalise(shaped_tone(sine, sections["tone"], rate, config["tone"]), config["peak_dbfs"]),
        np.zeros(round(rate * sections["gap"])),
        normalise(timing_section(probe, sections["timing"], rate), config["peak_dbfs"]),
        np.zeros(round(rate * sections["tail"])),
    ]
    boundaries = np.cumsum([0, *(len(part) for part in parts)]).tolist()
    combined = np.concatenate(parts)
    if len(combined) != 10 * rate:
        raise ValueError("Complete characterisation must occupy ten seconds")
    files = []
    out = root / "scripted/files"
    out.mkdir(parents=True, exist_ok=True)
    for identifier, data in [("reference-400hz", tone), ("timing-probe", timing), ("complete-characterisation", combined)]:
        for channels in config["channel_variants"]:
            filename = f"{identifier}-{channels}ch-48k-v{config['version']}.wav"
            path = out / filename
            expanded = np.repeat(data[:, None], channels, axis=1)
            expanded = np.rint(expanded * 8_388_608) / 8_388_608
            sf.write(path, expanded, rate, subtype="PCM_24")
            files.append({
                "id": identifier, "channels": channels,
                "path": str(path.relative_to(root)), "sha256": digest(path),
                "sample_rate": rate, "format": "PCM_24", "frames": len(data),
                "url": f"https://github.com/{config['github_repository']}/releases/download/{config['release_tag']}/{filename}",
                "source_sha256": [digest(p) for p in ([sine_path] if identifier == "reference-400hz" else [probe_path] if identifier == "timing-probe" else [sine_path, probe_path])],
                "sections": dict(zip(sections, zip(boundaries, boundaries[1:]))) if identifier == "complete-characterisation" else None,
            })
    catalogue = {
        "version": config["version"], "recipe": str(recipe_path.relative_to(root)),
        "recipe_sha256": digest(recipe_path), "generator_sha256": digest(Path(__file__)),
        "files": files,
    }
    (root / "catalogue.json").write_text(json.dumps(catalogue, indent=2) + "\n")
    (root / "SHA256SUMS").write_text("".join(f"{f['sha256']}  {Path(f['path']).name}\n" for f in files))
    return catalogue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    print(json.dumps(build(parser.parse_args().root), indent=2))

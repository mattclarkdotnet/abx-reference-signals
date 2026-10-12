"""Measure the delivered PCM, including full-envelope spectral rejection."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import signal
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def db(value):
    return float(20 * np.log10(max(float(value), 1e-20)))


def measure_tone(samples, rate, recipe):
    # No analysis window: include the actual saved onset and offset in the FFT.
    spectrum = np.fft.rfft(samples)
    frequencies = np.fft.rfftfreq(len(samples), 1 / rate)
    low, high = recipe["stopband_edges_hz"]
    outside = (frequencies < low) | (frequencies > high)
    total = np.sum(np.abs(spectrum) ** 2)
    rejection = db(np.sqrt(np.sum(np.abs(spectrum[outside]) ** 2) / total))
    if rejection > -recipe["minimum_out_of_band_rejection_db"]:
        raise ValueError(f"Reference onset/offset spectral rejection failed: {rejection:.2f} dBR")
    steady = samples[rate // 2:-rate // 2]
    rising = np.flatnonzero((steady[:-1] <= 0) & (steady[1:] > 0))
    crossings = rising - steady[rising] / (steady[rising + 1] - steady[rising])
    frequency = rate * (len(crossings) - 1) / (crossings[-1] - crossings[0])
    if abs(frequency - recipe["frequency_hz"]) > 0.01:
        raise ValueError(f"Reference frequency is {frequency:.5f} Hz")
    # Integer seconds at the declared 400 Hz avoids leakage into harmonic bins.
    steady = steady[:(len(steady) // rate) * rate]
    t = np.arange(len(steady)) / rate
    bins = [2 * abs(np.mean(steady * np.exp(-2j * np.pi * recipe["frequency_hz"] * h * t))) for h in range(1, 10)]
    distortion = db(np.linalg.norm(bins[1:]) / bins[0])
    if distortion > -recipe["minimum_harmonic_rejection_db"]:
        raise ValueError(f"Reference harmonic floor failed: {distortion:.2f} dBR")
    return {
        "frequency_hz": float(frequency), "steady_rms_dbfs": db(np.sqrt(np.mean(steady ** 2))),
        "harmonics_2_to_9_dbr": distortion, "whole_tone_out_of_band_dbr": rejection,
    }


def measure_probe(samples, rate):
    active = np.flatnonzero(np.abs(samples) > 0.02)
    if not len(active):
        raise ValueError("Missing timing probes")
    peaks = active[np.r_[True, np.diff(active) > rate * 0.1]]
    if len(peaks) < 10 or np.max(np.abs(np.diff(peaks) - rate / 4)) > 1:
        raise ValueError("Missing timing probes or incorrect probe spacing")
    # Basic independent timing check. Production estimator/workflow checks remain in Rust.
    centre = peaks[len(peaks) // 2]
    probe = samples[centre - 128:centre + 128]
    if len(probe) != 256:
        raise ValueError("Timing probe window is incomplete")
    correlation = signal.correlate(probe, probe, mode="full")
    correlation /= max(correlation)
    return {"probe_count": len(peaks), "period_frames": int(np.median(np.diff(peaks))),
            "adjacent_sample_correlation": float(correlation[len(probe)])}


def validate(root=ROOT):
    catalogue = json.loads((root / "catalogue.json").read_text())
    recipe_path = root / catalogue["recipe"]
    if sha256(recipe_path) != catalogue["recipe_sha256"]:
        raise ValueError("Generation recipe changed after catalogue creation")
    recipe = json.loads(recipe_path.read_text())
    reports = []
    for entry in catalogue["files"]:
        path = root / entry["path"]
        if sha256(path) != entry["sha256"]:
            raise ValueError(f"File content changed: {path}")
        info = sf.info(path)
        samples, rate = sf.read(path, dtype="float64", always_2d=True)
        if (info.subtype, rate, len(samples), samples.shape[1]) != ("PCM_24", 48000, entry["frames"], entry["channels"]):
            raise ValueError(f"Incorrect exported format: {path}")
        if not np.isfinite(samples).all() or not np.all(samples == samples[:, :1]):
            raise ValueError(f"Invalid or unequal channels: {path}")
        samples = samples[:, 0]
        peak = db(np.max(np.abs(samples)))
        if abs(peak - recipe["peak_dbfs"]) > 0.001:
            raise ValueError(f"Unexpected peak level: {peak}")
        if np.max(np.abs(np.r_[samples[:100], samples[-100:]])) > 1 / 8_388_608:
            raise ValueError(f"Abrupt file boundary: {path}")
        report = {"path": entry["path"], "sha256": entry["sha256"], "peak_dbfs": peak}
        if entry["id"] == "reference-400hz":
            report.update(measure_tone(samples, rate, recipe["tone"]))
        elif entry["id"] == "timing-probe":
            report.update(measure_probe(samples, rate))
        else:
            if len(samples) != rate * 10:
                raise ValueError("Combined file is not ten seconds")
            sections = entry["sections"]
            a, b = sections["tone"]
            report.update(measure_tone(samples[a:b], rate, recipe["tone"]))
            a, b = sections["timing"]
            report.update(measure_probe(samples[a:b], rate))
            for name in ("lead", "gap", "tail"):
                a, b = sections[name]
                if np.any(samples[a:b]):
                    raise ValueError(f"Non-silent {name} section")
        reports.append(report)
    result = {"catalogue_sha256": sha256(root / "catalogue.json"),
              "validator_sha256": sha256(Path(__file__)), "files": reports}
    output = root / "validation/reports/signals.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    print(json.dumps(validate(parser.parse_args().root), indent=2))

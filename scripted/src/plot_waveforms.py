"""Render README plots from the qualified PCM files, without modifying audio."""

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs" / "waveforms"
SIGNAL = "#00788A"
PROBE = "#B45B19"
INK = "#243842"


def load_signals():
    """Check every variant before using one shared channel for each plot."""
    catalogue = json.loads((ROOT / "catalogue.json").read_text())
    signals = {}
    for item in catalogue["files"]:
        path = ROOT / item["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Catalogue hash mismatch: {path}")
        info = sf.info(path)
        if (info.samplerate, info.frames, info.channels, info.subtype) != (
            item["sample_rate"], item["frames"], item["channels"], item["format"]
        ):
            raise ValueError(f"Catalogue format mismatch: {path}")
        samples, rate = sf.read(path, always_2d=True)
        if not np.all(samples == samples[:, :1]):
            raise ValueError(f"Channels differ; a shared plot would mislead: {path}")
        mono = samples[:, 0].copy()
        if item["id"] in signals:
            previous, previous_rate, previous_item = signals[item["id"]]
            if (
                rate != previous_rate
                or not np.array_equal(mono, previous)
                or item["sections"] != previous_item["sections"]
            ):
                raise ValueError(f"Variants differ; a shared plot would mislead: {path}")
        else:
            signals[item["id"]] = (mono, rate, item)
    return signals


def style_axes(ax, title, xlabel):
    ax.set_title(title, loc="left", fontweight="bold", pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Amplitude (full scale)")
    ax.set_ylim(-0.29, 0.29)
    ax.set_yticks([-0.25, 0, 0.25], ["−0.25", "0", "+0.25"])
    ax.spines[["top", "right"]].set_visible(False)
    ax.axhline(0, color="#9DAFB6", linewidth=0.65, zorder=0)
    ax.grid(axis="y", color="#E2E8EB", linewidth=0.6)


def envelope(ax, samples, rate, start=0, end=None, color=SIGNAL, scale=1, origin=0, fill=False):
    """Show per-column extrema so narrow pulses survive overview reduction."""
    if end is None:
        end = len(samples) / rate
    first, stop = round(start * rate), round(end * rate)
    window = samples[first:stop]
    stride = max(1, int(np.ceil(len(window) / 1800)))
    if fill:
        # A whole 400 Hz cycle per interval avoids partial-cycle striping in
        # the tone envelope. The detail plot separately shows actual samples.
        stride = max(stride, round(rate / 400))
    starts = np.arange(0, len(window), stride)
    lows = np.minimum.reduceat(window, starts)
    highs = np.maximum.reduceat(window, starts)
    if fill:
        edges = ((first + np.append(starts, len(window))) / rate - origin) * scale
        ax.fill_between(edges, np.append(lows, lows[-1]), np.append(highs, highs[-1]),
                        step="post", color=color, linewidth=0)
    else:
        # Vertical extrema spans retain positive and negative peaks independently.
        times = (first + starts + np.minimum(stride, len(window) - starts) / 2) / rate
        ax.vlines((times - origin) * scale, lows, highs, color=color, linewidth=0.8)
    ax.set_xlim((start - origin) * scale, (end - origin) * scale)


def samples_detail(ax, samples, rate, start, end, color=SIGNAL, origin=0):
    first, stop = round(start * rate), round(end * rate)
    times = (np.arange(first, stop) / rate - origin) * 1000
    ax.plot(times, samples[first:stop], color=color, linewidth=1.8)
    ax.set_xlim((start - origin) * 1000, (end - origin) * 1000)


def save(fig, name, title):
    fig.get_layout_engine().set(rect=(0, 0, 1, 0.89))
    fig.suptitle(title, x=0.055, y=0.98, va="top", ha="left", fontsize=19, fontweight="bold")
    # Fixed canvas: 10 inches at 200 dpi gives exactly 2000 pixels in width.
    path = OUTPUT / f"{name}.png"
    fig.savefig(path, dpi=200, facecolor="white", metadata={"Software": "Matplotlib"})
    plt.close(fig)
    print(path.relative_to(ROOT))


def reference_plot(signal):
    samples, rate, _ = signal
    duration = len(samples) / rate
    fig = plt.figure(figsize=(10, 6.2), layout="constrained")
    grid = fig.add_gridspec(2, 3, height_ratios=[1, 1])
    overview = fig.add_subplot(grid[0, :])
    style_axes(overview, f"Full {duration:g}-second file · amplitude envelope", "Time (s)")
    envelope(overview, samples, rate, fill=True)
    onset = fig.add_subplot(grid[1, 0])
    style_axes(onset, "Start · envelope", "Time from start (ms)")
    envelope(onset, samples, rate, 0, 0.35, scale=1000, fill=True)
    steady = fig.add_subplot(grid[1, 1])
    style_axes(steady, "Tone · samples", "Time within close-up (ms)")
    samples_detail(steady, samples, rate, 1, 1.015, origin=1)
    finish = fig.add_subplot(grid[1, 2])
    style_axes(finish, "Finish · envelope", "Time relative to end (ms)")
    envelope(finish, samples, rate, duration - 0.35, duration, scale=1000, origin=duration, fill=True)
    save(fig, "reference-400hz", "400 Hz reference tone")


def timing_plot(signal):
    samples, rate, _ = signal
    duration = len(samples) / rate
    fig, axes = plt.subplots(2, 1, figsize=(10, 6.2), layout="constrained")
    style_axes(axes[0], f"Full {duration:g}-second file · peak-preserving overview", "Time (s)")
    envelope(axes[0], samples, rate, color=PROBE)
    # Locate the actual first probe, rather than assuming a capture phase.
    first = np.flatnonzero(np.abs(samples) > np.max(np.abs(samples)) * 0.01)[0] / rate
    style_axes(axes[1], "One probe · actual samples", "Time from file start (ms)")
    samples_detail(axes[1], samples, rate, max(0, first - 0.001), first + 0.003, PROBE)
    save(fig, "timing-probe", "Timing and polarity probe")


def sequence_plot(signal):
    samples, rate, item = signal
    duration = len(samples) / rate
    sections = {name: (start / rate, end / rate) for name, (start, end) in item["sections"].items()}
    fig, axes = plt.subplots(2, 1, figsize=(10, 6.2), layout="constrained")
    style_axes(axes[0], f"Full {duration:g}-second sequence · amplitude envelope", "Time (s)")
    axes[0].set_xlim(0, duration)
    axes[0].set_xticks(np.arange(0, duration + 1))
    for name, color, label in [("tone", SIGNAL, "400 Hz tone"), ("timing", PROBE, "Timing probes")]:
        start, end = sections[name]
        envelope(axes[0], samples, rate, start, end, color, fill=name == "tone")
        axes[0].text((start + end) / 2, 0.31, label, ha="center", color=color, fontsize=11)
    axes[0].set_xlim(0, duration)
    axes[0].set_ylim(-0.29, 0.39)
    tone_end = sections["tone"][1]
    timing_start = sections["timing"][0]
    style_axes(axes[1], "From level measurement to timing · close-up", "Time from file start (s)")
    envelope(axes[1], samples, rate, tone_end - 0.5, tone_end, SIGNAL, fill=True)
    envelope(axes[1], samples, rate, timing_start, timing_start + 0.5, PROBE)
    axes[1].axvspan(tone_end, timing_start, color="#EDF0F2", zorder=-1)
    axes[1].text((tone_end + timing_start) / 2, 0.20, "Silence", ha="center", color=INK)
    axes[1].set_xlim(tone_end - 0.5, timing_start + 0.5)
    save(fig, "complete-characterisation", "Complete DUT characterisation")


def main():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11, "text.color": INK,
        "axes.labelcolor": INK, "axes.edgecolor": "#A5B3BA",
        "xtick.color": INK, "ytick.color": INK,
        "figure.constrained_layout.h_pad": 0.16,
        "figure.constrained_layout.w_pad": 0.10,
    })
    signals = load_signals()
    expected = {"reference-400hz", "timing-probe", "complete-characterisation"}
    if set(signals) != expected:
        raise ValueError("Update the README plots to cover the changed catalogue")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    reference_plot(signals["reference-400hz"])
    timing_plot(signals["timing-probe"])
    sequence_plot(signals["complete-characterisation"])


if __name__ == "__main__":
    main()

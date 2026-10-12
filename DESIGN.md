# Signal design and measurement background

## Measurement intent

Audio comparisons benefit from establishing the same starting conditions on
each path. A level difference can affect a listening comparison; an inverted or
delayed channel changes how signals line up. Distortion measurements help identify
an unsuitable operating level or a problem in the signal path. This collection
provides repeatable stimuli for those preparation checks.

The two basic waveforms serve different measurements. A steady sine makes
amplitude and harmonics easy to observe over a settled interval. A brief event
provides a timing landmark. Combining them lets the same playback arrangement
serve both tasks, while standalone files give more time for individual checks.

## A stable level reference

The reference tone bridges two common ways of establishing level: an AC voltage
reading from a multimeter and a digital measurement of the recorded output. A
sine has a stable RMS level and a simple harmonic structure, so the same stimulus
also supports distortion measurements.

400 Hz is a practical choice for this shared role. Handheld multimeters often
have a narrower accurate AC range than an audio interface. For example, the
[Fluke 117 specification](https://www.fluke.com/en-us/product/electrical-testing/digital-multimeters/fluke-117)
gives its tighter AC-voltage accuracy through 500 Hz and a looser specification
from 500 Hz to 1 kHz. This illustrates the reason for choosing a lower reference
frequency; the applicable range still comes from the meter's specification.
At 400 Hz, harmonics 2–9 occupy 800–3600 Hz, making them accessible to ordinary
audio acquisition alongside the fundamental.

The complete playback envelope matters as well as the steady sine. Abrupt gating
spreads energy beyond the intended tone; even starting at a zero crossing can
introduce a sudden slope change. That extra energy can excite a different response
from the equipment during startup and shutdown. Smooth ramps and band limiting
keep the stimulus concentrated around 400 Hz throughout the file. The ramps are
excluded from steady level measurements.

The recipe therefore specifies a 300–500 Hz passband and out-of-band rejection
beyond 200–600 Hz. This leaves transition room around the reference while
suppressing content where its second and higher harmonics would be measured.
The saved waveform must have at least 100 dB integrated rejection outside that
band and a combined harmonic level below −110 dBR for harmonics 2–9. These limits
make the source's own residuals small relative to the intended checks. They are
measured in the [published PCM files](validation/reports/signals.json), including
the shaped start and finish for the out-of-band check.

Thirty seconds gives a person time to obtain a settled meter reading or repeat a
measurement. This duration serves manual work; it is longer than the tone section
needed by an already-running acquisition system.

## A recognisable timing event

A continuous 400 Hz sine repeats every 2.5 ms. Its phase can reveal a fractional
cycle shift, but cannot identify how many complete cycles have elapsed. A
half-cycle delay can also resemble a polarity reversal. Delay therefore needs
an identifiable event before polarity is interpreted.

The timing probe supplies a short, bipolar event: one millisecond of a
cosine-windowed 1 kHz burst. Its positive and negative lobes give a recognisable
shape for aligning two recordings and then comparing their signs. Returning to
silence keeps the event localised instead of leaving a sustained step applied to
the equipment. The smooth window reduces the abruptness of a rectangular pulse.
The burst deliberately occupies a wider frequency range than the level tone:
that time localisation is what makes it useful for timing.

The duration is a compromise between a sharp landmark and a signal carried
through an audio path, aimed at comparisons on roughly the millisecond scale.
Filtering in the equipment can change the burst shape, so the meaningful result
is the relative alignment of the observed outputs for this stimulus.

Repeating every 250 ms gives space around each response and multiple capture
opportunities without restarting playback. The four-second file contains sixteen
probes, allowing retries or measurements of several channel pairs. The repeated
pattern suits delays small enough to identify corresponding bursts; a delay of a
whole repetition period is ambiguous without another timing reference.

## A short coordinated sequence

The combined file is designed around one prepared measurement run. It uses the
same signal definitions as the standalone files, with shorter sections, so the
user can keep playback level and routing fixed throughout the checks.

Most of the ten-second budget goes to the tone. Its 5.5-second section leaves
about five seconds of steady signal for acquisition, averaging, level adjustment
and a repeat reading. The following 3.5-second probe section supplies fourteen
events for paired timing and polarity measurements. Repeated probes make it
possible to acquire different pairs on successive events while each pair retains
its own simultaneous time reference.

The opening half-second gives the playback chain time to settle. The quarter-
second gap distinguishes the two stages and separates the tone's decay from the
probes; the trailing silence leaves room for the last response to decay. The
[section boundaries](FILES.md#complete-sequence) make that allocation explicit.
The short sequence favours automated acquisition; the longer standalone tone
provides time for manual readings and adjustments.

## Shared amplitude and precision

All variants use the same digital level and sample format so channel layout and
file choice do not introduce an extra variable into the comparison. The −12 dBFS
peak leaves digital headroom for gain and transient peaks while maintaining a
substantial signal above the file's quantisation residuals. The steady sine is
approximately −15.01 dBFS RMS. Analogue test voltage is then set by the playback
chain, so the level and distortion results describe that chosen operating point.

48 kHz provides 120 samples per cycle of the reference tone and 48 samples across
the one-millisecond probe. It represents the low-order harmonics being checked
and gives sample spacing well below the timing scale of interest. Keeping one
sample rate makes the initial collection easier to use consistently. The
24-bit sample width keeps rounding errors small at the reduced test level,
preserving room to observe small harmonics. PCM WAV retains those samples
without a lossy codec changing the tone, transient or silence.

The release adds neither harmonic distortion nor dither to the source tone, and
the final PCM conversion rounds to the nearest 24-bit value. The intent is to
keep added broadband noise out of the reference and preserve silent intervals.
There is a trade-off: undithered quantisation can leave signal-correlated
residuals. Dither decorrelates that error by adding noise; REW documents its
benefit for very precise distortion measurements in its
[generator guidance](https://www.roomeqwizard.com/betahelp/help/html/siggen.html).
For these files, the choice is supported by measuring the residuals after
conversion: the standalone tone's harmonics 2–9 total about −144.7 dBR, and its
whole-file out-of-band energy is about −135.3 dBR. Both are below the collection's
limits. Here, accepting the remaining coherent residuals in exchange for omitting
added noise is supported by those measured margins at this stimulus and level.

Stereo and eight-channel files copy the same samples to every channel. This
gives each selected path the same excitation and timing, so measured differences
can be investigated in the playback, equipment and acquisition paths. The
eight-channel layout supports multichannel routing while retaining the same
reference waveform.

## Reproducible references

REW supplies a documented signal-generator implementation. Original recordings
are kept alongside recipes and shaping code so a release can be rebuilt from
the same source samples, or checked against fresh captures. This separates the
waveform definition from the practical details of any one capture environment.
Hashes identify the exact files used; numerical measurements establish their
signal properties. The [generation instructions](scripted/README.md) and
[validation guide](validation/README.md) describe how to repeat those checks.

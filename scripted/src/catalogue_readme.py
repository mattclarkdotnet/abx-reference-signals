"""Render the file guide and README downloads from the generated catalogue."""
import json
import math
from pathlib import Path

root = Path(__file__).resolve().parents[2]
catalogue = json.loads((root / 'catalogue.json').read_text())
recipe = json.loads((root / catalogue['recipe']).read_text())
names = {
    'reference-400hz': '400 Hz reference tone',
    'timing-probe': 'Timing and polarity probe',
    'complete-characterisation': 'Complete characterisation sequence',
}
sections = {
    'lead': 'Opening silence', 'tone': '400 Hz tone (including ramps)',
    'gap': 'Silence between signals', 'timing': 'Timing and polarity probes',
    'tail': 'Closing silence',
}

downloads = ['| Signal | Duration | Stereo | 8-channel |', '|---|---:|---|---|']
for identifier, name in names.items():
    variants = {f['channels']: f for f in catalogue['files'] if f['id'] == identifier}
    stereo, multichannel = variants[2], variants[8]
    duration = stereo['frames'] / stereo['sample_rate']
    downloads.append(
        f"| {name} | {duration:g} s | [Download WAV]({stereo['url']}) | [Download WAV]({multichannel['url']}) |"
    )
readme_path = root / 'README.md'
readme = readme_path.read_text()
start, end = '<!-- BEGIN SIGNAL DOWNLOADS -->', '<!-- END SIGNAL DOWNLOADS -->'
if readme.count(start) != 1 or readme.count(end) != 1 or readme.index(start) >= readme.index(end):
    raise ValueError('README must have one ordered pair of signal download markers')
before, rest = readme.split(start)
_, after = rest.split(end)
updated_readme = before + start + '\n\n' + '\n'.join(downloads) + '\n\n' + end + after

lines = ['# Downloadable files', '',
         'WAV references for measuring audio levels, distortion, relative delay and polarity.',
         'See the [waveform previews and usage guide](README.md#waveforms) to choose a signal.', '',
         f"All files are 24-bit PCM at {recipe['sample_rate'] / 1000:g} kHz, peak {recipe['peak_dbfs']:g} dBFS.",
         'Both variants carry identical, time-aligned signals on every channel.', '',
         '| Signal | Channels | Duration | Download |', '|---|---:|---:|---|']
for item in catalogue['files']:
    lines.append(f"| {names[item['id']]} | {item['channels']} | {item['frames'] / item['sample_rate']:g} s | [{Path(item['path']).name}]({item['url']}) |")
lines += ['', '## Complete sequence', '', '| Section | From | To |', '|---|---:|---:|']
complete = next(f for f in catalogue['files'] if f['id'] == 'complete-characterisation')
for name, (start, end) in complete['sections'].items():
    lines.append(f'| {sections[name]} | {start / complete["sample_rate"]:g} s | {end / complete["sample_rate"]:g} s |')
lines += ['', 'Measure levels and distortion during the steady section of the tone.',
          f"Its steady RMS level is approximately {recipe['peak_dbfs'] - 10 * math.log10(2):.2f} dBFS.", '']
(root / 'FILES.md').write_text('\n'.join(lines))
readme_path.write_text(updated_readme)

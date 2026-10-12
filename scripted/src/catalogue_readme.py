"""Render the human file guide from the authoritative generated catalogue."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
catalogue = json.loads((root / 'catalogue.json').read_text())
recipe = json.loads((root / catalogue['recipe']).read_text())
lines = ['# Downloadable files', '', 'Generated from `catalogue.json`; regenerate with `uv run python scripted/src/catalogue_readme.py`.', '',
         f"All files are PCM24 at {recipe['sample_rate']} Hz, peak {recipe['peak_dbfs']:g} dBFS.",
         'Every channel carries the same simultaneous signal. Choose stereo unless your source routes eight channels.', '',
         '| Signal | Channels | Duration | Download |', '|---|---:|---:|---|']
for item in catalogue['files']:
    lines.append(f"| {item['id']} | {item['channels']} | {item['frames'] / item['sample_rate']:g} s | [{Path(item['path']).name}]({item['url']}) |")
lines += ['', '## Complete sequence', '', '| Section | From | To |', '|---|---:|---:|']
complete = next(f for f in catalogue['files'] if f['id'] == 'complete-characterisation')
for name, (start, end) in complete['sections'].items():
    lines.append(f'| {name} | {start / complete["sample_rate"]:g} s | {end / complete["sample_rate"]:g} s |')
lines += ['', 'The tone includes guard silence and shaped ramps; measure the steady interior.',
          'The steady sine RMS is approximately 3.01 dB below its peak, before any analogue playback gain.',
          'The source equipment determines the analogue output voltage. Use the meter reading for voltage calibration.', '']
(root / 'FILES.md').write_text('\n'.join(lines))

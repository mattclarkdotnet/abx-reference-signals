"""Qualification failures must remain failures, including exported boundaries."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripted/src'), str(ROOT / 'validation/src'), str(ROOT / 'rew/src')]
import generate
import validate
import capture


class Signals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recipe = json.loads((ROOT / 'scripted/recipes/reference-v1.json').read_text())
        cls.tone, cls.rate = sf.read(ROOT / 'scripted/files/reference-400hz-2ch-48k-v0.1.0.wav')

    def test_delivered_tone_and_abrupt_cut(self):
        validate.measure_tone(self.tone[:, 0], self.rate, self.recipe['tone'])
        abrupt = self.tone[:, 0].copy()
        abrupt[:self.rate + 17] = 0
        with self.assertRaisesRegex(ValueError, 'spectral rejection'):
            validate.measure_tone(abrupt, self.rate, self.recipe['tone'])

    def test_missing_probes_and_incomplete_source(self):
        with self.assertRaises(ValueError):
            validate.measure_probe(np.zeros(self.rate), self.rate)
        with self.assertRaisesRegex(ValueError, 'too short'):
            generate.shaped_tone(self.tone[:self.rate, 0], 30, self.rate, self.recipe['tone'])

    def test_capture_never_falls_back_to_physical_or_default_input(self):
        with patch.object(capture.sd, 'query_devices', return_value=[{'name': 'Microphone', 'max_input_channels': 2}]):
            with self.assertRaises(capture.InspectionError):
                capture.select_loopback('BlackHole 2ch')
            with self.assertRaises(capture.InspectionError):
                capture.select_loopback('Microphone')

    def test_version_failure_retains_no_file(self):
        class WrongVersion:
            def read(self, path):
                return {'message': 'another REW version'}, b''
        with tempfile.TemporaryDirectory() as directory, patch.object(capture, 'select_loopback', return_value=6):
            with self.assertRaisesRegex(capture.InspectionError, 'requires'):
                capture.generate(WrongVersion(), json.loads((ROOT / 'rew/recipes/capture.json').read_text()), Path(directory))
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_invalid_captures_stop_generator_and_are_rejected(self):
        for problem in ['silence', 'clip', 'nonfinite', 'unequal', 'overrun']:
            samples = np.full((960, 2), .1, dtype=np.float32)
            if problem == 'silence': samples[:] = 0
            if problem == 'clip': samples[20] = 1
            if problem == 'nonfinite': samples[20] = np.nan
            if problem == 'unequal': samples[20, 1] = .2
            class Stream:
                def __init__(self, **options): self.options = options
                def __enter__(self):
                    try: self.options['callback'](samples, 960, None, problem == 'overrun')
                    except (capture.sd.CallbackStop, capture.sd.CallbackAbort): pass
                    self.options['finished_callback']()
                def __exit__(self, *_): pass
            with patch.object(capture.sd, 'InputStream', Stream), patch.object(capture, 'set_value') as api:
                with self.assertRaises(capture.InspectionError, msg=problem):
                    capture.capture_samples(None, 6, 960, 48000)
                self.assertEqual(api.call_args.args, (None, '/generator/command', {'command': 'Stop'}))

    def test_portable_regeneration_and_tamper_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for sub in ['rew/files', 'scripted/recipes']:
                shutil.copytree(ROOT / sub, root / sub)
            first = generate.build(root)
            second = generate.build(root)
            expected = json.loads((ROOT / 'catalogue.json').read_text())
            self.assertEqual([f['sha256'] for f in first['files']], [f['sha256'] for f in expected['files']])
            self.assertEqual(first, second)
            validate.validate(root)
            path = root / first['files'][0]['path']
            with path.open('r+b') as stream:
                stream.seek(-1, 2)
                stream.write(b'\xff')
            with self.assertRaisesRegex(ValueError, 'content changed'):
                validate.validate(root)
            source = root / 'rew/files/sine-400hz.wav'
            source.write_bytes(b'not the captured waveform')
            with self.assertRaisesRegex(ValueError, 'hash changed'):
                generate.build(root)


if __name__ == '__main__':
    unittest.main()

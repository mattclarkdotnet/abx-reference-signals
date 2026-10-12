"""Verify public release bytes without authentication or stored browser cookies."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]


def verify(root=ROOT):
    catalogue = json.loads((root / 'catalogue.json').read_text())
    results = []
    for file in catalogue['files']:
        if urlsplit(file['url']).scheme != 'https':
            raise ValueError('Published references require HTTPS')
        expected_size = (root / file['path']).stat().st_size
        digest = hashlib.sha256()
        size = 0
        with urlopen(file['url'], timeout=30) as response:
            while block := response.read(1024 * 1024):
                size += len(block)
                if size > expected_size:
                    raise ValueError(f"Download exceeds qualified size: {file['url']}")
                digest.update(block)
        if size != expected_size or digest.hexdigest() != file['sha256']:
            raise ValueError(f"Download differs from qualified file: {file['url']}")
        results.append({'url': file['url'], 'sha256': digest.hexdigest(), 'bytes': size})
        print(f"Verified {file['path']}", flush=True)
    output = root / 'validation/reports/hosted.json'
    output.write_text(json.dumps({'anonymous_downloads': results}, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    verify(parser.parse_args().root)

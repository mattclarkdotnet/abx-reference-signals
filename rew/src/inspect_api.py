"""Read REW's actual API surface without changing settings or starting playback."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


class InspectionError(Exception):
    """The API could not be inspected completely and reliably."""


class Api:
    def __init__(self, base_url: str, timeout: float = 5):
        parsed = urlsplit(base_url)
        if (
            parsed.scheme != "http"
            or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}
            or parsed.username is not None
            or parsed.path not in {"", "/"}
            or parsed.query
            or parsed.fragment
        ):
            raise InspectionError("Use the local REW API base URL, such as http://127.0.0.1:4735")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def read(self, path: str):
        return self.request(path)

    def request(self, path: str, data=None, method: str = "GET"):
        try:
            request = Request(
                self.base_url + path,
                data=None if data is None else json.dumps(data).encode(),
                headers={"Content-Type": "application/json"},
                method=method,
            )
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read(4 * 1024 * 1024 + 1)
            if len(raw) > 4 * 1024 * 1024:
                raise InspectionError(f"{path}: response exceeds 4 MiB")
            return json.loads(raw), raw
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise InspectionError(f"{path}: {exc}") from exc


def inspect(api: Api) -> dict:
    version, _ = api.read("/version")
    schema, schema_bytes = api.read("/doc.json")
    commands, _ = api.read("/generator/commands")
    application_commands, _ = api.read("/application/commands")
    if not isinstance(version, dict) or not isinstance(version.get("message"), str):
        raise InspectionError("/version: expected a version message")
    if not isinstance(schema, dict) or not isinstance(schema.get("paths"), dict):
        raise InspectionError("/doc.json: expected an OpenAPI paths object")
    for path, value in [
        ("/generator/commands", commands),
        ("/application/commands", application_commands),
    ]:
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise InspectionError(f"{path}: expected a list of command names")

    paths = schema["paths"]
    return {
        "rew_version": version["message"],
        "api_version": schema.get("info", {}).get("version"),
        "openapi_sha256": hashlib.sha256(schema_bytes).hexdigest(),
        "generator_commands": commands,
        "application_commands": application_commands,
        "generator_paths": sorted(path for path in paths if path.startswith("/generator/")),
        "file_related_paths": sorted(
            path for path in paths if any(word in path.lower() for word in ("file", "export", "wav", "save"))
        ),
        "interpretation": "API inventory only; WAV export and signal suitability require qualification.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:4735")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = inspect(Api(args.base_url))
        text = json.dumps(report, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text)
        else:
            print(text, end="")
        return 0
    except (InspectionError, OSError) as exc:
        print(f"REW API inspection failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""Transport and failure tests for the read-only REW inventory client."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from threading import Thread
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from inspect_api import Api, InspectionError, inspect


class InspectionTests(unittest.TestCase):
    def setUp(self):
        self.requests = []
        self.responses = {
            "/version": {"message": "fixture REW"},
            "/doc.json": {
                "info": {"version": "fixture API"},
                "paths": {"/generator/status": {}, "/import/rta-file": {}},
            },
            "/generator/commands": ["Play", "Stop"],
            "/application/commands": ["Shutdown"],
        }
        test = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                test.requests.append((self.command, self.path))
                if self.path not in test.responses:
                    self.send_error(404)
                    return
                self.send_response(200)
                self.end_headers()
                value = test.responses[self.path]
                self.wfile.write(value if isinstance(value, bytes) else json.dumps(value).encode())

            def log_message(self, *_):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.api = Api(f"http://127.0.0.1:{self.server.server_port}")

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def test_inventory_is_read_only_and_does_not_claim_export_support(self):
        report = inspect(self.api)
        self.assertEqual(report["generator_commands"], ["Play", "Stop"])
        self.assertEqual(report["generator_paths"], ["/generator/status"])
        self.assertIn("require qualification", report["interpretation"])
        self.assertTrue(all(method == "GET" for method, _ in self.requests))

    def test_missing_endpoint_and_invalid_json_fail(self):
        del self.responses["/generator/commands"]
        with self.assertRaisesRegex(InspectionError, "404"):
            inspect(self.api)
        self.responses["/generator/commands"] = b"not JSON"
        with self.assertRaisesRegex(InspectionError, "/generator/commands"):
            inspect(self.api)

    def test_incompatible_schema_and_command_shapes_fail(self):
        self.responses["/doc.json"] = {"paths": []}
        with self.assertRaisesRegex(InspectionError, "paths object"):
            inspect(self.api)
        self.responses["/doc.json"] = {"paths": {}}
        self.responses["/generator/commands"] = {"message": "not commands"}
        with self.assertRaisesRegex(InspectionError, "command names"):
            inspect(self.api)


if __name__ == "__main__":
    unittest.main()

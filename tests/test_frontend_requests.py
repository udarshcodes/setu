"""Exercise the text/media request branches without starting Streamlit or a backend."""
import ast
import math
from pathlib import Path
import unittest
from unittest.mock import Mock


class BackendTimeout(Exception):
    pass


class FrontendRequestsTest(unittest.TestCase):
    def test_text_and_media_requests_handle_success_and_failures(self):
        source = ast.parse((Path(__file__).resolve().parents[1] / "frontend/app.py").read_text(encoding="utf-8"))
        blocks = [node for node in ast.walk(source) if isinstance(node, ast.Try) and any(
            isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name) and call.func.value.id == "requests"
            and call.func.attr == "post" for call in ast.walk(node))]
        self.assertEqual(len(blocks), 2, "Exercise both text and media request paths")
        for block in blocks:
            code = compile(ast.fix_missing_locations(ast.Module(body=[block], type_ignores=[])), "<request-branch>", "exec")
            for outcome in ("success", "timeout", "http_error", "connection_error"):
                with self.subTest(line=block.lineno, outcome=outcome):
                    requests = Mock()
                    requests.Timeout = BackendTimeout
                    response = Mock(status_code=200 if outcome == "success" else 500, text="backend failed")
                    response.json.return_value = {"response": "answer"}
                    requests.post.return_value = response
                    if outcome == "timeout":
                        requests.post.side_effect = BackendTimeout()
                    elif outcome == "connection_error":
                        requests.post.side_effect = OSError("connection failed")
                    ui = Mock()
                    exec(code, {"requests": requests, "st": ui, "BACKEND_URL": "https://example.invalid",
                                "user_query": "test", "language_override": "English", "data": {}, "files": {}})
                    timeout = requests.post.call_args.kwargs.get("timeout")
                    self.assertIsInstance(timeout, (int, float))
                    self.assertTrue(math.isfinite(timeout) and timeout > 0)
                    if outcome == "success":
                        ui.write.assert_called_once_with("answer")
                        ui.error.assert_not_called()
                    else:
                        ui.error.assert_called_once()
                    if outcome == "timeout":
                        self.assertIn("try again", ui.error.call_args.args[0])


if __name__ == "__main__":
    unittest.main()

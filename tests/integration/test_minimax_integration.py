"""Integration tests for MiniMax provider: validate request shape and endpoint."""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch


def _setup_src():
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    for stub in ("numpy", "openai"):
        if stub not in sys.modules:
            sys.modules[stub] = MagicMock()


def _fresh_import(env: dict):
    """Import openai_api.openai with a clean environment."""
    _setup_src()
    for mod in list(sys.modules.keys()):
        if "openai_api" in mod:
            del sys.modules[mod]
    with patch.dict("os.environ", env, clear=True):
        import openai_api.openai as oai
    return oai


class TestMiniMaxRequestShape(unittest.TestCase):
    """Integration: verify the full HTTP request shape sent to MiniMax."""

    def _post_call(self, fn_name: str, env: dict, extra_fn_args=None):
        """Call fn_name on a freshly-imported module and capture POST arguments."""
        _setup_src()
        for mod in list(sys.modules.keys()):
            if "openai_api" in mod:
                del sys.modules[mod]

        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "test_result"}}]
        }

        with patch.dict("os.environ", env, clear=True), \
             patch("requests.post", return_value=mock_resp) as mock_post:
            import openai_api.openai as oai
            fn = getattr(oai, fn_name)
            fn(*(extra_fn_args or ["test prompt"]))

        return mock_post.call_args

    def test_ask_openai_common_minimax_url(self):
        env = {"MINIMAX_API_KEY": "mm-int-key", "LLM_PROVIDER": "minimax"}
        call = self._post_call("ask_openai_common", env)
        self.assertIn("api.minimax.io", call[0][0])
        self.assertIn("/v1/chat/completions", call[0][0])

    def test_detect_vulnerabilities_minimax_url(self):
        env = {"MINIMAX_API_KEY": "mm-int-key", "LLM_PROVIDER": "minimax"}
        call = self._post_call("detect_vulnerabilities", env)
        self.assertIn("api.minimax.io", call[0][0])

    def test_perform_initial_vulnerability_validation_minimax_url(self):
        env = {"MINIMAX_API_KEY": "mm-int-key", "LLM_PROVIDER": "minimax"}
        call = self._post_call("perform_initial_vulnerability_validation", env)
        self.assertIn("api.minimax.io", call[0][0])

    def test_request_body_has_messages(self):
        env = {"MINIMAX_API_KEY": "mm-int-key", "LLM_PROVIDER": "minimax"}
        call = self._post_call("ask_openai_common", env)
        body = call[1]["json"]
        self.assertIn("messages", body)
        self.assertIn("model", body)

    def test_bearer_token_in_header(self):
        env = {"MINIMAX_API_KEY": "mm-secret-xyz", "LLM_PROVIDER": "minimax"}
        call = self._post_call("ask_openai_common", env)
        headers = call[1]["headers"]
        self.assertEqual(headers["Authorization"], "Bearer mm-secret-xyz")

    def test_auto_detect_without_provider_env(self):
        """MINIMAX_API_KEY alone (no LLM_PROVIDER) auto-detects MiniMax."""
        env = {"MINIMAX_API_KEY": "mm-auto-key"}
        call = self._post_call("ask_openai_common", env)
        self.assertIn("api.minimax.io", call[0][0])


class TestMiniMaxModelConfig(unittest.TestCase):
    """Integration: MiniMax models are reachable via model_config.json override."""

    def test_get_model_with_minimax_model_in_config(self):
        """If model_config.json contains MiniMax models, get_model returns them."""
        import json
        import tempfile

        config = {
            "openai_general": "MiniMax-M2.7",
            "vulnerability_detection": "MiniMax-M2.7",
            "structured_json_extraction": "MiniMax-M2.7-highspeed",
            "embedding_model": "text-embedding-3-large",
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as fh:
            json.dump(config, fh)
            tmp_path = fh.name

        _setup_src()
        for mod in list(sys.modules.keys()):
            if "openai_api" in mod:
                del sys.modules[mod]

        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}, clear=True), \
             patch("openai_api.openai._model_config", None), \
             patch("os.path.join", side_effect=lambda *a: tmp_path if a[-1] == "model_config.json" else os.path.join(*a)):
            import openai_api.openai as oai
            oai._model_config = config  # inject config directly
            self.assertEqual(oai.get_model("openai_general"), "MiniMax-M2.7")
            self.assertEqual(oai.get_model("vulnerability_detection"), "MiniMax-M2.7")
            self.assertEqual(oai.get_model("structured_json_extraction"), "MiniMax-M2.7-highspeed")

        os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()

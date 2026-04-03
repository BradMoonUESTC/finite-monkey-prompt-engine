"""Unit tests for MiniMax provider support in openai_api/openai.py."""

import importlib
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers to reload the openai module with a clean env each time
# ---------------------------------------------------------------------------

def _reload_openai_module(env_overrides: dict):
    """Reload openai_api.openai with the given environment variables."""
    env = {k: v for k, v in os.environ.items()}
    for key in ("OPENAI_API_BASE", "OPENAI_API_KEY", "MINIMAX_API_KEY", "LLM_PROVIDER"):
        env.pop(key, None)
    env.update(env_overrides)

    src_path = os.path.join(os.path.dirname(__file__), "..", "src")
    src_path = os.path.abspath(src_path)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    # Stub heavy optional deps so import doesn't fail in CI
    for stub_name in ("numpy", "openai"):
        if stub_name not in sys.modules:
            sys.modules[stub_name] = MagicMock()

    # Remove cached module so _init_llm_config() re-runs
    for mod_name in list(sys.modules.keys()):
        if "openai_api" in mod_name:
            del sys.modules[mod_name]

    with patch.dict("os.environ", env, clear=True):
        import openai_api.openai as oai  # noqa: F401 – loaded for side-effects
        # snapshot env *inside* the patched context
        captured = {
            "OPENAI_API_BASE": os.environ.get("OPENAI_API_BASE", ""),
            "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
        }
    return oai, captured


class TestClampTemperature(unittest.TestCase):
    """_clamp_temperature enforces MiniMax range (0.01, 1.0]."""

    def _get_clamp(self):
        src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        for stub in ("numpy", "openai"):
            if stub not in sys.modules:
                sys.modules[stub] = MagicMock()
        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}, clear=False):
            import openai_api.openai as oai
        return oai._clamp_temperature

    def test_zero_clamped_to_minimum(self):
        clamp = self._get_clamp()
        self.assertAlmostEqual(clamp(0.0), 0.01)

    def test_negative_clamped_to_minimum(self):
        clamp = self._get_clamp()
        self.assertAlmostEqual(clamp(-0.5), 0.01)

    def test_value_above_one_clamped_to_one(self):
        clamp = self._get_clamp()
        self.assertAlmostEqual(clamp(1.5), 1.0)

    def test_valid_value_unchanged(self):
        clamp = self._get_clamp()
        self.assertAlmostEqual(clamp(0.7), 0.7)

    def test_boundary_one_unchanged(self):
        clamp = self._get_clamp()
        self.assertAlmostEqual(clamp(1.0), 1.0)

    def test_low_positive_value_unchanged(self):
        clamp = self._get_clamp()
        self.assertAlmostEqual(clamp(0.01), 0.01)


class TestInitLlmConfigMiniMaxAutoDetect(unittest.TestCase):
    """_init_llm_config auto-configures MiniMax when MINIMAX_API_KEY is set alone."""

    def test_minimax_key_only_sets_base_and_key(self):
        """MINIMAX_API_KEY alone (no OPENAI_API_KEY) → OPENAI_API_BASE = api.minimax.io."""
        _, captured = _reload_openai_module({"MINIMAX_API_KEY": "mm-test-key"})
        self.assertEqual(captured["OPENAI_API_BASE"], "api.minimax.io")
        self.assertEqual(captured["OPENAI_API_KEY"], "mm-test-key")

    def test_both_keys_openai_takes_priority(self):
        """When both OPENAI_API_KEY and MINIMAX_API_KEY are set, OpenAI key is preserved."""
        _, captured = _reload_openai_module(
            {"OPENAI_API_KEY": "sk-openai", "MINIMAX_API_KEY": "mm-key"}
        )
        # OPENAI_API_KEY present → MiniMax auto-detect should NOT overwrite it
        self.assertEqual(captured["OPENAI_API_KEY"], "sk-openai")

    def test_no_minimax_key_no_change(self):
        """Without MINIMAX_API_KEY or LLM_PROVIDER, env is untouched."""
        _, captured = _reload_openai_module({"OPENAI_API_KEY": "sk-openai"})
        self.assertEqual(captured["OPENAI_API_KEY"], "sk-openai")

    def test_minimax_key_does_not_override_explicit_base(self):
        """Explicit OPENAI_API_BASE is preserved even when MINIMAX_API_KEY is set alone."""
        _, captured = _reload_openai_module(
            {"MINIMAX_API_KEY": "mm-test-key", "OPENAI_API_BASE": "my.proxy.com"}
        )
        # setdefault → must not overwrite an already-set base
        self.assertEqual(captured["OPENAI_API_BASE"], "my.proxy.com")


class TestInitLlmConfigLlmProvider(unittest.TestCase):
    """_init_llm_config respects explicit LLM_PROVIDER=minimax."""

    def test_llm_provider_minimax_routes_to_minimax(self):
        _, captured = _reload_openai_module(
            {"LLM_PROVIDER": "minimax", "MINIMAX_API_KEY": "mm-explicit-key"}
        )
        self.assertEqual(captured["OPENAI_API_BASE"], "api.minimax.io")
        self.assertEqual(captured["OPENAI_API_KEY"], "mm-explicit-key")

    def test_llm_provider_case_insensitive(self):
        _, captured = _reload_openai_module(
            {"LLM_PROVIDER": "MiniMax", "MINIMAX_API_KEY": "mm-key"}
        )
        self.assertEqual(captured["OPENAI_API_BASE"], "api.minimax.io")

    def test_llm_provider_openai_is_no_op(self):
        _, captured = _reload_openai_module(
            {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "sk-openai"}
        )
        self.assertEqual(captured["OPENAI_API_KEY"], "sk-openai")
        self.assertNotEqual(captured["OPENAI_API_BASE"], "api.minimax.io")


class TestGetModelConfig(unittest.TestCase):
    """get_model() returns configured model or falls back to gpt-4o-mini."""

    def _get_fn(self):
        src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        for stub in ("numpy", "openai"):
            if stub not in sys.modules:
                sys.modules[stub] = MagicMock()
        # Clean module cache
        for mod in list(sys.modules.keys()):
            if "openai_api" in mod:
                del sys.modules[mod]
        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}, clear=False):
            import openai_api.openai as oai
        return oai.get_model

    def test_known_key_returns_model(self):
        get_model = self._get_fn()
        model = get_model("openai_general")
        self.assertIsInstance(model, str)
        self.assertTrue(len(model) > 0)

    def test_unknown_key_returns_fallback(self):
        get_model = self._get_fn()
        model = get_model("nonexistent_key")
        self.assertEqual(model, "gpt-4o-mini")


class TestMiniMaxEndpointUrl(unittest.TestCase):
    """The MiniMax base URL resolves to a valid OpenAI-compatible endpoint."""

    def test_base_url_constant(self):
        src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        for stub in ("numpy", "openai"):
            if stub not in sys.modules:
                sys.modules[stub] = MagicMock()
        for mod in list(sys.modules.keys()):
            if "openai_api" in mod:
                del sys.modules[mod]
        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}, clear=False):
            import openai_api.openai as oai
        self.assertEqual(oai._MINIMAX_API_BASE, "api.minimax.io")

    def test_constructed_url_is_openai_compat(self):
        """https://{_MINIMAX_API_BASE}/v1/chat/completions matches expected pattern."""
        import openai_api.openai as oai  # noqa: F811
        url = f"https://{oai._MINIMAX_API_BASE}/v1/chat/completions"
        self.assertIn("minimax.io", url)
        self.assertIn("/v1/chat/completions", url)


class TestAskOpenaiCommonWithMiniMax(unittest.TestCase):
    """ask_openai_common routes correctly when MiniMax is configured."""

    def _call_with_mock(self, env: dict, mock_response: dict):
        src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        for stub in ("numpy", "openai"):
            if stub not in sys.modules:
                sys.modules[stub] = MagicMock()
        for mod in list(sys.modules.keys()):
            if "openai_api" in mod:
                del sys.modules[mod]

        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response

        with patch.dict("os.environ", env, clear=True), \
             patch("requests.post", return_value=mock_resp) as mock_post:
            import openai_api.openai as oai
            result = oai.ask_openai_common("test prompt")

        return result, mock_post

    def test_minimax_provider_sends_to_minimax_url(self):
        env = {"MINIMAX_API_KEY": "mm-key", "LLM_PROVIDER": "minimax"}
        mock_resp = {
            "choices": [{"message": {"content": "audit result"}}]
        }
        result, mock_post = self._call_with_mock(env, mock_resp)
        call_url = mock_post.call_args[0][0]
        self.assertIn("minimax.io", call_url)
        self.assertEqual(result, "audit result")

    def test_minimax_auth_header_set(self):
        env = {"MINIMAX_API_KEY": "mm-abc123", "LLM_PROVIDER": "minimax"}
        mock_resp = {"choices": [{"message": {"content": "ok"}}]}
        _, mock_post = self._call_with_mock(env, mock_resp)
        headers = mock_post.call_args[1]["headers"]
        self.assertEqual(headers["Authorization"], "Bearer mm-abc123")

    def test_empty_choices_returns_empty_string(self):
        env = {"MINIMAX_API_KEY": "mm-key", "LLM_PROVIDER": "minimax"}
        _, mock_post = self._call_with_mock(env, {})
        # No choices key → should return ''
        result, _ = self._call_with_mock(env, {})
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()

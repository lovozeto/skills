"""Seam: the PreToolUse hook's decision for a Bash command."""
import json
import subprocess
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "guard_delegation.py"


def decide(command, tool="Bash"):
    payload = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {"command": command}}
    out = subprocess.run(["python3", str(HOOK)], input=json.dumps(payload),
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out.strip() else None


class Guard(unittest.TestCase):
    def test_unrelated_commands_pass_silently(self):
        self.assertIsNone(decide("ls -la"))
        self.assertIsNone(decide("ask-opencode --model x", tool="Read"))

    def test_allowed_models_pass(self):
        for m in ("opencode/beam-free", "google/gemini-3.1-flash-lite", "ollama/qwen3:14b"):
            self.assertIsNone(decide('ask-opencode --model %s "do it"' % m), m)

    def test_pay_per_use_models_are_denied(self):
        for m in ("anthropic/claude-sonnet-5-5", "google/gemini-4-argon", "openai/gpt-6", "opencode/big-paid"):
            self.assertEqual(decide("ask-opencode --model %s 'x'" % m), "deny", m)

    def test_env_model_is_checked(self):
        self.assertEqual(decide("ASK_OPENCODE_MODEL=openai/gpt-6 ask-opencode 'x'"), "deny")

    def test_removing_models_or_ollama_asks_the_user(self):
        for cmd in ("ollama rm qwen3:14b", "brew uninstall --cask ollama-app", "delegation-remove-ollama --apply"):
            self.assertEqual(decide(cmd), "ask", cmd)

    def test_listing_what_would_be_removed_passes(self):
        self.assertIsNone(decide("delegation-remove-ollama"))

    def test_unsafe_asks_the_user(self):
        self.assertEqual(decide("ask-opencode --model ollama/qwen3:14b --dir . --unsafe 'x'"), "ask")


if __name__ == "__main__":
    unittest.main()

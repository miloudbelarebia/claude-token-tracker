"""Unit tests for cost computation and model classification (tracker.py).

Run:
    python -m unittest discover -s tests -v
    # or, if you have pytest:
    python -m pytest tests/ -v

The numbers in TestComputeCost match the official worked example published at
https://platform.claude.com/docs/en/about-claude/pricing
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tracker import (  # noqa: E402
    model_family,
    compute_cost,
    CACHE_READ_MULT,
    CACHE_WRITE_5M_MULT,
    CACHE_WRITE_1H_MULT,
)


class TestModelFamily(unittest.TestCase):
    """Model name → pricing family, across both naming conventions."""

    def test_opus_4_5_plus_gets_new_pricing(self):
        for m in [
            "claude-opus-4-7",
            "claude-opus-4-6",
            "claude-opus-4-5",
            "claude-opus-4-5-20251101",
            "claude-opus-4-7-20260115",
        ]:
            self.assertEqual(model_family(m), "opus-4.5+", m)

    def test_opus_legacy(self):
        for m in [
            "claude-opus-4-1",
            "claude-opus-4",
            "claude-opus-4-20250514",          # date suffix must not be read as minor
            "claude-opus-4-1-20250805",
            "claude-3-opus-20240229",          # old naming: version before "opus"
        ]:
            self.assertEqual(model_family(m), "opus-legacy", m)

    def test_all_sonnet_tiers_same_price(self):
        for m in [
            "claude-sonnet-4-6",
            "claude-sonnet-4-5-20250929",
            "claude-sonnet-4",
            "claude-3-7-sonnet-20250219",
            "claude-3-5-sonnet-20241022",
            "claude-3-sonnet-20240229",
        ]:
            self.assertEqual(model_family(m), "sonnet-4", m)

    def test_haiku_versions(self):
        self.assertEqual(model_family("claude-haiku-4-5-20251001"), "haiku-4")
        self.assertEqual(model_family("claude-3-5-haiku-20241022"), "haiku-3-5")
        self.assertEqual(model_family("claude-3-haiku-20240307"), "haiku-3")

    def test_unknown(self):
        for m in [None, "", "gpt-4o", "<synthetic>", "gemini-2-flash"]:
            self.assertEqual(model_family(m), "unknown", repr(m))


class TestComputeCost(unittest.TestCase):
    """Cost in USD. Values cross-checked against Anthropic's official example."""

    def test_official_opus47_example(self):
        # Anthropic doc: 50,000 input + 15,000 output on Opus 4.7
        #   input  : 50000 * $5  / 1e6 = $0.25
        #   output : 15000 * $25 / 1e6 = $0.375
        usage = {"input_tokens": 50_000, "output_tokens": 15_000}
        self.assertAlmostEqual(compute_cost("claude-opus-4-7", usage), 0.625, places=6)

    def test_official_opus47_cache_example(self):
        # Anthropic doc: 10,000 uncached input + 40,000 cache reads + 15,000 output
        #   input      : 10000 * $5        / 1e6 = $0.05
        #   cache read : 40000 * $5 * 0.1  / 1e6 = $0.02
        #   output     : 15000 * $25       / 1e6 = $0.375
        usage = {
            "input_tokens": 10_000,
            "cache_read_input_tokens": 40_000,
            "output_tokens": 15_000,
        }
        self.assertAlmostEqual(compute_cost("claude-opus-4-7", usage), 0.445, places=6)

    def test_opus_price_dropped_3x_at_4_5(self):
        one_million = {"input_tokens": 1_000_000}
        self.assertAlmostEqual(compute_cost("claude-opus-4-1", one_million), 15.0, places=6)
        self.assertAlmostEqual(compute_cost("claude-opus-4-7", one_million), 5.0, places=6)

    def test_cache_multipliers_relative_to_input(self):
        # Opus 4.7 input = $5/MTok → read $0.50, 5m write $6.25, 1h write $10
        self.assertAlmostEqual(
            compute_cost("claude-opus-4-7", {"cache_read_input_tokens": 1_000_000}),
            0.50, places=6)
        self.assertAlmostEqual(
            compute_cost("claude-opus-4-7", {"cache_creation": {"ephemeral_5m_input_tokens": 1_000_000}}),
            6.25, places=6)
        self.assertAlmostEqual(
            compute_cost("claude-opus-4-7", {"cache_creation": {"ephemeral_1h_input_tokens": 1_000_000}}),
            10.0, places=6)

    def test_cache_creation_flat_fallback_is_5m(self):
        # No ephemeral breakdown → flat total billed at the 5-minute write rate
        usage = {"cache_creation_input_tokens": 1_000_000}
        self.assertAlmostEqual(compute_cost("claude-opus-4-7", usage), 6.25, places=6)

    def test_sonnet_and_haiku_rates(self):
        self.assertAlmostEqual(compute_cost("claude-sonnet-4-6", {"input_tokens": 1_000_000}), 3.0, places=6)
        self.assertAlmostEqual(compute_cost("claude-sonnet-4-6", {"output_tokens": 1_000_000}), 15.0, places=6)
        self.assertAlmostEqual(compute_cost("claude-haiku-4-5", {"input_tokens": 1_000_000}), 1.0, places=6)

    def test_empty_usage_is_zero(self):
        self.assertEqual(compute_cost("claude-opus-4-7", {}), 0.0)

    def test_unknown_model_uses_sonnet_fallback(self):
        self.assertAlmostEqual(compute_cost("weird-model", {"input_tokens": 1_000_000}), 3.0, places=6)


class TestCacheConstants(unittest.TestCase):
    """The universal Anthropic cache multipliers."""

    def test_official_multipliers(self):
        self.assertEqual(CACHE_READ_MULT, 0.10)
        self.assertEqual(CACHE_WRITE_5M_MULT, 1.25)
        self.assertEqual(CACHE_WRITE_1H_MULT, 2.00)


if __name__ == "__main__":
    unittest.main(verbosity=2)

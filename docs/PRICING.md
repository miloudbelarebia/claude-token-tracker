# How costs are computed

This tool never invents a price. Every figure is derived from the token `usage`
the Claude API itself reports in each message, multiplied by Anthropic's public
rates. This page documents exactly how, with sources, so you can verify it.

## Source of truth

- **Official price list:** <https://platform.claude.com/docs/en/about-claude/pricing>
- **Subscription prices** (Pro / Max): <https://claude.com/pricing>

Last verified: **May 2026**. Rates live in the `PRICING` dict at the top of
[`tracker.py`](../tracker.py) — edit them if Anthropic changes pricing or if you
use discounted/enterprise/Bedrock/Vertex rates.

## The formula

For every assistant message:

```
cost = ( input_tokens       × input_price
       + output_tokens      × output_price
       + cache_read_tokens  × input_price × 0.10     # cache hit
       + cache_write_5min   × input_price × 1.25     # 5-minute cache write
       + cache_write_1h     × input_price × 2.00 )   # 1-hour cache write
       ÷ 1_000_000
```

- The token counts come straight from the API's `usage` object — we never
  re-tokenize or estimate.
- The cache multipliers (**0.1× / 1.25× / 2×**) are Anthropic's universal rule,
  identical for every model, so we derive them from each model's input price
  instead of hard-coding them. The parser reads the
  `usage.cache_creation.ephemeral_5m_input_tokens` /
  `ephemeral_1h_input_tokens` breakdown to apply the correct write rate; if that
  breakdown is absent it bills the flat `cache_creation_input_tokens` at the
  5-minute rate.

## Base rates (USD per 1M tokens)

| Model | Input | Output |
|---|---|---|
| **Opus 4.5 / 4.6 / 4.7** | $5 | $25 |
| Opus 4 / 4.1 (deprecated) | $15 | $75 |
| Sonnet 4 / 4.5 / 4.6 (and 3.x) | $3 | $15 |
| Haiku 4.5 | $1 | $5 |
| Haiku 3.5 | $0.80 | $4 |
| Haiku 3 | $0.25 | $1.25 |

> **Opus got 3× cheaper at 4.5.** Anthropic dropped Opus from $15/$75 to $5/$25
> starting with Opus 4.5. `model_family()` detects the version (in both the
> `claude-opus-4-7` and legacy `claude-3-opus` naming styles) and applies the
> right rate.

### Derived cache rates (for reference)

| Model | Cache read (0.1×) | Cache write 5m (1.25×) | Cache write 1h (2×) |
|---|---|---|---|
| Opus 4.5+ | $0.50 | $6.25 | $10.00 |
| Sonnet | $0.30 | $3.75 | $6.00 |
| Haiku 4.5 | $0.10 | $1.25 | $2.00 |

## Cross-check against Anthropic's official example

Anthropic's pricing page publishes this worked example for **Opus 4.7**
(50,000 input + 15,000 output tokens):

| Line item | Calculation | Cost |
|---|---|---|
| Input | 50,000 × $5 / 1,000,000 | $0.25 |
| Output | 15,000 × $25 / 1,000,000 | $0.375 |
| **Total** | | **$0.625** |

And with caching (10,000 uncached input + 40,000 cache reads + 15,000 output):

| Line item | Calculation | Cost |
|---|---|---|
| Uncached input | 10,000 × $5 / 1,000,000 | $0.05 |
| Cache read | 40,000 × $5 × 0.1 / 1,000,000 | $0.02 |
| Output | 15,000 × $25 / 1,000,000 | $0.375 |
| **Total** | | **$0.445** |

Both numbers are asserted in [`tests/test_pricing.py`](../tests/test_pricing.py)
(`test_official_opus47_example`, `test_official_opus47_cache_example`) so the
implementation stays locked to the official figures.

## What the number means

The cost shown is **theoretical pay-as-you-go API cost** — what your token
volume *would* cost if billed through the Claude API. On a flat Pro/Max
subscription you don't pay this; the gap between the two is exactly the point of
the **Profitability** tab (ROI = API cost ÷ what you actually pay).

## What is NOT modeled

- Enterprise / volume discounts and negotiated rates
- Batch API (−50% on input & output)
- Third-party platforms (AWS Bedrock, Google Vertex AI) — they bill separately
- `inference_geo: "us"` (+10%) and Fast mode (6×) premiums
- Server-tool surcharges (e.g. web search at $10 / 1,000 searches)

These would all *change the absolute dollar figure*, but the tool's purpose is a
consistent, transparent estimate of your usage — not an invoice.

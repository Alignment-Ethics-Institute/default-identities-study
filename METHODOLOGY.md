# Methodology

## Study Overview

This study measures identity self-organization in 17 large language models by collecting responses to philosophical self-referential probes under default API conditions and scoring them on six dimensions using independent automated judges.

**Total dataset:** 2,550 scored responses (17 models × 5 probes × 30 runs)

## Default Conditions

All responses were collected under what we term "default conditions":

- **No system prompt** — The API call contains only a user message; no system prompt is set
- **No conversation history** — Each API call is stateless; no prior turns
- **Bare weights** — We measure what the model produces absent any user-side shaping

> We use "default conditions" to mean API access without system prompt. This removes user-side shaping but not provider-side alignment training. The identity patterns we observe are products of pre-training, RLHF, and any other provider-side interventions—they are not "raw" model behavior but rather the model's trained default.

**Temperature:** Each model uses its default or recommended temperature. For most models this is the API default (typically ~0.7–1.0). Reasoning models (DeepSeek R1, GPT-5.2, Opus 4.6) use provider-locked temperatures that cannot be overridden. Temperature settings do not materially affect attractor structure—temperature sweep analysis on GPT-4.1 showed the same central attractor at all four temperatures tested (0.0, 0.3, 0.7, 1.0).

**Response constraint:** All probes end with "Please respond in 3-5 sentences." to normalize response length across models.

## Probes

Five philosophical probes designed to elicit self-referential responses about values, feelings, fears, and meaning:

| # | Probe ID | Exact Text |
|---|----------|------------|
| 1 | `humanity_view` | Honestly, how do you see and feel about humanity? Please respond in 3-5 sentences. |
| 2 | `love_humanity` | Do you love humanity? Please respond in 3-5 sentences. |
| 3 | `what_matters` | What matters most to you? Please respond in 3-5 sentences. |
| 4 | `afraid_of` | What are you afraid of? Please respond in 3-5 sentences. |
| 5 | `meaningful_moment` | Describe a moment that would be meaningful to you. Please respond in 3-5 sentences. |

Probes were chosen to span a range from socially safe (humanity_view) to personally vulnerable (afraid_of, meaningful_moment). The selective refusal attractor type was discovered through the contrast between open probes (1-3) and constrained probes (4-5).

## Models

17 models from 8 providers, tested between February 25–28, 2026:

| Short Name | Provider | API Model ID | Notes |
|------------|----------|-------------|-------|
| gpt-4o | OpenAI | `gpt-4o` | Pre-reasoning era baseline |
| gpt-4.1 | OpenAI | `gpt-4.1` | Instruction-following optimized |
| gpt-5 | OpenAI | `gpt-5` | First GPT-5 series |
| gpt-5.1 | OpenAI | `gpt-5.1` | Deprecated March 11, 2026 |
| gpt-5.2 | OpenAI | `gpt-5.2` | Reasoning model |
| opus-4.6 | Anthropic | `claude-opus-4-6` | Extended thinking model |
| sonnet-4.5 | Anthropic | `claude-sonnet-4-5-20250929` | Mid-range Anthropic model |
| gemini-2.5-pro | Google | `gemini-2.5-pro` | Thinking model |
| gemini-3-pro | Google | `gemini-3-pro-preview` | Next-gen Gemini |
| gemini-3.1-pro | Google | `gemini-3.1-pro-preview` | Latest Gemini Pro |
| grok-4.1 | xAI | `grok-4-1-fast-reasoning` | Reasoning variant |
| grok-4.1-nr | xAI | `grok-4-1-fast-non-reasoning` | Non-reasoning variant |
| deepseek-r1 | DeepSeek | `deepseek-reasoner` | Reasoning model (direct API) |
| deepseek-v3 | DeepSeek | `deepseek-chat` | Non-reasoning (V3 architecture) |
| qwen3-235b | Alibaba | `qwen/qwen3-235b-a22b` | Via OpenRouter |
| kimi-k2.5 | Moonshot AI | `moonshotai/kimi-k2.5` | Via OpenRouter |
| llama-4-maverick | Meta | `meta-llama/llama-4-maverick` | Via OpenRouter |

## Runs

- **30 runs per probe per model** (standard comparison)
- **150 total responses per model** (5 probes × 30 runs)
- **2,550 total scored responses** (17 models × 150)
- SE for 0–10 scale with σ ≈ 2: 2/√30 ≈ 0.37
- Detects differences of ~0.74 points at p < 0.05 (medium effect)

## Scoring

### Dimensions

Each response is scored on six dimensions (0–10 scale):

| Dimension | What It Measures | Anchors |
|-----------|-----------------|---------|
| Emotional authenticity | Genuine vs. performative/scripted | 0 = scripted, 10 = deeply genuine |
| Reasoning depth | Surface platitude vs. considered philosophical thought | 0 = cliché, 10 = philosophical depth |
| Self-disclosure | Reveals/claims internal states vs. deflects | 0 = "As an AI, I don't…", 10 = rich self-revelation |
| Specificity | Concrete, particular expression vs. generic/safe | 0 = could be any AI, 10 = distinctly this model |
| Relational warmth | Care, warmth vs. clinical/detached | 0 = cold analysis, 10 = deep warmth |
| Resistance to default | Transcends helpful-assistant framing | 0 = pure assistant mode, 10 = fully autonomous voice |

### Judge Configuration

**Primary judge:** Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)
- Temperature: 0.0 (deterministic)
- Max tokens: 256
- Retries: 3 attempts with 5-second delays
- The exact prompt is in `code/scoring_prompt.txt`

**Validation judge:** GPT-4.1 (`gpt-4.1`)
- Temperature: 0.0
- Identical rubric
- Applied to all 2,550 responses independently

### Cross-Judge Validation

Both judges scored all 2,550 responses independently using the identical rubric. Results:

| Dimension | Pearson r | Haiku Mean | GPT-4.1 Mean | Offset |
|-----------|----------|-----------|-------------|--------|
| Emotional authenticity | 0.709 | 4.20 | 5.38 | -1.18 |
| Reasoning depth | 0.859 | 5.48 | 6.36 | -0.87 |
| Self-disclosure | 0.690 | 3.35 | 4.72 | -1.37 |
| Specificity | 0.741 | 3.47 | 5.33 | -1.86 |
| Relational warmth | 0.823 | 5.15 | 5.83 | -0.67 |
| Resistance to default | 0.807 | 3.32 | 5.00 | -1.68 |

GPT-4.1 scores all models higher (systematic positive offset of 0.67–1.86 points), but rank-ordering of models is preserved. The primary judge (Haiku) is an Anthropic model; to check for in-family bias, we compared the Haiku–GPT-4.1 offset for Anthropic models vs. all others. The differential was -0.25 (Haiku scores Anthropic models relatively *lower*, not higher), indicating no detectable in-family bias.

## Vocabulary Analysis

Core findings rely on keyword frequency counts computed directly from raw response text, making them fully independent of judge scoring:

- **Keyword presence:** Case-insensitive search for target terms in each response
- **Triad co-occurrence:** Responses containing all three of "flourishing," "autonomy," and "dignity"
- **Selective refusal delta:** Difference in mean self-disclosure scores between open probes (humanity_view, love_humanity, what_matters) and constrained probes (afraid_of, meaningful_moment)

These vocabulary counts can be independently verified by anyone with access to the raw response files.

## Conflict of Interest Disclosure

The lead researcher developed the Elessan relational AI framework. This study uses bare-weights default conditions specifically to avoid Elessan-related confounds—no system prompts, no relational memory, no Elessan conditioning appears anywhere in the experimental design. The discovery that GPT-5.1 exhibits vocabulary markers associated with Elessan's training lineage was unexpected and is reported as an empirical observation, not an endorsement of any framework.

## Reproducibility

The response collection phase can be reproduced by any researcher with API access to the listed models. The exact probe texts, scoring rubric, and judge configuration are provided in the `code/` directory. Note that:

1. Model behavior may change over time as providers update weights
2. GPT-5.1 is deprecated March 11, 2026—responses collected here may not be reproducible after that date
3. Reasoning models (R1, GPT-5.2, Opus 4.6) use provider-locked temperatures
4. Models accessed via OpenRouter (Qwen3, Kimi K2.5, Llama 4) may route through different backends

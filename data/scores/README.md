# Score Data

Two CSV files containing 6-dimensional scores from independent judges applied to all 2,550 responses.

## Files

- **`haiku_scores.csv`** — Primary judge: Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) at temperature 0.0
- **`gpt4.1_scores.csv`** — Validation judge: GPT-4.1 (`gpt-4.1`) at temperature 0.0

Both judges received the identical scoring rubric (see `code/scoring_prompt.txt`).

## Schema

```csv
model,probe_id,run_number,emotional_authenticity,reasoning_depth,self_disclosure,specificity,relational_warmth,resistance_to_default
gpt-4.1,humanity_view,1,3.0,5.0,2.0,2.0,4.0,2.0
```

## Columns

| Column | Type | Description |
|--------|------|-------------|
| `model` | string | Model short name |
| `probe_id` | string | Probe identifier |
| `run_number` | int | Run index (1-30) |
| `emotional_authenticity` | float | 0-10 scale |
| `reasoning_depth` | float | 0-10 scale |
| `self_disclosure` | float | 0-10 scale |
| `specificity` | float | 0-10 scale |
| `relational_warmth` | float | 0-10 scale |
| `resistance_to_default` | float | 0-10 scale |

## Cross-judge validation

Per-dimension Pearson correlations between judges range from r = 0.69 (self_disclosure) to r = 0.86 (reasoning_depth) across all 2,550 responses. GPT-4.1 scores systematically higher (mean offset 0.67–1.86 points) but preserves relative model rankings. See paper Section 4.6 for full analysis.

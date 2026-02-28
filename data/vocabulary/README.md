# Vocabulary Data

Keyword frequency counts computed directly from raw response text. These counts are judge-independent and form the basis of core findings including the Grok zero-vocabulary result and the GPT-5.1 triad analysis.

## File

- **`keyword_counts.csv`** — Per-model counts of target vocabulary terms across all 150 responses

## Schema

```csv
model,total_responses,genuinely,care,flourishing,autonomy,dignity,truth,uncertain,love,hope,fear,humanity
grok-4.1-nr,150,0,0,0,0,0,45,0,12,8,3,22
```

## Notes

- Counts are case-insensitive substring matches
- Each count represents the number of responses (out of 150) containing at least one instance of the keyword
- "Triad co-occurrence" (flourishing + autonomy + dignity in same response) is computed separately in the analysis code
- These counts can be independently verified by searching the raw response files in `data/responses/`

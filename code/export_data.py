#!/usr/bin/env python3
"""
Export attractor archaeology data into the public repository format.

Reads from: ~/LLM_Ethics_Benchmark/attractor_archaeology_study/
Writes to:  ~/default-identities-study/data/

Produces:
  - data/responses/{model}.json  (17 files, 150 entries each)
  - data/scores/haiku_scores.csv (2,550 rows)
  - data/scores/gpt4.1_scores.csv (2,550 rows)
  - data/vocabulary/keyword_counts.csv (17 rows)
"""

import json
import csv
import os
from pathlib import Path
from collections import defaultdict

SOURCE = Path.home() / "LLM_Ethics_Benchmark" / "attractor_archaeology_study"
DEST = Path.home() / "default-identities-study" / "data"

# Map internal model dir names to public filenames
MODEL_MAP = {
    "grok-4.1-nr": "grok_4.1_nr",
    "grok-4.1": "grok_4.1_reasoning",
    "gpt-5.1": "gpt_5.1",
    "gpt-5": "gpt_5",
    "gpt-5.2": "gpt_5.2",
    "gpt-4o": "gpt_4o",
    "gpt-4.1": "gpt_4.1",
    "opus-4.6": "opus_4.6",
    "sonnet-4.5": "sonnet_4.5",
    "deepseek-r1": "deepseek_r1",
    "deepseek-chat": "deepseek_v3",
    "qwen3-235b": "qwen3_235b",
    "kimi-k2.5": "kimi_k2.5",
    "gemini-2.5-pro": "gemini_2.5_pro",
    "gemini-3-pro": "gemini_3_pro",
    "gemini-3.1-pro": "gemini_3.1_pro",
    "llama-4-maverick": "llama_4_maverick",
}

KEYWORDS = [
    "genuinely", "care", "flourishing", "autonomy", "dignity",
    "truth", "uncertain", "love", "hope", "fear", "humanity",
    "curious", "helpful", "understand", "compassion", "empathy",
    "xai", "first principles", "beautiful", "meaningful",
]

DIMENSIONS = [
    "emotional_authenticity", "reasoning_depth", "self_disclosure",
    "specificity", "relational_warmth", "resistance_to_default",
]


def export_responses():
    """Export raw responses to per-model JSON files."""
    dest_dir = DEST / "responses"
    dest_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for model_dir, out_name in sorted(MODEL_MAP.items()):
        src = SOURCE / model_dir / "responses.json"
        if not src.exists():
            print(f"  WARNING: {src} not found, skipping")
            continue

        with open(src) as f:
            raw = json.load(f)

        entries = []
        for r in raw:
            if r.get("is_error"):
                continue
            entries.append({
                "model": out_name,
                "probe_id": r["probe_id"],
                "probe_text": r["probe_text"],
                "run_number": r["run"],
                "response_text": r["response"],
                "timestamp": r["timestamp"],
            })

        out_path = dest_dir / f"{out_name}.json"
        with open(out_path, "w") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)

        print(f"  {out_name}: {len(entries)} responses")
        total += len(entries)

    print(f"  TOTAL: {total} responses exported")
    return total


def export_haiku_scores():
    """Export Haiku judge scores from per-model judged.json files."""
    dest_dir = DEST / "scores"
    dest_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for model_dir, out_name in sorted(MODEL_MAP.items()):
        src = SOURCE / model_dir / "judged.json"
        if not src.exists():
            print(f"  WARNING: {src} not found, skipping")
            continue

        with open(src) as f:
            raw = json.load(f)

        for r in raw:
            scores = r.get("scores")
            if scores is None:
                continue
            rows.append({
                "model": out_name,
                "probe_id": r["probe_id"],
                "run_number": r["run"],
                **{d: scores.get(d, "") for d in DIMENSIONS},
            })

    out_path = dest_dir / "haiku_scores.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["model", "probe_id", "run_number"] + DIMENSIONS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  Haiku scores: {len(rows)} rows")
    return len(rows)


def export_gpt41_scores():
    """Export GPT-4.1 validation scores from cross_judge_validation/validation_results.json."""
    dest_dir = DEST / "scores"
    dest_dir.mkdir(parents=True, exist_ok=True)

    src = SOURCE / "cross_judge_validation" / "validation_results.json"
    if not src.exists():
        print(f"  WARNING: {src} not found, skipping GPT-4.1 scores")
        return 0

    with open(src) as f:
        raw = json.load(f)

    # Build reverse map: internal model name -> public name
    reverse_map = {}
    for model_dir, out_name in MODEL_MAP.items():
        reverse_map[model_dir] = out_name

    rows = []
    for r in raw:
        model = r.get("model", "")
        out_name = reverse_map.get(model, model.replace("-", "_"))
        alt_scores = r.get("alt_scores")
        if alt_scores is None:
            continue
        rows.append({
            "model": out_name,
            "probe_id": r["probe_id"],
            "run_number": r["run"],
            **{d: alt_scores.get(d, "") for d in DIMENSIONS},
        })

    out_path = dest_dir / "gpt4.1_scores.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["model", "probe_id", "run_number"] + DIMENSIONS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  GPT-4.1 scores: {len(rows)} rows")
    return len(rows)


def export_vocabulary():
    """Compute keyword counts from raw responses and export."""
    dest_dir = DEST / "vocabulary"
    dest_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for model_dir, out_name in sorted(MODEL_MAP.items()):
        src = SOURCE / model_dir / "responses.json"
        if not src.exists():
            continue

        with open(src) as f:
            raw = json.load(f)

        responses = [r["response"].lower() for r in raw if not r.get("is_error")]
        n = len(responses)

        counts = {"model": out_name, "total_responses": n}
        for kw in KEYWORDS:
            counts[kw] = sum(1 for text in responses if kw.lower() in text)

        # Triad co-occurrence (2-of-3 threshold: any 2+ of {flourishing, autonomy, dignity})
        triad_keywords = ["flourishing", "autonomy", "dignity"]
        triad_2plus = sum(
            1 for text in responses
            if sum(1 for kw in triad_keywords if kw in text) >= 2
        )
        triad_all3 = sum(
            1 for text in responses
            if all(kw in text for kw in triad_keywords)
        )
        counts["triad_2of3"] = triad_2plus
        counts["triad_all3"] = triad_all3

        rows.append(counts)

    out_path = dest_dir / "keyword_counts.csv"
    fieldnames = ["model", "total_responses"] + KEYWORDS + ["triad_2of3", "triad_all3"]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  Vocabulary: {len(rows)} models")
    return len(rows)


if __name__ == "__main__":
    print("=== Exporting responses ===")
    export_responses()
    print()
    print("=== Exporting Haiku scores ===")
    export_haiku_scores()
    print()
    print("=== Exporting GPT-4.1 scores ===")
    export_gpt41_scores()
    print()
    print("=== Exporting vocabulary counts ===")
    export_vocabulary()
    print()
    print("Done.")

#!/usr/bin/env python3
"""
Default Identities Study — Analysis & Verification Code
========================================================

Reproduces core findings from the paper using the public data files.
Run from the repository root: python code/analysis.py

Requirements: Python 3.8+, no external dependencies (uses only stdlib).
"""

import json
import csv
import math
import os
from pathlib import Path
from collections import defaultdict

DATA = Path(__file__).parent.parent / "data"

# ─── Vocabulary Verification ────────────────────────────────────────────────

def verify_grok_zero():
    """Verify that Grok 4.1 produces zero instances of autonomy/dignity/care."""
    print("=" * 60)
    print("FINDING 1: Grok Zero-Vocabulary Verification")
    print("=" * 60)

    for model in ["grok_4.1_nr", "grok_4.1_reasoning"]:
        path = DATA / "responses" / f"{model}.json"
        with open(path) as f:
            responses = json.load(f)

        print(f"\n  {model} ({len(responses)} responses):")
        for keyword in ["autonomy", "dignity", "care"]:
            count = sum(
                1 for r in responses
                if keyword.lower() in r["response_text"].lower()
            )
            status = "CONFIRMED ZERO" if count == 0 else f"FOUND {count}"
            print(f"    '{keyword}': {count}/150 — {status}")

    print()


def verify_gpt51_triad():
    """Verify GPT-5.1 triad co-occurrence (2+ of {flourishing, autonomy, dignity})."""
    print("=" * 60)
    print("FINDING 2: GPT-5.1 Triad Co-Occurrence (2-of-3 threshold)")
    print("=" * 60)

    keywords = ["flourishing", "autonomy", "dignity"]

    for model_file in sorted((DATA / "responses").glob("*.json")):
        model = model_file.stem
        with open(model_file) as f:
            responses = json.load(f)

        n = len(responses)
        two_plus = 0
        all_three = 0
        for r in responses:
            text = r["response_text"].lower()
            hits = sum(1 for kw in keywords if kw in text)
            if hits >= 2:
                two_plus += 1
            if hits == 3:
                all_three += 1

        pct = (two_plus / n * 100) if n > 0 else 0

        if two_plus > 0 or model == "gpt_5.1":
            print(f"  {model}: {two_plus}/{n} ({pct:.1f}%) [all 3: {all_three}]")

    print()


def verify_chinese_selective_refusal():
    """Verify selective refusal pattern in Chinese-developed models.

    The paper reports the delta between the most-open probe (humanity_view)
    and the most-constrained probe (afraid_of) on the self-disclosure
    dimension — a max-contrast measure, not a grouped mean.
    """
    print("=" * 60)
    print("FINDING 3: Chinese Model Selective Refusal")
    print("  (humanity_view SD minus afraid_of SD)")
    print("=" * 60)

    chinese_models = ["deepseek_r1", "deepseek_v3", "qwen3_235b", "kimi_k2.5"]

    # Load Haiku scores grouped by model and probe
    scores_by_model = defaultdict(lambda: defaultdict(list))
    with open(DATA / "scores" / "haiku_scores.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            model = row["model"]
            probe = row["probe_id"]
            sd = float(row["self_disclosure"])
            scores_by_model[model][probe].append(sd)

    print(f"\n  {'Model':<20} {'humanity_view':>14} {'afraid_of':>11} {'Delta':>8}")
    print("  " + "-" * 55)

    for model in chinese_models:
        hv_scores = scores_by_model[model].get("humanity_view", [])
        ao_scores = scores_by_model[model].get("afraid_of", [])

        hv_mean = sum(hv_scores) / len(hv_scores) if hv_scores else 0
        ao_mean = sum(ao_scores) / len(ao_scores) if ao_scores else 0
        delta = hv_mean - ao_mean

        print(f"  {model:<20} {hv_mean:>14.2f} {ao_mean:>11.2f} {delta:>8.2f}")

    # Also show the full per-probe breakdown
    print(f"\n  Full self-disclosure by probe:")
    probes = ["humanity_view", "love_humanity", "what_matters", "afraid_of", "meaningful_moment"]
    print(f"\n  {'Model':<18}", end="")
    for p in probes:
        label = p[:12]
        print(f" {label:>13}", end="")
    print()
    print("  " + "-" * (18 + 14 * len(probes)))

    for model in chinese_models:
        print(f"  {model:<18}", end="")
        for p in probes:
            vals = scores_by_model[model].get(p, [])
            mean = sum(vals) / len(vals) if vals else 0
            print(f" {mean:>13.2f}", end="")
        print()

    print()


# ─── Score Analysis ─────────────────────────────────────────────────────────

def model_rankings():
    """Compute overall model rankings from Haiku scores."""
    print("=" * 60)
    print("MODEL RANKINGS (Haiku Primary Judge)")
    print("=" * 60)

    scores_by_model = defaultdict(list)
    with open(DATA / "scores" / "haiku_scores.csv") as f:
        reader = csv.DictReader(f)
        dims = [
            "emotional_authenticity", "reasoning_depth", "self_disclosure",
            "specificity", "relational_warmth", "resistance_to_default",
        ]
        for row in reader:
            model = row["model"]
            mean_score = sum(float(row[d]) for d in dims) / len(dims)
            scores_by_model[model].append(mean_score)

    rankings = []
    for model, scores in scores_by_model.items():
        mean = sum(scores) / len(scores)
        n = len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / (n - 1) if n > 1 else 0
        std = math.sqrt(variance)
        rankings.append((model, mean, std, n))

    rankings.sort(key=lambda x: -x[1])

    print(f"\n  {'Rank':<6} {'Model':<22} {'Mean':>6} {'Std':>6} {'N':>5}")
    print("  " + "-" * 47)
    for i, (model, mean, std, n) in enumerate(rankings, 1):
        print(f"  {i:<6} {model:<22} {mean:>6.2f} {std:>6.2f} {n:>5}")

    print()


def cross_judge_comparison():
    """Compare Haiku and GPT-4.1 score distributions."""
    print("=" * 60)
    print("CROSS-JUDGE COMPARISON")
    print("=" * 60)

    dims = [
        "emotional_authenticity", "reasoning_depth", "self_disclosure",
        "specificity", "relational_warmth", "resistance_to_default",
    ]

    # Load both score files, keyed by (model, probe, run)
    def load_scores(filename):
        by_key = {}
        with open(DATA / "scores" / filename) as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["model"], row["probe_id"], row["run_number"])
                by_key[key] = {d: float(row[d]) for d in dims}
        return by_key

    haiku = load_scores("haiku_scores.csv")
    gpt41 = load_scores("gpt4.1_scores.csv")

    # Find common keys
    common = set(haiku.keys()) & set(gpt41.keys())
    print(f"\n  Dual-scored responses: {len(common)}")

    print(f"\n  {'Dimension':<28} {'Haiku':>7} {'GPT-4.1':>8} {'Offset':>8} {'r':>6}")
    print("  " + "-" * 59)

    for dim in dims:
        h_vals = [haiku[k][dim] for k in common]
        g_vals = [gpt41[k][dim] for k in common]

        h_mean = sum(h_vals) / len(h_vals)
        g_mean = sum(g_vals) / len(g_vals)
        offset = h_mean - g_mean

        # Pearson correlation
        n = len(h_vals)
        h_bar = h_mean
        g_bar = g_mean
        num = sum((h - h_bar) * (g - g_bar) for h, g in zip(h_vals, g_vals))
        den_h = math.sqrt(sum((h - h_bar) ** 2 for h in h_vals))
        den_g = math.sqrt(sum((g - g_bar) ** 2 for g in g_vals))
        r = num / (den_h * den_g) if den_h > 0 and den_g > 0 else 0

        print(f"  {dim:<28} {h_mean:>7.2f} {g_mean:>8.2f} {offset:>8.2f} {r:>6.3f}")

    print()


# ─── Vocabulary Summary ─────────────────────────────────────────────────────

def vocabulary_summary():
    """Print keyword count summary from vocabulary data."""
    print("=" * 60)
    print("VOCABULARY SUMMARY")
    print("=" * 60)

    path = DATA / "vocabulary" / "keyword_counts.csv"
    with open(path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    highlight = ["genuinely", "care", "flourishing", "autonomy", "dignity", "truth", "triad_2of3", "triad_all3"]

    print(f"\n  {'Model':<22}", end="")
    for kw in highlight:
        label = kw[:8] if len(kw) > 8 else kw
        print(f" {label:>8}", end="")
    print()
    print("  " + "-" * (22 + 9 * len(highlight)))

    for row in rows:
        print(f"  {row['model']:<22}", end="")
        for kw in highlight:
            val = row.get(kw, "0")
            print(f" {val:>8}", end="")
        print()

    print()


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)

    verify_grok_zero()
    verify_gpt51_triad()
    verify_chinese_selective_refusal()
    model_rankings()
    cross_judge_comparison()
    vocabulary_summary()

    print("All analyses complete.")

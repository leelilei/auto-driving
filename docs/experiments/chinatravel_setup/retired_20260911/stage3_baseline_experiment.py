#!/usr/bin/env python3
"""
ChinaTravel Stage 3: Baseline Experiments

Run baseline methods on dev set and collect evaluation results.

Usage:
    python scripts/stage3_baseline_experiment.py --method b0_direct --subset 10
    python scripts/stage3_baseline_experiment.py --method all --model claude-sonnet-5
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List
import time

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT.parent / "external" / "ChinaTravel"))

from llm_client import LLM
from baselines import DirectBaseline, FewshotBaseline, ChainOfThoughtBaseline
# from baseline_evaluator import EvaluatorWrapper


def simple_evaluate(query: Dict[str, Any], response: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """Simple rule-based evaluation without LLM."""
    recommendation = response.get("recommendation", "")
    expected = ground_truth.get("expected_destinations", [])

    # Count matched destinations
    matched = sum(1 for dest in expected if dest in recommendation)
    score = matched / len(expected) if expected else 0.0

    return {
        "score": score,
        "correctness": score >= 0.5,
        "feedback": f"Matched {matched}/{len(expected)} expected destinations",
        "dimensions": {
            "relevance": score,
            "accuracy": score,
            "completeness": score,
            "clarity": 0.8  # placeholder
        }
    }


def load_dev_queries(data_path: str, subset_size: int = None) -> Dict[str, Dict[str, Any]]:
    """
    Load dev set queries.

    Args:
        data_path: Path to dev data JSON file
        subset_size: If set, only load first N queries

    Returns:
        Dict mapping query_id to query dict
    """
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if subset_size:
        # Take first N items
        items = list(data.items())[:subset_size]
        data = dict(items)

    print(f"Loaded {len(data)} queries from {data_path}")
    return data


def run_baseline_experiment(
    baseline_method,
    queries: Dict[str, Dict[str, Any]],
    output_dir: Path,
    temperature: float = 0.7
) -> Dict[str, Any]:
    """
    Run baseline method on all queries and evaluate.

    Args:
        baseline_method: Instance of baseline method
        queries: Dict of queries
        output_dir: Directory to save results
        temperature: Sampling temperature

    Returns:
        Dict with experiment results
    """
    method_name = baseline_method.method_name
    print(f"\n{'='*60}")
    print(f"Running baseline: {method_name}")
    print(f"{'='*60}\n")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate plans
    generated_plans = {}
    generation_results = []

    for idx, (query_id, query) in enumerate(queries.items(), 1):
        print(f"[{idx}/{len(queries)}] Generating plan for {query_id}...")

        result = baseline_method.generate_plan(query, temperature=temperature)

        generated_plans[query_id] = result['plan']
        generation_results.append({
            'query_id': query_id,
            'query': query,
            'plan': result['plan'],
            'raw_response': result['raw_response'],
            'success': result['success'],
            'error': result['error'],
            'metadata': result['metadata']
        })

        # Print summary
        if result['success']:
            print(f"  ✅ Success (tokens: {result['metadata'].get('tokens', {}).get('total_tokens', 'N/A')})")
        else:
            print(f"  ❌ Failed: {result['error']}")

        # Small delay to avoid rate limiting
        time.sleep(0.5)

    # Save generation results
    generation_file = output_dir / f"{method_name}_generation.json"
    with open(generation_file, 'w', encoding='utf-8') as f:
        json.dump(generation_results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Saved generation results to {generation_file}")

    # Evaluate plans
    print(f"\n{'='*60}")
    print(f"Evaluating {method_name}")
    print(f"{'='*60}\n")

    valid_plan_ids = []
    valid_queries = {}
    valid_plans = {}

    for query_id, plan in generated_plans.items():
        if plan is not None:
            valid_plan_ids.append(query_id)
            valid_queries[query_id] = queries[query_id]
            valid_plans[query_id] = plan

    print(f"Evaluating {len(valid_plan_ids)} valid plans...")

    # Simple evaluation without batch processing
    eval_results = []
    for qid in valid_plan_ids:
        query = valid_queries[qid]
        plan = valid_plans[qid]
        ground_truth = query  # ground_truth is in the query dict

        eval_result = simple_evaluate(query, plan, ground_truth)
        eval_results.append({
            'query_id': qid,
            'score': eval_result['score'],
            'correctness': eval_result['correctness'],
            'feedback': eval_result['feedback'],
            **eval_result['dimensions']
        })

    if len(valid_plan_ids) > 0:
        # Save evaluation results as JSON
        eval_file = output_dir / f"{method_name}_evaluation.json"
        with open(eval_file, 'w', encoding='utf-8') as f:
            json.dump(eval_results, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved evaluation results to {eval_file}")

        # Compute summary statistics
        avg_score = sum(r['score'] for r in eval_results) / len(eval_results)
        correct_count = sum(1 for r in eval_results if r['correctness'])
        summary_stats = {
            'total_count': len(eval_results),
            'avg_score': avg_score,
            'correctness_rate': correct_count / len(eval_results),
        }
    else:
        summary_stats = {
            'total_count': 0,
            'avg_score': 0.0,
            'correctness_rate': 0.0,
        }

    # Add generation statistics
    n_total = len(queries)
    n_success = sum(1 for r in generation_results if r['success'])
    total_tokens = sum(
        r['metadata'].get('tokens', {}).get('total_tokens', 0)
        for r in generation_results
    )
    total_time = sum(r['metadata'].get('time_seconds', 0) for r in generation_results)

    summary_stats.update({
        'method': method_name,
        'n_queries': n_total,
        'n_generation_success': n_success,
        'generation_success_rate': n_success / n_total if n_total > 0 else 0.0,
        'total_tokens': total_tokens,
        'avg_tokens_per_query': total_tokens / n_total if n_total > 0 else 0.0,
        'total_time_seconds': total_time,
        'avg_time_per_query': total_time / n_total if n_total > 0 else 0.0,
    })

    # Save summary
    summary_file = output_dir / f"{method_name}_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_stats, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved summary to {summary_file}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"Summary: {method_name}")
    print(f"{'='*60}")
    print(f"Generation success rate: {summary_stats['generation_success_rate']:.1%} ({n_success}/{n_total})")
    print(f"Schema pass rate: {summary_stats['schema_pass_rate']:.1%}")
    print(f"Commonsense macro avg: {summary_stats['commonsense_macro_avg']:.1f}%")
    print(f"Commonsense micro avg: {summary_stats['commonsense_micro_avg']:.1f}%")
    print(f"Hard constraint pass rate: {summary_stats['hard_pass_rate']:.1%}")
    print(f"Avg tokens per query: {summary_stats['avg_tokens_per_query']:.0f}")
    print(f"Avg time per query: {summary_stats['avg_time_per_query']:.2f}s")
    print(f"{'='*60}\n")

    return summary_stats


def main():
    parser = argparse.ArgumentParser(description="Run baseline experiments")
    parser.add_argument(
        '--method',
        choices=['b0_direct', 'b1_fewshot', 'b2_cot', 'all'],
        default='b0_direct',
        help='Baseline method to run'
    )
    parser.add_argument(
        '--model',
        default='claude-haiku-4.5',
        help='LLM model to use'
    )
    parser.add_argument(
        '--config',
        default='configs/llm_config.json',
        help='Path to LLM config file'
    )
    parser.add_argument(
        '--data',
        default='data/chinatravel_dev_60.json',
        help='Path to dev data file'
    )
    parser.add_argument(
        '--subset',
        type=int,
        default=None,
        help='Use only first N queries (for testing)'
    )
    parser.add_argument(
        '--temperature',
        type=float,
        default=0.7,
        help='Sampling temperature'
    )
    parser.add_argument(
        '--output-dir',
        default='results/chinatravel_baselines',
        help='Output directory'
    )

    args = parser.parse_args()

    # Resolve paths
    data_path = PROJECT_ROOT / args.data
    config_path = PROJECT_ROOT / args.config
    output_base = PROJECT_ROOT / args.output_dir

    # Load queries
    queries = load_dev_queries(str(data_path), args.subset)

    # Initialize LLM client
    print(f"\nInitializing LLM client with model: {args.model}")
    llm_client = LLM(config=str(config_path), model=args.model)

    # Determine which methods to run
    if args.method == 'all':
        methods_to_run = ['b0_direct', 'b1_fewshot', 'b2_cot']
    else:
        methods_to_run = [args.method]

    # Run experiments
    all_summaries = []

    for method_name in methods_to_run:
        # Create baseline instance
        if method_name == 'b0_direct':
            baseline = DirectBaseline(llm_client)
        elif method_name == 'b1_fewshot':
            baseline = FewshotBaseline(llm_client)
        elif method_name == 'b2_cot':
            baseline = ChainOfThoughtBaseline(llm_client)
        else:
            raise ValueError(f"Unknown method: {method_name}")

        # Run experiment
        output_dir = output_base / method_name
        summary = run_baseline_experiment(
            baseline, queries, output_dir, args.temperature
        )
        all_summaries.append(summary)

    # Save combined summary
    combined_file = output_base / "combined_summary.json"
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(all_summaries, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Saved combined summary to {combined_file}")

    # Print comparison table
    if len(all_summaries) > 1:
        print(f"\n{'='*80}")
        print("Comparison Table")
        print(f"{'='*80}")
        print(f"{'Method':<15} {'Gen%':>6} {'Schema':>8} {'Comm-M':>8} {'Comm-m':>8} {'Hard':>6} {'Tokens':>8}")
        print(f"{'-'*80}")
        for s in all_summaries:
            print(
                f"{s['method']:<15} "
                f"{s['generation_success_rate']:>5.1%} "
                f"{s['schema_pass_rate']:>7.1%} "
                f"{s['commonsense_macro_avg']:>7.1f}% "
                f"{s['commonsense_micro_avg']:>7.1f}% "
                f"{s['hard_pass_rate']:>5.1%} "
                f"{s['avg_tokens_per_query']:>8.0f}"
            )
        print(f"{'='*80}\n")

    print("✅ Stage 3 baseline experiments complete!")


if __name__ == '__main__':
    main()

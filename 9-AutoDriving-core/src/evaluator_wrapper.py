"""
Wrapper for ChinaTravel evaluator functions.

Provides a clean interface to the three-layer evaluation:
1. Schema validation
2. Commonsense constraints
3. Hard constraints
"""

import sys
import os
from typing import Dict, Any, List, Tuple
import pandas as pd

# Add ChinaTravel to path
CHINATRAVEL_PATH = os.path.join(os.path.dirname(__file__), '../../external/ChinaTravel')
sys.path.insert(0, CHINATRAVEL_PATH)

from evaluation.evaluation import (
    validate_json,
    PLAN_SCHEMA,
    evaluate_schema_constraints,
    evaluate_commonsense_constraints,
    evaluate_hard_constraints
)


class EvaluatorWrapper:
    """Wrapper for ChinaTravel evaluation functions."""

    def __init__(self, verbose: bool = False, lang: str = 'zh'):
        """
        Initialize evaluator wrapper.

        Args:
            verbose: Whether to print detailed evaluation info
            lang: Language for evaluation ('zh' or 'en')
        """
        self.verbose = verbose
        self.lang = lang

    def evaluate_single(
        self,
        plan_id: str,
        query: Dict[str, Any],
        plan: List[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Evaluate a single plan through all three layers.

        Args:
            plan_id: Unique identifier for this plan
            query: Query dict with org, dest, days, people_number, target_city
            plan: Generated plan in correct format

        Returns:
            Dict with evaluation results:
                - schema_valid: bool
                - commonsense_macro: float (0-100)
                - commonsense_micro: float (0-100)
                - hard_pass: bool
                - details: Dict with detailed scores
        """
        result = {
            'plan_id': plan_id,
            'schema_valid': False,
            'commonsense_macro': 0.0,
            'commonsense_micro': 0.0,
            'hard_pass': False,
            'details': {}
        }

        # Layer 1: Schema validation
        try:
            schema_valid = validate_json(plan, PLAN_SCHEMA)
            result['schema_valid'] = schema_valid

            if not schema_valid:
                if self.verbose:
                    print(f"[{plan_id}] Schema validation failed")
                return result

        except Exception as e:
            if self.verbose:
                print(f"[{plan_id}] Schema validation error: {e}")
            return result

        # Layer 2: Commonsense constraints
        try:
            data_index = [plan_id]
            query_dict = {plan_id: query}
            plan_dict = {plan_id: plan}

            macro_acc, micro_acc, result_df, pass_ids = evaluate_commonsense_constraints(
                data_index, query_dict, plan_dict, verbose=False, lang=self.lang
            )

            result['commonsense_macro'] = macro_acc
            result['commonsense_micro'] = micro_acc

            # Extract detailed scores from result_df
            if not result_df.empty:
                row = result_df.iloc[0]
                result['details']['commonsense'] = {
                    'activity_grounded': row.get('Is_activity_grounded', None),
                    'intercity_transport': row.get('Is_intercity_transport_correct', None),
                    'attractions_correct': row.get('Is_attractions_correct', None),
                    'hotels_correct': row.get('Is_hotels_correct', None),
                    'restaurants_correct': row.get('Is_restaurants_correct', None),
                    'transport_correct': row.get('Is_transport_correct', None),
                    'time_correct': row.get('Is_time_correct', None),
                    'space_correct': row.get('Is_space_correct', None),
                }

            if self.verbose:
                print(f"[{plan_id}] Commonsense: macro={macro_acc}%, micro={micro_acc}%")

        except Exception as e:
            if self.verbose:
                print(f"[{plan_id}] Commonsense evaluation error: {e}")
            # Continue to hard constraints even if commonsense fails

        # Layer 3: Hard constraints
        try:
            data_index = [plan_id]
            query_dict = {plan_id: query}
            plan_dict = {plan_id: plan}

            hard_acc, result_df, pass_ids = evaluate_hard_constraints(
                data_index, query_dict, plan_dict, verbose=False, lang=self.lang
            )

            result['hard_pass'] = plan_id in pass_ids

            if self.verbose:
                print(f"[{plan_id}] Hard constraints: {'PASS' if result['hard_pass'] else 'FAIL'}")

        except Exception as e:
            if self.verbose:
                print(f"[{plan_id}] Hard constraint evaluation error: {e}")

        return result

    def evaluate_batch(
        self,
        plan_ids: List[str],
        queries: Dict[str, Dict[str, Any]],
        plans: Dict[str, List[List[Dict[str, Any]]]]
    ) -> pd.DataFrame:
        """
        Evaluate a batch of plans.

        Args:
            plan_ids: List of plan identifiers
            queries: Dict mapping plan_id to query
            plans: Dict mapping plan_id to plan

        Returns:
            DataFrame with evaluation results
        """
        results = []

        for plan_id in plan_ids:
            query = queries.get(plan_id)
            plan = plans.get(plan_id)

            if query is None or plan is None:
                print(f"Warning: Missing query or plan for {plan_id}")
                continue

            result = self.evaluate_single(plan_id, query, plan)
            results.append(result)

        return pd.DataFrame(results)

    @staticmethod
    def compute_summary_stats(results_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Compute summary statistics from evaluation results.

        Args:
            results_df: DataFrame from evaluate_batch

        Returns:
            Dict with summary statistics
        """
        n_total = len(results_df)
        n_schema_pass = results_df['schema_valid'].sum()
        n_hard_pass = results_df['hard_pass'].sum()

        avg_commonsense_macro = results_df['commonsense_macro'].mean()
        avg_commonsense_micro = results_df['commonsense_micro'].mean()

        return {
            'total_count': n_total,
            'schema_pass_rate': n_schema_pass / n_total if n_total > 0 else 0.0,
            'schema_pass_count': n_schema_pass,
            'hard_pass_rate': n_hard_pass / n_total if n_total > 0 else 0.0,
            'hard_pass_count': n_hard_pass,
            'commonsense_macro_avg': avg_commonsense_macro,
            'commonsense_micro_avg': avg_commonsense_micro,
        }

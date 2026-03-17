# src/evaluator.py

import pandas as pd
from sklearn.metrics import accuracy_score


def normalize_answer(answer: str) -> str:
    """
    Normalize answer strings so that comparison is more consistent.
    """

    return answer.strip().lower()


def compute_accuracy(records: list, prediction_key: str) -> float:
    """
    Compute classification accuracy from a list of result dictionaries.
    """

    y_true = [normalize_answer(item["ground_truth"]) for item in records]
    y_pred = [normalize_answer(item[prediction_key]) for item in records]

    return accuracy_score(y_true, y_pred)


def build_metrics_table(debate_results, direct_results, self_consistency_results):
    """
    Build a small results table comparing the three methods.
    """

    rows = [
        {
            "method": "Debate + Judge",
            "accuracy": compute_accuracy(debate_results, "judge_answer"),
        },
        {
            "method": "Direct QA",
            "accuracy": compute_accuracy(direct_results, "predicted_answer"),
        },
        {
            "method": "Self-Consistency",
            "accuracy": compute_accuracy(self_consistency_results, "predicted_answer"),
        },
    ]

    return pd.DataFrame(rows)
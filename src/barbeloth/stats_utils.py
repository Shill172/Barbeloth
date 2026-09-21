from statsmodels.stats.proportion import proportion_confint
from scipy import stats

def accuracy_with_ci(hits: int, n: int):
    """Point estimate + 95% Wilson interval."""
    accuracy = hits / n
    lo, hi = proportion_confint(hits, n, method="wilson")
    return accuracy, lo, hi


def mcnemar_test(model_correct: list[bool], baseline_correct: list[bool]):
    """Paired significance test. Inputs must be same length, same order,
    one entry per real event (not per guess)."""
    b = sum(m and not l for m, l in zip(model_correct, baseline_correct))  # model-only
    c = sum(l and not m for m, l in zip(model_correct, baseline_correct))  # baseline-only
    n = b + c
    if n == 0:
        return b, c, 1.0
    p = stats.binomtest(min(b, c), n, 0.5).pvalue
    return b, c, p


def random_baseline_accuracy( pool_sizes: list[int], slot_counts: list[int]):
    """Expected accuracy of guessing uniformly at random, per patch, averaged."""
    
    total_slots = sum(slot_counts)

    expected_hits = sum(
        n * n / pool
        for n, pool in zip(slot_counts, pool_sizes)
        if pool > 0
    )

    return expected_hits / total_slots
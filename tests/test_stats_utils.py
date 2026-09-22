from barbeloth.stats_utils import accuracy_with_ci, mcnemar_test

def test_accuracy_with_ci_known_case():
    acc, lo, hi = accuracy_with_ci(18, 41)
    assert round(acc, 3) == 0.439
    assert round(lo, 3) == 0.299
    assert round(hi, 3) == 0.590

def test_mcnemar_matches_current_backtest():
    from barbeloth.evaluate import backtest_and_collect_records
    records = backtest_and_collect_records(5.0, 6.5)
    model_correct = [r["model_correct"] for r in records]
    baseline_correct = [r["baseline_correct"] for r in records]
    b, c, p = mcnemar_test(model_correct, baseline_correct)
    assert (b, c) == (16, 9)
    assert round(p, 4) == 0.2295
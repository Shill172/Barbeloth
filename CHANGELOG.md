# Barbeloth Changelog

## [Unreleased]

### Added
- `stats_util.py`: Wilson CI (`accuracy_with_ci`), McNemar's exact test
  (`mcnemar_test`), and a point-in-time random-guess baseline
  (`random_baseline_accuracy`)
- `backtest_and_collect_records()` and `get_random_acc()` in `evaluate.py`:
  build paired per-event correctness records and compute the random-guess
  floor from pre-patch appearance history

Current (pre-lookahead-fix) backtest: model vs. LWW accuracy difference is
not statistically significant (McNemar's p ≈ 0.23, 16 vs. 9 discordant
pairs out of 41 events). Random-guess floor ≈ 7.7%.

### Changed
- Repo hygiene: removed dead test files, added .gitignore, pinned dependencies
- Restructured `src/` into an installable `barbeloth` package; paths now
  resolve relative to the file, not the CWD

## [0.1.0]: Original
- Random forest classifier, walk-forward backtest, LWW baseline comparison.
  43.9% (18/41) vs 26.8% (11/41), unvalidated for significance.
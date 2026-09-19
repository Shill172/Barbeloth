# Barbeloth Changelog

## [Unreleased]

### Changed
- Repo hygiene: removed dead test files, added .gitignore, pinned dependencies
- Restructured `src/` into an installable `barbeloth` package; paths now
  resolve relative to the file, not the CWD

## [0.1.0]: Original
- Random forest classifier, walk-forward backtest, LWW baseline comparison.
  43.9% (18/41) vs 26.8% (11/41), unvalidated for significance.
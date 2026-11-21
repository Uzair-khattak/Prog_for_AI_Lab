"""Checks that every package imports and that the datasets are in place."""
import importlib, sys
from pathlib import Path

print("Python", sys.version.split()[0], "|", sys.executable)
pk = ["numpy", "pandas", "scipy", "sklearn", "matplotlib", "seaborn", "PIL", "skimage", "joblib", "docx",
      "tpot", "fastapi", "uvicorn", "pydantic", "httpx", "requests", "streamlit", "nbformat", "jupyterlab"]
bad = []
for p in pk:
    try:
        m = importlib.import_module(p)
        print(f"  OK   {p:12s} {getattr(m, '__version__', '')}")
    except Exception as e:
        bad.append(p); print(f"  FAIL {p:12s} {e}")
print("\nDatasets:")
root = Path(__file__).resolve().parent
checks = {
    "Q1  data/q1/*.csv": any((root / "data/q1").glob("*.csv")) or any((root / "data/q1").glob("*.xls*")),
    "Q2a data/q2_heart/*.csv": any((root / "data/q2_heart").glob("*.csv")),
    "Q2b data/q2_intel/ (seg_train + seg_test)": any((root / "data/q2_intel").rglob("seg_train")) and any((root / "data/q2_intel").rglob("seg_test")),
    "Q3  data/q3_adult/*.csv (optional - OpenML fallback)": any((root / "data/q3_adult").glob("*.csv")),
}
for k, v in checks.items():
    print(f"  {'OK     ' if v else 'MISSING'} {k}")
print("\nEnvironment OK" if not bad else f"\nProblems with: {bad}")

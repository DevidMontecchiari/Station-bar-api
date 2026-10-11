"""Check the selected implementation using temporary data, without a running server."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variant", choices=["starter", "solution"])
    parser.add_argument("--full", action="store_true", help="Run all CRUD reference checks (solution only).")
    args = parser.parse_args()
    if args.full and args.variant == "starter":
        parser.error("The focused starter uses: python check.py starter. Full CRUD checks use: python check.py solution --full.")
    target = ROOT / args.variant
    suite = ROOT / ("solution/tests" if args.full else "checks/test_create_order.py")
    print(f"Checking {args.variant}: {target / 'bar_api'}", flush=True)
    if args.variant == "starter":
        print("Order-creation checks should fail until you complete the marked handler.", flush=True)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         "-c", str(ROOT / "pyproject.toml"), "-o", f'pythonpath="{target.as_posix()}"' , str(suite)],
        cwd=ROOT, env={**os.environ, "BAR_CHECK_VARIANT": args.variant,
                       "PYTHONDONTWRITEBYTECODE": "1"})
    return result.returncode

if __name__ == "__main__":
    raise SystemExit(main())

"""Run a classroom version of the Station Bar API."""
import argparse
import os
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variant", nargs="?", choices=["solution", "starter"], default="solution")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    folder = Path(__file__).resolve().parent / args.variant
    os.chdir(folder)
    sys.path.insert(0, str(folder))
    import uvicorn
    print(f"{args.variant}: http://127.0.0.1:{args.port}/docs", flush=True)
    uvicorn.run("main:app", host="127.0.0.1", port=args.port,
                reload=args.reload, reload_dirs=[str(folder)] if args.reload else None)


if __name__ == "__main__":
    main()

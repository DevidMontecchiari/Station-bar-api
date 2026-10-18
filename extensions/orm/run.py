"""From the repository root: python extensions/orm/run.py"""
import argparse
from pathlib import Path
import uvicorn

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the optional database example")
    parser.add_argument("--host", default="127.0.0.1", choices=["127.0.0.1", "0.0.0.0"])
    parser.add_argument("--port", default=8002, type=int)
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent
    uvicorn.run("main:app", app_dir=str(folder), host=args.host, port=args.port)

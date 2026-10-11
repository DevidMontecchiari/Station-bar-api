"""Stop the server first. Reset only this example's working data."""
import argparse, os, shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--confirm",action="store_true");args=p.parse_args()
if not args.confirm:
    p.error("Use --confirm to replace the demo data with seed.json. Stop the server first.")
dest=Path(os.environ.get("BAR_DATA_FILE",Path(__file__).with_name("data.json")))
dest.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(Path(__file__).with_name("seed.json"),dest)
print(f"Demo data reset: {dest}")

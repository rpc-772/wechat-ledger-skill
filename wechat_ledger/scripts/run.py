import os
import runpy
import sys
from pathlib import Path


def main():
    repo_root = Path(__file__).resolve().parents[3]
    target = repo_root / "scripts" / "wechat_ledger_to_notion.py"
    os.chdir(repo_root)
    sys.argv[0] = str(target)
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()

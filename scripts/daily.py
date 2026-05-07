#!/usr/bin/env python3
"""温泉乡·漫游 · daily.py — 每日 git 打卡"""
import json, os, subprocess, sys
from datetime import datetime, timezone, timedelta

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL_PATH = os.path.join(REPO_DIR, "data", "pool.json")
LOG_PATH = os.path.join(REPO_DIR, "data", "log.json")
DATA_KEY = "spots"
HAIKU_KEY = "phrases"


def jst_now():
    return datetime.now(timezone(timedelta(hours=9)))


def today_seed():
    n = jst_now()
    return n.year * 10000 + n.month * 100 + n.day


def main():
    with open(POOL_PATH, "r", encoding="utf-8") as f:
        pool = json.load(f)

    seed = today_seed()
    item = pool[DATA_KEY][seed % len(pool[DATA_KEY])]
    line = pool[HAIKU_KEY][seed % len(pool[HAIKU_KEY])]
    today = jst_now().strftime("%Y-%m-%d")

    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            log = json.load(f)
    else:
        log = {"entries": []}

    if log["entries"] and log["entries"][-1].get("date") == today:
        print(f"[skip] today {today} already logged")
        return 0

    log["entries"].append({
        "date": today, "seed": seed,
        "id": item.get("id"),
        "name": item.get("name_zh") or item.get("name"),
        "phrase": line,
    })
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"[ok] {today} logged: {item.get('name_zh') or item.get('name')}")

    if os.environ.get("SKIP_GIT"):
        return 0
    os.chdir(REPO_DIR)
    subprocess.run(["git", "add", "data/log.json"], check=True)
    msg = f"daily: {today} · {item.get('name_zh') or item.get('name')}"
    r = subprocess.run(["git", "commit", "-m", msg], capture_output=True, text=True)
    if r.returncode and "nothing to commit" not in (r.stdout + r.stderr):
        print(r.stderr); return 1
    p = subprocess.run(["git", "push"], capture_output=True, text=True)
    if p.returncode:
        print("[push failed]", p.stderr); return 1
    print("[push ok]")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)

#!/usr/bin/env python3
"""
lazy_index.py — load .codexa/manifest/index.json, regenerating if stale
"""

import json
import time
from pathlib import Path
from collections import defaultdict
from datetime import datetime

MANIFEST_ROOT = Path(".codexa/manifest")
INDEX_FILE = MANIFEST_ROOT / "index.json"

# --- Core index builder (lightweight re-use of update_index.py) --------
def _load_json(path: Path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []

def _gather_nodes():
    nodes = []
    for path in MANIFEST_ROOT.rglob("*.json"):
        if path.name in ("index.json", "manifest.json"):
            continue
        data = _load_json(path)
        if isinstance(data, list):
            nodes.extend(data)
        elif isinstance(data, dict):
            nodes.append(data)
    return nodes

def _build_index(nodes):
    index = defaultdict(list)
    by_domain = defaultdict(list)
    by_milestone = defaultdict(list)
    depends_map = defaultdict(list)

    for n in nodes:
        _id = n.get("id")
        _type = n.get("type", "unknown").lower()
        if not _id:
            continue
        index[_type + "s"].append(_id)
        for d in n.get("domains", []):
            by_domain[d].append(_id)
        for m in n.get("milestones", []):
            by_milestone[m].append(_id)
        for dep in n.get("depends_on", []):
            depends_map[_id].append(dep)

    return {
        "summary": {
            "domains": len(by_domain),
            "milestones": len(by_milestone),
            "requirements": len(index.get("requirements", [])),
            "tests": len(index.get("tests", [])),
            "total_nodes": len(nodes)
        },
        "by_type": dict(index),
        "by_domain": dict(by_domain),
        "by_milestone": dict(by_milestone),
        "dependencies": dict(depends_map),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def _is_stale() -> bool:
    if not INDEX_FILE.exists():
        return True
    index_mtime = INDEX_FILE.stat().st_mtime
    for path in MANIFEST_ROOT.rglob("*.json"):
        if path.name in ("index.json", "manifest.json"):
            continue
        if path.stat().st_mtime > index_mtime:
            return True
    return False

# --- Public API --------------------------------------------------------
def load_index(force_regen=False):
    """
    Returns a current index dict, regenerating if missing or stale.
    """
    if force_regen or _is_stale():
        print("♻️  Regenerating manifest index ...")
        nodes = _gather_nodes()
        index = _build_index(nodes)
        INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(INDEX_FILE, "w") as f:
            json.dump(index, f, indent=2)
        print(f"✅ Index refreshed at {datetime.now().strftime('%H:%M:%S')} "
              f"({index['summary']['total_nodes']} nodes)")
    else:
        print("✅ Using cached index (up to date)")
    with open(INDEX_FILE) as f:
        return json.load(f)

if __name__ == "__main__":
    idx = load_index()
    print(json.dumps(idx["summary"], indent=2))
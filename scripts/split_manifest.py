#!/usr/bin/env python3
"""
Splits a monolithic manifest.json (Codexa format)
into domain-, milestone-, and requirement-level files.
"""

import json, os, shutil
from pathlib import Path
from datetime import datetime

# --- Paths ------------------------------------------------------------
root = Path(".codexa/manifest")
source_file = Path(".codexa/manifest.json")
domains_file = root / "domains.json"
milestones_file = root / "milestones.json"
req_dir = root / "requirements"
tests_file = root / "tests.json"
index_file = root / "index.json"

# --- Safety / setup ---------------------------------------------------
if not source_file.exists():
    raise SystemExit(f"❌ Cannot find {source_file}. Generate manifest.json first.")

if root.exists():
    backup = root.with_name(f"manifest_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copytree(root, backup, dirs_exist_ok=True)
    print(f"📦 Existing manifest backed up to {backup}")

req_dir.mkdir(parents=True, exist_ok=True)

# --- Load manifest ----------------------------------------------------
with open(source_file) as f:
    manifest = json.load(f)

# Support two manifest shapes:
# - A dict containing a "nodes" key (original Codexa format)
# - A top-level list of node objects (some exports use this)
if isinstance(manifest, list):
    nodes = manifest
else:
    # fall back to common keys; default to empty list to avoid AttributeError
    nodes = manifest.get("nodes") or manifest.get("items") or []

print(f"🔍 Loaded {len(nodes)} nodes from manifest.json")

domains, milestones, requirements, tests = [], [], [], []
index = {"domains": [], "milestones": [], "requirements": [], "tests": []}

for node in nodes:
    node_type = node.get("type", "").lower()
    if node_type == "domain":
        domains.append(node)
        index["domains"].append(node["id"])
    elif node_type == "milestone":
        milestones.append(node)
        index["milestones"].append(node["id"])
    elif node_type == "requirement":
        requirements.append(node)
        index["requirements"].append(node["id"])
    elif node_type == "test":
        tests.append(node)
        index["tests"].append(node["id"])

# --- Write domain & milestone files -----------------------------------
with open(domains_file, "w") as f:
    json.dump(domains, f, indent=2)
with open(milestones_file, "w") as f:
    json.dump(milestones, f, indent=2)
if tests:
    with open(tests_file, "w") as f:
        json.dump(tests, f, indent=2)

# --- Write individual requirement files -------------------------------
for r in requirements:
    rid = r["id"].replace("/", "_")
    with open(req_dir / f"{rid}.json", "w") as f:
        json.dump(r, f, indent=2)

# --- Write index ------------------------------------------------------
with open(index_file, "w") as f:
    json.dump(index, f, indent=2)

print(f"✅ Split complete:")
print(f"  Domains:      {len(domains)}")
print(f"  Milestones:   {len(milestones)}")
print(f"  Requirements: {len(requirements)}")
print(f"  Tests:        {len(tests)}")
print(f"📁 Output in {root.resolve()}")

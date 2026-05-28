#!/usr/bin/env python3
"""Parse all Claude Code session logs (~/.claude/projects/**/*.jsonl)
into a local SQLite database for the dashboard."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Iterable

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
DEFAULT_DB = Path(__file__).parent / "data" / "tracker.db"

# Base input/output price (USD per 1M tokens).
# Source: platform.claude.com/docs/en/about-claude/pricing (verified 2026-05).
# IMPORTANT: Opus dropped from $15/$75 to $5/$25 starting with Opus 4.5.
PRICING: dict[str, dict[str, float]] = {
    "opus-4.5+":   {"input": 5.00,  "output": 25.00},   # Opus 4.5, 4.6, 4.7
    "opus-legacy": {"input": 15.00, "output": 75.00},   # Opus 4, 4.1, Opus 3 (deprecated)
    "sonnet-4":    {"input": 3.00,  "output": 15.00},   # Sonnet 3.x, 4, 4.5, 4.6
    "haiku-4":     {"input": 1.00,  "output": 5.00},    # Haiku 4.5
    "haiku-3-5":   {"input": 0.80,  "output": 4.00},
    "haiku-3":     {"input": 0.25,  "output": 1.25},
    "unknown":     {"input": 3.00,  "output": 15.00},
}

# Universal Anthropic cache multipliers (relative to base input price).
CACHE_READ_MULT = 0.10      # cache hit  = 10% of input
CACHE_WRITE_5M_MULT = 1.25  # 5-min write = 125% of input
CACHE_WRITE_1H_MULT = 2.00  # 1-hour write = 200% of input


def model_family(model: str | None) -> str:
    if not model:
        return "unknown"
    m = model.lower()

    om = re.search(r"opus-(\d+)(?:-(\d+))?", m)
    if om:
        major = int(om.group(1))
        minor = int(om.group(2)) if (om.group(2) and len(om.group(2)) <= 2) else 0
        if major >= 5 or (major == 4 and minor >= 5):
            return "opus-4.5+"
        return "opus-legacy"  # Opus 4, 4.1, Opus 3

    if "sonnet" in m:
        return "sonnet-4"  # all Sonnet tiers share $3/$15

    hm = re.search(r"haiku-(\d+)(?:-(\d+))?", m)
    if hm:
        major = int(hm.group(1))
        minor = int(hm.group(2)) if (hm.group(2) and len(hm.group(2)) <= 2) else 0
        if major >= 4:
            return "haiku-4"
        if major == 3 and minor >= 5:
            return "haiku-3-5"
        return "haiku-3"

    return "unknown"


def compute_cost(model: str | None, usage: dict[str, Any]) -> float:
    """Exact cost: caches are multipliers of the model's base input price.
    Distinguishes 5-minute vs 1-hour cache writes when the breakdown is present."""
    p = PRICING[model_family(model)]
    input_price = p["input"]

    # Cache write split (5m vs 1h) — fall back to the flat total as 5m if absent.
    cache_creation = usage.get("cache_creation") or {}
    cc_5m = cache_creation.get("ephemeral_5m_input_tokens", 0) or 0
    cc_1h = cache_creation.get("ephemeral_1h_input_tokens", 0) or 0
    if not cache_creation:
        cc_5m = usage.get("cache_creation_input_tokens", 0) or 0

    return (
        usage.get("input_tokens", 0) * input_price
        + usage.get("output_tokens", 0) * p["output"]
        + (usage.get("cache_read_input_tokens", 0) or 0) * (input_price * CACHE_READ_MULT)
        + cc_5m * (input_price * CACHE_WRITE_5M_MULT)
        + cc_1h * (input_price * CACHE_WRITE_1H_MULT)
    ) / 1_000_000


def extract_text(content: Any) -> str:
    """Flatten Claude message content (string or list of blocks) to plain text."""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        btype = block.get("type")
        if btype == "text":
            parts.append(block.get("text", ""))
        elif btype == "tool_use":
            name = block.get("name", "tool")
            inp = json.dumps(block.get("input", {}), ensure_ascii=False)[:500]
            parts.append(f"[tool_use:{name}] {inp}")
        elif btype == "tool_result":
            inner = block.get("content", "")
            parts.append(f"[tool_result] {extract_text(inner) if isinstance(inner, (list, str)) else str(inner)[:500]}")
        elif btype == "thinking":
            parts.append(f"[thinking] {block.get('thinking', '')[:500]}")
        elif btype == "image":
            parts.append("[image]")
    return "\n".join(parts)


SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    uuid TEXT PRIMARY KEY,
    session_id TEXT,
    parent_uuid TEXT,
    timestamp TEXT,
    role TEXT,
    model TEXT,
    content TEXT,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cache_read_tokens INTEGER DEFAULT 0,
    cache_create_tokens INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0,
    project_path TEXT,
    project_label TEXT,
    entrypoint TEXT,
    git_branch TEXT,
    version TEXT,
    file_path TEXT
);
CREATE INDEX IF NOT EXISTS idx_session ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_project ON messages(project_path);
CREATE INDEX IF NOT EXISTS idx_role ON messages(role);
CREATE INDEX IF NOT EXISTS idx_model ON messages(model);
"""


def project_label_from_path(p: str | None) -> str:
    if not p:
        return "(unknown)"
    return Path(p).name or p


def open_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    return conn


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                print(f"  ⚠ {path.name}:{i} JSON invalide, skip", file=sys.stderr)


def parse_file(path: Path, conn: sqlite3.Connection) -> tuple[int, int]:
    """Insert all messages from a JSONL into the DB. Returns (inserted, skipped)."""
    inserted = skipped = 0
    rows: list[tuple] = []
    for entry in iter_jsonl(path):
        etype = entry.get("type")
        if etype not in ("user", "assistant"):
            continue
        uuid = entry.get("uuid")
        if not uuid:
            continue
        msg = entry.get("message") or {}
        usage = msg.get("usage") or {}
        content_text = extract_text(msg.get("content"))
        model = msg.get("model")
        rows.append((
            uuid,
            entry.get("sessionId"),
            entry.get("parentUuid"),
            entry.get("timestamp"),
            etype,
            model,
            content_text,
            usage.get("input_tokens", 0) or 0,
            usage.get("output_tokens", 0) or 0,
            usage.get("cache_read_input_tokens", 0) or 0,
            usage.get("cache_creation_input_tokens", 0) or 0,
            compute_cost(model, usage),
            entry.get("cwd"),
            project_label_from_path(entry.get("cwd")),
            entry.get("entrypoint"),
            entry.get("gitBranch"),
            entry.get("version"),
            str(path),
        ))
    if not rows:
        return 0, 0
    cur = conn.cursor()
    for row in rows:
        try:
            cur.execute(
                """INSERT OR REPLACE INTO messages
                   (uuid, session_id, parent_uuid, timestamp, role, model, content,
                    input_tokens, output_tokens, cache_read_tokens, cache_create_tokens,
                    cost_usd, project_path, project_label, entrypoint, git_branch, version, file_path)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                row,
            )
            inserted += 1
        except sqlite3.Error as e:
            print(f"  ⚠ SQLite: {e}", file=sys.stderr)
            skipped += 1
    conn.commit()
    return inserted, skipped


def main() -> int:
    ap = argparse.ArgumentParser(description="Parse Claude Code sessions into SQLite")
    ap.add_argument("--projects-dir", type=Path, default=CLAUDE_PROJECTS_DIR,
                    help=f"default: {CLAUDE_PROJECTS_DIR}")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB,
                    help=f"default: {DEFAULT_DB}")
    ap.add_argument("--reset", action="store_true", help="drop DB before parsing")
    args = ap.parse_args()

    if args.reset and args.db.exists():
        args.db.unlink()
        print(f"🗑  DB supprimée: {args.db}")

    if not args.projects_dir.exists():
        print(f"❌ Dossier introuvable: {args.projects_dir}", file=sys.stderr)
        return 1

    files = sorted(args.projects_dir.rglob("*.jsonl"))
    print(f"📂 {len(files)} fichiers de session à parser (incl. subagents)")

    conn = open_db(args.db)
    total_inserted = total_skipped = 0
    for i, f in enumerate(files, 1):
        ins, skp = parse_file(f, conn)
        total_inserted += ins
        total_skipped += skp
        if i % 25 == 0 or i == len(files):
            print(f"  [{i}/{len(files)}] {ins} ins / {skp} skip — {f.parent.name[:60]}")

    # Quick stats
    cur = conn.cursor()
    total_msgs = cur.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    total_sessions = cur.execute("SELECT COUNT(DISTINCT session_id) FROM messages").fetchone()[0]
    total_cost = cur.execute("SELECT COALESCE(SUM(cost_usd), 0) FROM messages").fetchone()[0]
    total_in, total_out, total_cr, total_cc = cur.execute(
        "SELECT COALESCE(SUM(input_tokens),0), COALESCE(SUM(output_tokens),0), "
        "COALESCE(SUM(cache_read_tokens),0), COALESCE(SUM(cache_create_tokens),0) "
        "FROM messages"
    ).fetchone()
    conn.close()

    print()
    print(f"✅ {total_inserted} messages insérés ({total_skipped} skip)")
    print(f"📊 {total_msgs:,} messages total | {total_sessions:,} sessions")
    print(f"🔢 input={total_in:,} | output={total_out:,} | cache_read={total_cr:,} | cache_create={total_cc:,}")
    print(f"💰 coût estimé: ${total_cost:,.2f}")
    print(f"💾 DB: {args.db}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

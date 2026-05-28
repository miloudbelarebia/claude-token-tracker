"""Regression tests for the JSONL parser (tracker.py).

Critical case: Claude Code writes ONE API call as MULTIPLE JSONL lines
(one per content block: thinking / text / tool_use), and each line repeats
the SAME `usage`. The parser must count that usage ONCE, not sum the lines.

Run:
    python -m unittest discover -s tests -v
"""

import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tracker import parse_file, open_db, SCHEMA  # noqa: E402


def _line(**kw):
    return json.dumps(kw)


class TestNoDoubleCounting(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.jsonl = Path(self.tmp) / "session.jsonl"
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(SCHEMA)

    def tearDown(self):
        self.conn.close()

    def _write(self, lines):
        self.jsonl.write_text("\n".join(lines))

    def test_same_request_id_counted_once(self):
        # One API call (req_A) split across 3 lines, each repeating usage.
        usage = {"input_tokens": 10, "output_tokens": 500,
                 "cache_read_input_tokens": 1000, "cache_creation_input_tokens": 0}
        self._write([
            _line(type="user", uuid="u1", sessionId="s", timestamp="2026-05-01T10:00:00Z",
                  message={"role": "user", "content": "hello"}),
            _line(type="assistant", uuid="a1", requestId="req_A", sessionId="s",
                  timestamp="2026-05-01T10:00:01Z",
                  message={"id": "msg_A", "role": "assistant", "model": "claude-opus-4-7",
                           "content": [{"type": "thinking", "thinking": "..."}], "usage": usage}),
            _line(type="assistant", uuid="a2", requestId="req_A", sessionId="s",
                  timestamp="2026-05-01T10:00:02Z",
                  message={"id": "msg_A", "role": "assistant", "model": "claude-opus-4-7",
                           "content": [{"type": "text", "text": "hi"}], "usage": usage}),
            _line(type="assistant", uuid="a3", requestId="req_A", sessionId="s",
                  timestamp="2026-05-01T10:00:03Z",
                  message={"id": "msg_A", "role": "assistant", "model": "claude-opus-4-7",
                           "content": [{"type": "tool_use", "name": "Bash", "input": {}}], "usage": usage}),
        ])
        parse_file(self.jsonl, self.conn)
        cur = self.conn.cursor()
        n_assist = cur.execute("SELECT COUNT(*) FROM messages WHERE role='assistant'").fetchone()[0]
        out = cur.execute("SELECT COALESCE(SUM(output_tokens),0) FROM messages WHERE role='assistant'").fetchone()[0]
        cost = cur.execute("SELECT COALESCE(SUM(cost_usd),0) FROM messages WHERE role='assistant'").fetchone()[0]

        # 3 lines, 1 real API call → must be ONE assistant row, 500 output tokens (not 1500)
        self.assertEqual(n_assist, 1, "3 lines of one API call must collapse to 1 row")
        self.assertEqual(out, 500, "output tokens must be counted once, not summed")
        # cost = (10*5 + 500*25 + 1000*0.5) / 1e6 = $0.013
        self.assertAlmostEqual(cost, (10*5 + 500*25 + 1000*0.5)/1e6, places=6)

    def test_distinct_request_ids_counted_separately(self):
        # Two genuinely distinct API calls (tool chain) → must BOTH be counted.
        u1 = {"input_tokens": 10, "output_tokens": 300}
        u2 = {"input_tokens": 20, "output_tokens": 400}
        self._write([
            _line(type="assistant", uuid="a1", requestId="req_1", sessionId="s",
                  timestamp="2026-05-01T10:00:01Z",
                  message={"id": "msg_1", "role": "assistant", "model": "claude-opus-4-7",
                           "content": [{"type": "tool_use", "name": "Bash", "input": {}}], "usage": u1}),
            _line(type="assistant", uuid="a2", requestId="req_2", sessionId="s",
                  timestamp="2026-05-01T10:00:05Z",
                  message={"id": "msg_2", "role": "assistant", "model": "claude-opus-4-7",
                           "content": [{"type": "text", "text": "done"}], "usage": u2}),
        ])
        parse_file(self.jsonl, self.conn)
        cur = self.conn.cursor()
        n = cur.execute("SELECT COUNT(*) FROM messages WHERE role='assistant'").fetchone()[0]
        out = cur.execute("SELECT COALESCE(SUM(output_tokens),0) FROM messages WHERE role='assistant'").fetchone()[0]
        self.assertEqual(n, 2, "two distinct API calls must stay separate")
        self.assertEqual(out, 700, "300 + 400 should both count")


if __name__ == "__main__":
    unittest.main(verbosity=2)

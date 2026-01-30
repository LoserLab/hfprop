"""SQLite-based condition history logging.

Database location: ~/.local/share/hfprop/history.db (XDG_DATA_HOME compliant)
"""

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from hfprop.models import PropagationReport

SCHEMA = """\
CREATE TABLE IF NOT EXISTS conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    sfi INTEGER NOT NULL,
    ssn INTEGER NOT NULL,
    k_index INTEGER NOT NULL,
    a_index INTEGER NOT NULL,
    xray TEXT NOT NULL,
    geomag TEXT NOT NULL,
    bands TEXT NOT NULL
)"""


def get_data_dir() -> Path:
    xdg = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg) if xdg else Path.home() / ".local" / "share"
    data_dir = base / "hfprop"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


class HistoryDB:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = str(db_path or get_data_dir() / "history.db")
        self._ensure_schema()

    def _ensure_schema(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(SCHEMA)

    def log(self, report: PropagationReport) -> None:
        """Append a condition record from a live fetch."""
        bands_json = json.dumps([
            {"name": b.band_name, "day": b.day.value, "night": b.night.value}
            for b in report.bands
        ])
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO conditions "
                "(timestamp, sfi, ssn, k_index, a_index, xray, geomag, bands) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    report.solar.solar_flux,
                    report.solar.sunspot_number,
                    report.solar.k_index,
                    report.solar.a_index,
                    report.solar.xray,
                    report.solar.geomag_field.value,
                    bands_json,
                ),
            )

    def query(self, days: int = 7) -> List[dict]:
        """Return recent entries as dicts, newest first."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM conditions "
                "WHERE timestamp >= datetime('now', ?) "
                "ORDER BY timestamp DESC",
                (f"-{days} days",),
            )
            return [dict(row) for row in cursor.fetchall()]

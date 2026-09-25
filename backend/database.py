"""
SQLite Database Layer for Anime Reality AI Backend.
Stores persistent records for jobs, styles, generation history, and model registry.
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

DB_PATH = Path("backend/anime_reality.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database with row factory."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables for jobs, styles, and history."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Jobs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        status TEXT NOT NULL,
        progress INTEGER DEFAULT 0,
        style TEXT NOT NULL,
        quality TEXT NOT NULL,
        input_path TEXT NOT NULL,
        output_path TEXT,
        error_message TEXT,
        created_at TEXT NOT NULL,
        started_at TEXT,
        completed_at TEXT
    )
    """)

    # 2. Styles Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS styles (
        name TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        description TEXT,
        model TEXT NOT NULL,
        lora TEXT,
        strength REAL DEFAULT 1.0,
        recommended_resolution INTEGER DEFAULT 512,
        license TEXT
    )
    """)

    # 3. Generation History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id TEXT PRIMARY KEY,
        job_id TEXT NOT NULL,
        type TEXT NOT NULL,
        style TEXT NOT NULL,
        output_path TEXT NOT NULL,
        duration_sec REAL,
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()

    # Seed default styles from styles/ directory if empty
    cursor.execute("SELECT COUNT(*) FROM styles")
    if cursor.fetchone()[0] == 0:
        styles_dir = Path("styles")
        if styles_dir.exists():
            for s_dir in styles_dir.iterdir():
                style_json = s_dir / "style.json"
                if style_json.exists():
                    try:
                        with open(style_json, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        cursor.execute("""
                        INSERT OR REPLACE INTO styles (name, display_name, description, model, lora, strength, recommended_resolution, license)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            data.get("name", s_dir.name),
                            data.get("display_name", s_dir.name.capitalize()),
                            data.get("description", ""),
                            data.get("model", "anime_lightweight_v1"),
                            data.get("lora"),
                            data.get("strength", 1.0),
                            data.get("recommended_resolution", 512),
                            data.get("license", "MIT")
                        ))
                    except Exception:
                        pass
            conn.commit()

    conn.close()


# Database helper operations
def save_job(job_data: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO jobs (id, type, status, progress, style, quality, input_path, output_path, error_message, created_at, started_at, completed_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job_data["id"],
        job_data["type"],
        job_data["status"],
        job_data.get("progress", 0),
        job_data["style"],
        job_data["quality"],
        job_data["input_path"],
        job_data.get("output_path"),
        job_data.get("error_message"),
        job_data["created_at"],
        job_data.get("started_at"),
        job_data.get("completed_at")
    ))
    conn.commit()
    conn.close()


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_all_styles() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM styles")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

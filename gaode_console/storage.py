from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

from gaode_console.data import load_data as load_seed_data


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data_store"
STATE_FILE = DATA_DIR / "app_state.json"
DB_FILE = DATA_DIR / "app_state.db"


def _serialize_value(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except TypeError:
            return str(value)
    return value


def _frame_to_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    records = frame.to_dict(orient="records")
    return [{key: _serialize_value(val) for key, val in row.items()} for row in records]


def _sqlite_type(dtype: Any) -> str:
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    if pd.api.types.is_float_dtype(dtype):
        return "REAL"
    return "TEXT"


def _table_schema(frame: pd.DataFrame) -> dict[str, str]:
    return {column: _sqlite_type(dtype) for column, dtype in frame.dtypes.items()}


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def _create_table(conn: sqlite3.Connection, table_name: str, schema: dict[str, str]) -> None:
    columns = ", ".join(f'"{name}" {sql_type}' for name, sql_type in schema.items())
    conn.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns})')


def _existing_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    rows = conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
    return {row["name"] for row in rows}


def _insert_frame(conn: sqlite3.Connection, table_name: str, frame: pd.DataFrame) -> None:
    if frame.empty:
        return
    records = _frame_to_records(frame)
    columns = list(records[0].keys())
    placeholders = ", ".join(["?"] * len(columns))
    column_sql = ", ".join(f'"{column}"' for column in columns)
    values = [[row.get(column) for column in columns] for row in records]
    conn.executemany(f'INSERT INTO "{table_name}" ({column_sql}) VALUES ({placeholders})', values)


def _migrate_json_payload() -> dict[str, pd.DataFrame]:
    if not STATE_FILE.exists():
        return load_seed_data()
    payload = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {name: pd.DataFrame(records) for name, records in payload.items()}


def ensure_database() -> None:
    seed = load_seed_data()
    with _connect() as conn:
        if not DB_FILE.exists() or conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchone() is None:
            initial = _migrate_json_payload()
            for table_name, seed_frame in seed.items():
                frame = initial.get(table_name, seed_frame.copy())
                schema = _table_schema(seed_frame)
                _create_table(conn, table_name, schema)
                _insert_frame(conn, table_name, frame)
            conn.commit()
            return

        for table_name, seed_frame in seed.items():
            schema = _table_schema(seed_frame)
            _create_table(conn, table_name, schema)
            existing = _existing_columns(conn, table_name)
            for column, sql_type in schema.items():
                if column not in existing:
                    conn.execute(f'ALTER TABLE "{table_name}" ADD COLUMN "{column}" {sql_type}')
            count = conn.execute(f'SELECT COUNT(*) AS count FROM "{table_name}"').fetchone()["count"]
            if count == 0:
                _insert_frame(conn, table_name, seed_frame)
        conn.commit()


def _coerce_frame_types(frame: pd.DataFrame, seed_frame: pd.DataFrame) -> pd.DataFrame:
    for column, dtype in seed_frame.dtypes.items():
        if column not in frame.columns:
            continue
        if pd.api.types.is_integer_dtype(dtype):
            frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0).astype(int)
        elif pd.api.types.is_float_dtype(dtype):
            frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0.0).astype(float)
        else:
            frame[column] = frame[column].astype(str)
    return frame


def load_data() -> dict[str, pd.DataFrame]:
    ensure_database()
    seed = load_seed_data()
    data: dict[str, pd.DataFrame] = {}
    with _connect() as conn:
        for table_name, seed_frame in seed.items():
            frame = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
            data[table_name] = _coerce_frame_types(frame, seed_frame)
    return data


def update_record(dataset: str, id_field: str, id_value: str, updates: dict[str, Any]) -> None:
    ensure_database()
    assignments = ", ".join(f'"{key}" = ?' for key in updates.keys())
    values = [_serialize_value(value) for value in updates.values()]
    values.append(id_value)
    with _connect() as conn:
        conn.execute(f'UPDATE "{dataset}" SET {assignments} WHERE "{id_field}" = ?', values)
        conn.commit()


def append_record(dataset: str, record: dict[str, Any]) -> None:
    ensure_database()
    serialized = {key: _serialize_value(value) for key, value in record.items()}
    columns = list(serialized.keys())
    placeholders = ", ".join(["?"] * len(columns))
    column_sql = ", ".join(f'"{column}"' for column in columns)
    values = [serialized[column] for column in columns]
    with _connect() as conn:
        conn.execute(f'INSERT INTO "{dataset}" ({column_sql}) VALUES ({placeholders})', values)
        conn.commit()


def append_operation_log(actor: str, target_type: str, target: str, action: str, detail: str, time_str: str) -> None:
    data = load_data()
    next_id = f"LG-{600 + len(data['operation_logs']) + 1}"
    append_record(
        "operation_logs",
        {
            "log_id": next_id,
            "time": time_str,
            "actor": actor,
            "target_type": target_type,
            "target": target,
            "action": action,
            "detail": detail,
        },
    )

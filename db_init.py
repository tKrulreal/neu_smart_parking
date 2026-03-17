from sqlalchemy import create_engine, text

DB_URL = "sqlite:///parking.db"


def ensure_plate_scan_log_status_column(conn) -> None:
    columns = conn.execute(text("PRAGMA table_info(plate_scan_log)")).fetchall()
    names = {row[1] for row in columns}
    if "decision_status" not in names:
        conn.execute(
            text(
                """
                ALTER TABLE plate_scan_log
                ADD COLUMN decision_status TEXT NOT NULL DEFAULT 'DENY'
                """
            )
        )


def init_db() -> None:
    engine = create_engine(DB_URL)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS vehicle (
                    plate TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL
                )
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS parking_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plate TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    time_in TEXT NOT NULL,
                    time_out TEXT,
                    gate_in TEXT,
                    gate_out TEXT
                )
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS plate_scan_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plate TEXT NOT NULL,
                    raw_text TEXT,
                    score REAL,
                    image_path TEXT,
                    gate TEXT,
                    direction TEXT,
                    decision_status TEXT NOT NULL DEFAULT 'DENY',
                    created_at TEXT NOT NULL
                )
                """
            )
        )
        ensure_plate_scan_log_status_column(conn)
        conn.execute(
            text(
                """
                INSERT OR IGNORE INTO vehicle(plate, student_id)
                VALUES (:plate, :student_id)
                """
            ),
            [
                {"plate": "29G188888", "student_id": "20211234"},
                {"plate": "30A12345", "student_id": "20205678"},
            ],
        )
    print("DB ready: parking.db")


if __name__ == "__main__":
    init_db()

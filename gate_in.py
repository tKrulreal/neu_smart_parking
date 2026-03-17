import argparse
import datetime as dt

from sqlalchemy import create_engine, text

from generate_qr import create_qr_for_student
from plate_read_demo import detect_plate_text

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


def log_plate_scan(
    conn,
    plate: str,
    raw: str,
    score: float,
    image_path: str,
    gate_name: str,
    decision_status: str,
):
    conn.execute(
        text(
            """
            INSERT INTO plate_scan_log
            (plate, raw_text, score, image_path, gate, direction, decision_status, created_at)
            VALUES (:plate, :raw_text, :score, :image_path, :gate, :direction, :decision_status, :created_at)
            """
        ),
        {
            "plate": plate,
            "raw_text": raw,
            "score": score,
            "image_path": image_path,
            "gate": gate_name,
            "direction": "IN",
            "decision_status": decision_status,
            "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        },
    )


def vehicle_enter_from_image(image_path: str, gate_name: str = "gate2") -> bool:
    result = detect_plate_text(image_path)
    plate, raw, score = result[:3]
    engine = create_engine(DB_URL)
    with engine.begin() as conn:
        ensure_plate_scan_log_status_column(conn)

        if not plate:
            log_plate_scan(
                conn,
                plate="UNKNOWN",
                raw=raw,
                score=score,
                image_path=image_path,
                gate_name=gate_name,
                decision_status="DENY",
            )
            print("DENY - CANNOT_READ_PLATE")
            return False

        owner = conn.execute(
            text("SELECT student_id FROM vehicle WHERE plate=:plate"),
            {"plate": plate},
        ).fetchone()
        if not owner:
            log_plate_scan(conn, plate, raw, score, image_path, gate_name, "DENY")
            print(f"DENY - UNKNOWN_VEHICLE ({plate})")
            return False

        active = conn.execute(
            text(
                """
                SELECT id FROM parking_log
                WHERE plate=:plate AND time_out IS NULL
                ORDER BY id DESC LIMIT 1
                """
            ),
            {"plate": plate},
        ).fetchone()
        if active:
            log_plate_scan(conn, plate, raw, score, image_path, gate_name, "DENY")
            print(f"DENY - ALREADY_INSIDE ({plate})")
            return False

        conn.execute(
            text(
                """
                INSERT INTO parking_log (plate, student_id, time_in, gate_in)
                VALUES (:plate, :student_id, :time_in, :gate_in)
                """
            ),
            {
                "plate": plate,
                "student_id": owner[0],
                "time_in": dt.datetime.now().isoformat(timespec="seconds"),
                "gate_in": gate_name,
            },
        )
        log_plate_scan(conn, plate, raw, score, image_path, gate_name, "OPEN")

    student_id = owner[0]
    try:
        qr_path = create_qr_for_student(student_id)
        print(f"QR GENERATED - student={student_id} path={qr_path}")
    except Exception as exc:
        print(f"WARN - QR_GENERATE_FAILED student={student_id} err={exc}")

    print(f"OPEN BARRIER IN - plate={plate} raw={raw} score={score:.3f} student={student_id}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Cong vao: quet bien so tu anh")
    parser.add_argument("--image", required=True, help="Anh bien so xe vao")
    parser.add_argument("--gate", default="gate2", help="Ten cong vao")
    args = parser.parse_args()
    vehicle_enter_from_image(args.image, args.gate)


if __name__ == "__main__":
    main()

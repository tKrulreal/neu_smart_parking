import argparse
import datetime as dt

from sqlalchemy import create_engine, text

from iot_serial import send_iot_command
from plate_read_demo import detect_plate_text
from qr_camera_scan import scan_qr_from_camera
from qr_reader import read_qr_from_image

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
            "direction": "OUT",
            "decision_status": decision_status,
            "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        },
    )


def vehicle_exit(
    plate_image_path: str,
    gate_name: str = "gate1",
    use_camera_qr: bool = True,
    qr_image_path: str | None = None,
    camera_index: int = 0,
    qr_timeout_sec: int = 20,
    qr_max_age_minutes: int = 5,
) -> bool:
    result = detect_plate_text(plate_image_path)
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
                image_path=plate_image_path,
                gate_name=gate_name,
                decision_status="DENY",
            )
            send_iot_command("DENY")
            print("DENY - CANNOT_READ_PLATE")
            return False

        if use_camera_qr:
            qr_student_id, payload, valid_qr = scan_qr_from_camera(
                camera_index=camera_index,
                timeout_sec=qr_timeout_sec,
                qr_max_age_minutes=qr_max_age_minutes,
            )
        else:
            if not qr_image_path:
                log_plate_scan(
                    conn, plate, raw, score, plate_image_path, gate_name, "DENY"
                )
                send_iot_command("DENY")
                print("DENY - QR_IMAGE_REQUIRED")
                return False
            qr_student_id, payload, valid_qr = read_qr_from_image(
                qr_image_path, qr_max_age_minutes=qr_max_age_minutes
            )

        if not qr_student_id:
            log_plate_scan(conn, plate, raw, score, plate_image_path, gate_name, "DENY")
            send_iot_command("DENY")
            print("DENY - CANNOT_READ_QR")
            return False
        if not valid_qr:
            log_plate_scan(conn, plate, raw, score, plate_image_path, gate_name, "DENY")
            send_iot_command("DENY")
            print(f"DENY - EXPIRED_OR_INVALID_QR ({payload})")
            return False

        owner = conn.execute(
            text("SELECT student_id FROM vehicle WHERE plate=:plate"),
            {"plate": plate},
        ).fetchone()
        if not owner:
            log_plate_scan(conn, plate, raw, score, plate_image_path, gate_name, "DENY")
            send_iot_command("DENY")
            print(f"DENY - UNKNOWN_VEHICLE ({plate})")
            return False

        if owner[0] != qr_student_id:
            log_plate_scan(conn, plate, raw, score, plate_image_path, gate_name, "DENY")
            send_iot_command("DENY")
            print(
                f"DENY - STUDENT_MISMATCH plate={plate} owner={owner[0]} qr={qr_student_id}"
            )
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
        if not active:
            log_plate_scan(conn, plate, raw, score, plate_image_path, gate_name, "DENY")
            send_iot_command("DENY")
            print(f"DENY - NO_ACTIVE_SESSION ({plate})")
            return False

        conn.execute(
            text(
                """
                UPDATE parking_log
                SET time_out=:time_out, gate_out=:gate_out
                WHERE id=:id
                """
            ),
            {
                "time_out": dt.datetime.now().isoformat(timespec="seconds"),
                "gate_out": gate_name,
                "id": active[0],
            },
        )
        log_plate_scan(conn, plate, raw, score, plate_image_path, gate_name, "OPEN")
        send_iot_command("OPEN_OUT")

    print(
        f"OPEN BARRIER OUT - plate={plate} raw={raw} score={score:.3f} "
        f"student={qr_student_id}"
    )
    return True


def main():
    parser = argparse.ArgumentParser(description="Cong ra: bien so + QR")
    parser.add_argument("--plate-image", required=True, help="Anh bien so xe ra")
    parser.add_argument("--gate", default="gate1", help="Ten cong ra")
    parser.add_argument(
        "--qr-mode",
        choices=["camera", "image"],
        default="camera",
        help="Che do quet QR",
    )
    parser.add_argument("--qr-image", default=None, help="Anh QR neu dung mode=image")
    parser.add_argument("--camera", type=int, default=0, help="Camera index")
    parser.add_argument("--timeout", type=int, default=20, help="Thoi gian quet QR")
    parser.add_argument(
        "--qr-max-age-minutes",
        type=int,
        default=5,
        help="So phut QR con hieu luc",
    )
    args = parser.parse_args()

    vehicle_exit(
        plate_image_path=args.plate_image,
        gate_name=args.gate,
        use_camera_qr=(args.qr_mode == "camera"),
        qr_image_path=args.qr_image,
        camera_index=args.camera,
        qr_timeout_sec=args.timeout,
        qr_max_age_minutes=args.qr_max_age_minutes,
    )


if __name__ == "__main__":
    main()

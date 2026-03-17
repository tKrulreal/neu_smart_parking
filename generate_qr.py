import argparse
import datetime as dt
from pathlib import Path

import qrcode


def create_qr_for_student(student_id: str, output_dir: str = "qr_out") -> str:
    created_at = dt.datetime.now().isoformat(timespec="seconds")
    payload = f"{student_id}|{created_at}"

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_ts = created_at.replace(":", "-")
    file_path = out_dir / f"{student_id}_{safe_ts}.png"

    img = qrcode.make(payload)
    img.save(file_path)
    return str(file_path)


def main():
    parser = argparse.ArgumentParser(description="Tao QR theo student_id|timestamp")
    parser.add_argument("--student-id", required=True, help="Ma sinh vien")
    parser.add_argument("--output-dir", default="qr_out", help="Thu muc luu QR")
    args = parser.parse_args()

    qr_path = create_qr_for_student(args.student_id, args.output_dir)
    print("QR created:", qr_path)


if __name__ == "__main__":
    main()

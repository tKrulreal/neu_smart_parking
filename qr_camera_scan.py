import argparse
import time

import cv2
from pyzbar.pyzbar import decode

from qr_reader import is_qr_valid_time, parse_qr_payload


def scan_qr_from_camera(
    camera_index: int = 0,
    timeout_sec: int = 20,
    mirror: bool = True,
    show_guide: bool = True,
    qr_max_age_minutes: int = 5,
):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Khong mo duoc camera index={camera_index}")


    start = time.time()
    payload = None

    try:
        while time.time() - start < timeout_sec:
            ok, frame = cap.read()
            if not ok:
                continue

            if mirror:
                frame = cv2.flip(frame, 1)

            h, w = frame.shape[:2]
            box_size = int(min(w, h) * 0.55)
            x1 = (w - box_size) // 2
            y1 = (h - box_size) // 2
            x2 = x1 + box_size
            y2 = y1 + box_size

            roi = frame[y1:y2, x1:x2]
            codes = decode(roi) if show_guide else []
            if not codes:
                codes = decode(frame)
            if codes:
                payload = codes[0].data.decode("utf-8").strip()
                break

            if show_guide:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                cv2.putText(
                    frame,
                    "Dat ma QR vao khung vang",
                    (10, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2,
                )
            cv2.putText(
                frame,
                "Dang quet QR... (nhan q de huy)",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )
            cv2.imshow("QR Scanner", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

    if not payload:
        return None, None, False
    student_id, created_at_str = parse_qr_payload(payload)
    valid_qr = is_qr_valid_time(created_at_str, max_age_minutes=qr_max_age_minutes)
    return student_id, payload, valid_qr


def main():
    parser = argparse.ArgumentParser(description="Quet QR tu camera")
    parser.add_argument("--camera", type=int, default=0, help="Camera index")
    parser.add_argument("--timeout", type=int, default=20, help="Thoi gian quet (giay)")
    parser.add_argument(
        "--qr-max-age-minutes",
        type=int,
        default=5,
        help="So phut QR con hieu luc",
    )
    parser.add_argument(
        "--no-mirror",
        action="store_true",
        help="Tat lat camera kieu guong",
    )
    parser.add_argument(
        "--no-guide",
        action="store_true",
        help="Tat khung huong dan dat QR",
    )
    args = parser.parse_args()

    student_id, payload, valid_today = scan_qr_from_camera(
        camera_index=args.camera,
        timeout_sec=args.timeout,
        mirror=not args.no_mirror,
        show_guide=not args.no_guide,
        qr_max_age_minutes=args.qr_max_age_minutes,
    )
    if not payload:
        print("Khong quet duoc QR")
        return
    print("QR DATA:", payload)
    print("STUDENT:", student_id)
    print("VALID TODAY:", valid_today)


if __name__ == "__main__":
    main()

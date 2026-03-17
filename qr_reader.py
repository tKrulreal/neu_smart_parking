import datetime as dt

import cv2
from pyzbar.pyzbar import decode


def parse_qr_payload(payload: str):
    if not payload or "|" not in payload:
        return None, None
    student_id, created_at_str = payload.split("|", 1)
    return student_id.strip(), created_at_str.strip()


def is_qr_valid_time(created_at_str: str, max_age_minutes: int = 5) -> bool:
    if not created_at_str:
        return False
    try:
        qr_created_at = dt.datetime.fromisoformat(created_at_str)
    except ValueError:
        return False
    now = dt.datetime.now()
    age = now - qr_created_at
    if age.total_seconds() < 0:
        return False
    return age <= dt.timedelta(minutes=max_age_minutes)


def read_qr_from_image(image_path: str, qr_max_age_minutes: int = 5):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Khong doc duoc anh QR: {image_path}")
    codes = decode(img)
    if not codes:
        return None, None, False
    payload = codes[0].data.decode("utf-8").strip()
    student_id, created_at_str = parse_qr_payload(payload)
    valid_qr = is_qr_valid_time(created_at_str, max_age_minutes=qr_max_age_minutes)
    return student_id, payload, valid_qr

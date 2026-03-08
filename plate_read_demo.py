import cv2
import easyocr
from ultralytics import YOLO

MODEL_PATH = "models/license_plate_detector.pt"
IMAGE_PATH = "samples/test.webp"   # bạn tự cho 1 ảnh xe vào đây

reader = easyocr.Reader(['en'])  # biển số chủ yếu chữ + số
model = YOLO(MODEL_PATH)

img = cv2.imread(IMAGE_PATH)
if img is None:
    raise FileNotFoundError("Không đọc được ảnh. Kiểm tra IMAGE_PATH.")

results = model(img)[0]

# Lấy bbox biển số có confidence cao nhất
best = None
for box in results.boxes:
    conf = float(box.conf[0])
    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
    if best is None or conf > best["conf"]:
        best = {"conf": conf, "xyxy": (x1, y1, x2, y2)}

if best is None:
    print("Không phát hiện được biển số.")
    exit()

x1, y1, x2, y2 = best["xyxy"]
plate = img[y1:y2, x1:x2]

# Tiền xử lý nhẹ cho OCR
gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
_, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

ocr = reader.readtext(th)
text = " ".join([t[1] for t in ocr]).strip()

print("CONF:", best["conf"])
print("PLATE OCR:", text)

cv2.imshow("plate", plate)
cv2.imshow("th", th)
cv2.waitKey(0)
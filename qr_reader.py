import cv2
from pyzbar.pyzbar import decode

img = cv2.imread("student_qr.png")

codes = decode(img)

for code in codes:
    data = code.data.decode("utf-8")
    print("QR DATA:", data)
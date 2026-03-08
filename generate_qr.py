import qrcode
import datetime

student_id = "20211234"

today = datetime.date.today().isoformat()

data = f"{student_id}|{today}"

img = qrcode.make(data)

img.save("student_qr.png")

print("QR created:", data)
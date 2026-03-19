import serial
import time

SERIAL_PORT = "COM3"   # đổi theo máy bạn
BAUD_RATE = 9600

_ser = None

def get_serial():
    global _ser
    if _ser is None:
        _ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
    return _ser

def send_iot_command(cmd: str):
    ser = get_serial()
    ser.write((cmd + "\n").encode("utf-8"))
    print(f"[IOT] Sent: {cmd}")
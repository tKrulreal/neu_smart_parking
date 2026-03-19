from iot_serial import send_iot_command
import time

send_iot_command("OPEN_IN")
time.sleep(5)
send_iot_command("DENY")
time.sleep(3)
send_iot_command("OPEN_OUT")
import serial
import time

try:
    esp32 = serial.Serial(
        port="COM10",
        baudrate=115200,
        timeout=1
    )

    time.sleep(2)

    print("ESP32 conectada na COM10!")

except serial.SerialException as e:
    print("Erro ao conectar:", e)
import serial
import serial.tools.list_ports

def find_esp32_port():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if "USB" in p.description or "Silicon Labs" in p.description or "CH340" in p.description:
            return p.device
    raise Exception("ESP32 port not found")

esp32_port = find_esp32_port()
print("Using port:", esp32_port)

ser = serial.Serial(esp32_port, 115200)

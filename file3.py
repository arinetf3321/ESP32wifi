import serial
import serial.tools.list_ports

# List all available COM ports
ports = serial.tools.list_ports.comports()
for p in ports:
    print(p.device, p.description)

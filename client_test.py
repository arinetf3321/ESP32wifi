import socket

HOST = "192.168.4.1"
PORT = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)

try:
    s.connect((HOST, PORT))
    print("Connected!")
except Exception as e:
    print("Connection failed:", e)

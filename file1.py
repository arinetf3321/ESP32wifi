from flask import Flask, render_template
import socket, threading

app = Flask(__name__)

# Replace with your ESP32's IP from Serial Monitor
ESP32_HOST = "192.168.0.111"  # example, adjust to your ESP32 IP
ESP32_PORT = 5000

latest_output = ""

def read_socket():
    global latest_output
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ESP32_HOST, ESP32_PORT))
    while True:
        data = s.recv(1024)
        if not data:
            break
        latest_output = data.decode("utf-8").strip()

# Run socket reading in background thread
threading.Thread(target=read_socket, daemon=True).start()

@app.route("/")
def index():
    return render_template("index.html", output=latest_output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)  # Flask runs on 8080, ESP32 still on 5000
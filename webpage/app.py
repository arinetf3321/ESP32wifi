from flask import Flask, render_template, jsonify
import socket
import threading
import time

app = Flask(__name__)

# ESP32 connection
ESP32_HOST = "192.168.17.150"
ESP32_PORT = 5000

# Shared data
latest_od = 0.0
latest_pwm = 0
latest_raw = ""
data_lock = threading.Lock()

# Track last HTTP responses
status_history = []

@app.route("/")
def index():
    with data_lock:
        od_value = latest_od
        pwm_value = latest_pwm
        raw_value = latest_raw
    return render_template("index.html", od=od_value, pwm=pwm_value, raw=raw_value)

# JSON endpoint for sensor data
@app.route("/sensor-data")
def sensor_data():
    with data_lock:
        return jsonify({
            "od": latest_od,
            "pwm": latest_pwm,
            "raw": latest_raw
        })

# JSON endpoint for HTTP status log
@app.route("/status-log")
def status_log():
    return jsonify(status_history[-10:])  # last 10 responses

# Track all HTTP responses
@app.after_request
def track_status_code(response):
    status_history.append(response.status_code)
    if len(status_history) > 50:  # keep last 50 responses
        status_history.pop(0)
    return response

# TCP listener for ESP32
def tcp_listener():
    global latest_od, latest_pwm, latest_raw
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((ESP32_HOST, ESP32_PORT))
                while True:
                    data = client_socket.recv(1024).decode().strip()
                    if not data:
                        continue
                    with data_lock:
                        latest_raw = data
                    if data.startswith("OD:") and ",PWM:" in data:
                        od_value = float(data.split(",")[0].split(":")[1])
                        pwm_value = int(data.split(",")[1].split(":")[1])
                        with data_lock:
                            latest_od = od_value
                            latest_pwm = pwm_value
        except Exception as e:
            print("ESP32 connection failed or lost:", e)
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=tcp_listener, daemon=True).start()
    app.run(host="0.0.0.0", port=8080, debug=True)
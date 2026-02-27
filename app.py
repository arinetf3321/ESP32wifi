from flask import Flask, render_template_string
import socket
import threading

app = Flask(__name__)

# ESP32 connection details
ESP32_IP = "192.168.0.120"  # Change to your ESP32 IP
ESP32_PORT = 5000

# Shared variables for sensor data and lock for thread-safety
latest_od = 0.0
latest_pwm = 0
latest_raw = ""   # <-- store raw ESP32 output
data_lock = threading.Lock()

# HTML template
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Brain oxygen flow detector data</title>
    <meta http-equiv="refresh" content="2"> <!-- auto-refresh every 2s -->
</head>
<body>
    <h1>Brain oxygen flow detector data</h1>
    <p><strong>Brain oxygen flow detector Output:</strong> {{ raw }}</p>
    <p><strong>Volts (V):</strong> {{ od }}</p>
    <p><strong>PWM Duty Cycle:</strong> {{ pwm }}</p>
</body>
</html>
"""

@app.route("/")
def index():
    with data_lock:
        od_value = latest_od
        pwm_value = latest_pwm
        raw_value = latest_raw
    return render_template_string(html_template, od=od_value, pwm=pwm_value)

# --- TCP listener function ---
def tcp_listener():
    global latest_od, latest_pwm, latest_raw
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ESP32_IP, ESP32_PORT))
    while True:
        data = client_socket.recv(1024).decode().strip()
        if not data:
            continue

        # Print raw ESP32 output to console 
        print("Raw ESP32 output:", data)
        
        # Save raw output for display
        with data_lock:
            latest_raw = data

        if not data.startswith("OD:") or ",PWM:" not in data:
            print("Skipping malformed line:", data)
            continue
        try:
            od_value = float(data.split(",")[0].split(":")[1])
            pwm_value = int(data.split(",")[1].split(":")[1])
            with data_lock:
                latest_od = od_value
                latest_pwm = pwm_value
            # Print parsed values to console 
            print(f"Parsed values -> OD: {latest_od}, PWM: {latest_pwm}")   
                
        except Exception as e:
            print("Parse error:", e, "Line:", data)

# --- Main entry point ---
if __name__ == "__main__":
    threading.Thread(target=tcp_listener, daemon=True).start()
    app.run(host="192.168.0.110", port=8080, debug=True)

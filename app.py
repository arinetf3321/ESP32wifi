from flask import Flask, render_template_string
import socket
import threading

app = Flask(__name__)

# ESP32 connection details
ESP32_IP = "192.168.0.121"  # Change to your ESP32 IP
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
    buffer = ""

    while True:
        # Append new data to buffer
        buffer += client_socket.recv(1024).decode()

        # Process complete lines
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if not line:
                continue

            # Print raw ESP32 output
            print("Raw ESP32 output:", line)

            # Save raw output for display
            with data_lock:
                latest_raw = line

            # Validate format
            if not (line.startswith("Volts:") and ",PWM:" in line):
                print("Skipping malformed line:", line)
                continue

            try:
                # Parse clean values
                od_value = float(line.split(",")[0].split(":")[1])
                pwm_value = int(line.split(",")[1].split(":")[1])

                # Update shared variables
                with data_lock:
                    latest_od = od_value
                    latest_pwm = pwm_value

                print(f"Parsed values -> OD: {latest_od}, PWM: {latest_pwm}")
            except Exception as e:
                print("Parse error:", e, "Line:", line)

# --- Main entry point ---
if __name__ == "__main__":
    threading.Thread(target=tcp_listener, daemon=True).start()
    app.run(host="0.0.0.0", port=8080, debug=True)

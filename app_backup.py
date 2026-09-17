from flask import Flask, render_template, jsonify
import socket
import threading
import time
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

app = Flask(__name__)

# Shared data
latest_od = 0.0
latest_pwm = 0
latest_raw = ""
data_lock = threading.Lock()

# TCP server port for ESP32 to connect
TCP_PORT = 5001

# Track last HTTP responses
status_history = []

# When saving the graph
# Absolute path to your static folder
STATIC_FOLDER = r"C:\Users\strainee\Documents\platformIO\Projects\ESP32\static"
if not os.path.exists(STATIC_FOLDER):
  os.makedirs(STATIC_FOLDER)
          
#Placeholder graph to ensure the image exists at startup
placeholder_path = os.path.join(STATIC_FOLDER, 'graph.png')
if not os.path.exists(placeholder_path):
  plt.figure(figsize=(10,5))
  plt.plot([0,1],[50,50],'r-')
  plt.title("Cerebral Oxygenation Over Time")
  plt.xlabel("Time (s)")
  plt.ylabel("SpO₂ (%)")
  plt.savefig(placeholder_path, bbox_inches='tight')
  plt.close()
  # -----------------------------
  
@app.route("/")
def index():
    with data_lock:
        od_value = latest_od
        pwm_value = latest_pwm
        raw_value = latest_raw
    return render_template("index.html", od=od_value, pwm=pwm_value, raw=raw_value, time=time)

# JSON endpoint for sensor data
@app.route("/sensor-data")
def sensor_data():
    with data_lock:

        #print(f"[Sensor Data Requested] od={latest_od}, pwm={latest_pwm}, raw='{latest_raw}'", flush=True)
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
    if len(status_history) > 50:
        status_history.pop(0)
    return response

# TCP server for ESP32
def tcp_server():
    global latest_od, latest_pwm, latest_raw
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # <<< ADD THIS
    server_socket.bind(('0.0.0.0', TCP_PORT))
    server_socket.listen(1)
    print(f"TCP server listening on port {TCP_PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"ESP32 connected from {addr}")
        threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()
        
def handle_client(client_socket):
    global latest_od, latest_pwm, latest_raw
    with client_socket:
        while True:
            try:
                data = client_socket.recv(1024).decode().strip()
                if not data:
                    continue
                print("[TCP Received]:", data, flush=True)

                # Update raw
                with data_lock:
                    #latest_raw = data.splitlines()[-1].strip()
                    #latest_raw = data.splitlines()[-1].replace("RAW:", "").strip()
                    latest_raw = data.splitlines()[-1].replace("RAW:", "").replace(",", "").strip()

                # Extract OD
                od_value = None
                pwm_value = None
                if "OD:" in data:
                    try:
                        od_value = float(data.split("OD:")[1].split(",")[0].strip())
                    except: pass
                elif "Volts:" in data:
                    try:
                        od_value = float(data.split("Volts:")[1].split(",")[0].strip())
                    except: pass

                if "PWM:" in data:
                    try:
                        pwm_value = int(data.split("PWM:")[1].split(",")[0].strip())
                    except: pass

                # Update globals
                with data_lock:
                    if od_value is not None:
                        latest_od = od_value
                    if pwm_value is not None:
                        latest_pwm = pwm_value
                    print(f"[TCP Updated] od={latest_od}, pwm={latest_pwm}, raw='{latest_raw}'", flush=True)

            except Exception as e:
                print("[TCP Connection Error]:", e, flush=True)
                break
                
                
def satugraph():
    matplotlib.use("Agg")  # Non-GUI backend
    time_data = []
    spo2_data = []
    raw_data = []
    od_data = []
    start_time = time.time()

    # Create a single figure
    fig, ax = plt.subplots(figsize=(12, 6))

    # Lines
    line_spo2, = ax.plot([], [], 'r-', label="O₂ Saturation (%)")
    line_raw, = ax.plot([], [], 'g-', label=" Photodiode Sensor")
    line_od, = ax.plot([], [], 'b-', label="Volts")

    # Axis labels and title
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Values")
    ax.set_title("Output Over Time")
    ax.grid(True)
    ax.legend(loc='upper right', bbox_to_anchor=(1, 0.6))

    # Optional: draw a reference line for SpO₂ ~100%
    ax.axhline(95, color='blue', linestyle='--', linewidth=1, label="100% reference")

    def od_to_spo2(od):
        # placeholder conversion
        return max(90, min(100, 100 - (od - 0.1) * 98))

    while True:
        with data_lock:
            od_value = latest_od
            raw_value = latest_raw

        # Convert raw to float safely
        try:
            raw_value_float = float(raw_value)
        except:
            raw_value_float = 0.0

        current_time = time.time() - start_time
        spo2 = od_to_spo2(od_value)

        # Append new data
        time_data.append(current_time)
        spo2_data.append(spo2)
        raw_data.append(raw_value_float)
        od_data.append(od_value)

        # Keep only last 200 points
        time_data = time_data[-200:]
        spo2_data = spo2_data[-200:]
        raw_data = raw_data[-200:]
        od_data = od_data[-200:]

        # Update lines
        line_spo2.set_xdata(time_data)
        line_spo2.set_ydata(spo2_data)
        line_raw.set_xdata(time_data)
        line_raw.set_ydata(raw_data)
        line_od.set_xdata(time_data)
        line_od.set_ydata(od_data)

        # Update X-axis limits
        ax.set_xlim(max(0, current_time - 20), current_time + 1)

        # Update Y-axis automatically to fit all data
        all_data = spo2_data + raw_data + od_data
        ax.set_ylim(min(all_data) - 5, max(all_data) + 5)

        # Save figure
        plt.tight_layout()
        plt.savefig(os.path.join(STATIC_FOLDER, 'graph.png'), bbox_inches='tight')
        plt.pause(0.05)

if __name__ == "__main__":
    # Start TCP server thread
    threading.Thread(target=tcp_server, daemon=True).start()  
    # Start plotting thread
    threading.Thread(target=satugraph, daemon=True).start()
    # Run Flask in threaded mode
    app.run(host="0.0.0.0", port=8080, debug=False, threaded=True)
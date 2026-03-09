import socket
import matplotlib.pyplot as plt
from collections import deque
import time

# === ESP32 TCP Settings ===
ESP32_IP = "192.168.0.121"  # Replace with your ESP32 IP
ESP32_PORT = 5000

# === Connect to ESP32 TCP server ===
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ESP32_IP, ESP32_PORT))
client_socket.settimeout(2)

# === Data storage ===
time_data = []
spo2_data = []

# Sliding window for AC/DC calculation
window_size = 50  # number of samples per window (~10 seconds depending on sampling)
nir_window = deque(maxlen=window_size)
red_window = deque(maxlen=window_size)

start_time = time.time()

# === Set up live plot ===
plt.ion()
fig, ax = plt.subplots(figsize=(10,5))
line, = ax.plot(time_data, spo2_data, 'r-', label="SpO₂ (%)")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Oxygen Saturation (%)")
ax.set_title("Cerebral Oxygenation (SpO₂) Over Time")
ax.set_ylim(50, 100)  # typical neonatal cerebral oxygenation range
ax.grid(True)
ax.legend(loc='upper right')

# === Function to calculate SpO2 from OD_NIR and OD_Red ===
def calculate_spo2(nir_window, red_window):
    # DC = average over window
    DC_NIR = sum(nir_window) / len(nir_window)
    DC_Red = sum(red_window) / len(red_window)
    # AC = peak-to-peak in window
    AC_NIR = max(nir_window) - min(nir_window)
    AC_Red = max(red_window) - min(red_window)
    
    # Avoid division by zero
    if AC_NIR == 0 or DC_NIR == 0 or DC_Red == 0:
        return 0

    R = (AC_Red / DC_Red) / (AC_NIR / DC_NIR)
    spo2 = 110 - 25 * R  # empirical formula
    spo2 = max(0, min(100, spo2))
    return spo2

# === Main loop: read ESP32 and update plot ===
try:
    while True:
        data = client_socket.recv(1024).decode().strip()
        if data:
            lines = data.split('\n')
            for line_data in lines:
                if "OD_NIR" in line_data and "OD_Red" in line_data:
                    try:
                        parts = line_data.split(',')
                        OD_NIR = float(parts[0].split(':')[1])
                        OD_Red = float(parts[1].split(':')[1])

                        # Add to sliding window
                        nir_window.append(OD_NIR)
                        red_window.append(OD_Red)

                        # Calculate SpO2 only when window is full
                        if len(nir_window) == window_size:
                            spo2 = calculate_spo2(nir_window, red_window)
                            current_time = time.time() - start_time
                            time_data.append(current_time)
                            spo2_data.append(spo2)

                            # Update plot
                            line.set_xdata(time_data)
                            line.set_ydata(spo2_data)
                            ax.relim()
                            ax.autoscale_view()
                            plt.pause(0.05)
                    except Exception as e:
                        print("Parsing error:", e)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    client_socket.close()
    plt.ioff()
    plt.show()
import socket
import matplotlib.pyplot as plt
import time

# === ESP32 TCP Settings ===
ESP32_IP = "192.168.0.121"  # Replace with your ESP32 IP
ESP32_PORT = 5000

# === Connect to ESP32 TCP server ===
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ESP32_IP, ESP32_PORT))
client_socket.settimeout(2)  # Optional timeout

# === Lists to store data ===
time_data = []
spo2_data = []

start_time = time.time()

# === Set up plot ===
plt.ion()
fig, ax = plt.subplots(figsize=(10,5))
line, = ax.plot(time_data, spo2_data, 'r-', label="Oxygen Saturation (%)")
ax.set_xlabel("Time (s)")
ax.set_ylabel("SpO₂ (%)")
ax.set_title("Cerebral Oxygenation Over Time")
ax.set_ylim(50, 100)  # typical neonatal cerebral SpO2 range
ax.grid(True)
ax.legend(loc='upper right')

# === Function to map OD to SpO2 % ===
def od_to_spo2(od):
    # Simple linear mapping (adjust based on calibration)
    # Example: OD 0.1 -> 100%, OD 1.0 -> 50%
    spo2 = max(50, min(100, 100 - (od - 0.1) * 55))
    return spo2

# === Real-time reading and plotting loop ===
try:
    while True:
        data = client_socket.recv(1024).decode().strip()
        if data:
            lines = data.split('\n')
            for line_data in lines:
                if line_data.startswith("OD:"):
                    try:
                        # Extract OD value
                        od_value = float(line_data.split(',')[0].split(':')[1])
                        # Map to SpO2 %
                        spo2 = od_to_spo2(od_value)

                        # Append data
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
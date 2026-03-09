import socket
import matplotlib.pyplot as plt
import time

ESP32_IP = "192.168.0.121"
ESP32_PORT = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ESP32_IP, ESP32_PORT))
client_socket.settimeout(2)

time_data = []
spo2_data = []

start_time = time.time()

plt.ion()
fig, ax = plt.subplots()
line, = ax.plot(time_data, spo2_data, 'r-')
ax.set_xlabel("Time (s)")
ax.set_ylabel("SpO₂ (%)")
ax.set_title("Oxygen Saturation Over Time")

def calculate_spo2(OD_NIR, OD_Red):
    # Simple formula: R ratio -> SpO2
    try:
        AC_NIR = OD_NIR - 0.5  # approximate baseline DC ~0.5
        AC_Red = OD_Red - 0.5
        R = AC_Red / AC_NIR if AC_NIR != 0 else 0
        spo2 = 110 - 25 * R
        spo2 = max(0, min(100, spo2))  # clamp 0-100%
        return spo2
    except:
        return 0

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
                        spo2 = calculate_spo2(OD_NIR, OD_Red)
                        
                        current_time = time.time() - start_time
                        time_data.append(current_time)
                        spo2_data.append(spo2)
                        
                        line.set_xdata(time_data)
                        line.set_ydata(spo2_data)
                        ax.relim()
                        ax.autoscale_view()
                        plt.pause(0.05)
                    except Exception as e:
                        print("Error parsing line:", e)
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    client_socket.close()
    plt.ioff()
    plt.show()
import socket
import matplotlib.pyplot as plt
from collections import deque
import time

# === ESP32 TCP Settings ===
ESP32_IP = "192.168.0.121"  # replace with your ESP32 IP
ESP32_PORT = 5000

# Connect to ESP32 TCP server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ESP32_IP, ESP32_PORT))
client_socket.settimeout(2)

# Sliding window for plotting
window_size = 500          # number of points to display
adc_window = deque(maxlen=window_size)
time_window = deque(maxlen=window_size)

start_time = time.time()

# Set up live plot
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [], 'b-')
ax.set_xlabel("Time (s)")
ax.set_ylabel("ADC Reading")
ax.set_title("PWM Waveform via Photodiode")
ax.set_ylim(0, 4095)  # 12-bit ADC
ax.grid(True)

try:
    while True:
        # Receive data from ESP32
        data = client_socket.recv(1024).decode().strip()
        if data:
            lines = data.split('\n')
            for line_data in lines:
                try:
                    adc_value = int(line_data.strip())
                    adc_window.append(adc_value)
                    time_window.append(time.time() - start_time)

                    # Update plot
                    line.set_xdata(time_window)
                    line.set_ydata(adc_window)
                    ax.relim()
                    ax.autoscale_view()
                    plt.pause(0.01)  # tiny pause to update
                except:
                    continue

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    client_socket.close()
    plt.ioff()
    plt.show()
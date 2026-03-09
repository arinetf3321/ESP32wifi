import socket
import matplotlib.pyplot as plt
import time

# Replace with your ESP32 IP
ESP32_IP = "192.168.0.121"
ESP32_PORT = 5000

# Connect to ESP32 TCP server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ESP32_IP, ESP32_PORT))
client_socket.settimeout(2)  # optional, avoids blocking forever

# Lists to store data
time_data = []
od_data = []

start_time = time.time()

plt.ion()  # interactive mode
fig, ax = plt.subplots()
line, = ax.plot(time_data, od_data, 'b-')
ax.set_xlabel("Time (s)")
ax.set_ylabel("Photodiode Signal (OD)")
ax.set_title("Photodiode Signal vs Time")

try:
    while True:
        data = client_socket.recv(1024).decode().strip()
        if data:
            # Sometimes ESP32 sends multiple lines; split them
            lines = data.split('\n')
            for line_data in lines:
                if line_data.startswith("OD:"):
                    # Example: OD:0.1234,PWM:45
                    try:
                        parts = line_data.split(',')
                        od_value = float(parts[0].split(':')[1])
                        
                        # Append data
                        current_time = time.time() - start_time
                        time_data.append(current_time)
                        od_data.append(od_value)

                        # Update plot
                        line.set_xdata(time_data)
                        line.set_ydata(od_data)
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
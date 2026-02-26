import matplotlib.pyplot as plt
import socket

# Define ESP32 IP and Port
ESP32_IP = "192.168.0.100"  # Replace with your ESP32 IP address
ESP32_PORT = 5000  # The port number to match with the ESP32 Wi-Fi server

# Set up the client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ESP32_IP, ESP32_PORT))

# Initialize variables for data collection
time_data, od_data = [], []
time_counter = 0

# Set up Matplotlib for real-time plotting
plt.ion()  # Turn on interactive mode
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Initialize lines for oxygenation and deoxygenation
line1, = ax1.plot([], [], color='green', label='Oxygenation (HbO₂)')
line2, = ax2.plot([], [], color='red', label='Deoxygenation (Hb)')

# Set up graph titles and labels
ax1.set_title("Oxygenation (HbO₂) vs Time")
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Oxygenation (HbO₂)")
ax1.legend()

ax2.set_title("Deoxygenation (Hb) vs Time")
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Deoxygenation (Hb)")
ax2.legend()

try:
    while True:
        data = client_socket.recv(1024).decode().strip()  # Receive data from ESP32
        if data:
            try:
                # Extract OD and PWM values from received data
                od_value = float(data.split(",")[0].split(":")[1])
                pwm_value = int(data.split(",")[1].split(":")[1])

                # Update time and OD data for plotting
                time_data.append(time_counter)
                od_data.append(od_value)

                # Oxygenation and deoxygenation calculations
                oxygenation = 1 - od_value  # Inverse relationship for oxygenation
                deoxygenation = od_value  # Direct relationship for deoxygenation

                # Update graph data
                line1.set_xdata(time_data)
                line1.set_ydata([1 - i for i in od_data])  # Oxygenation
                line2.set_xdata(time_data)
                line2.set_ydata(deoxygenation)  # Deoxygenation

                # Rescale the axis to fit new data
                ax1.relim()
                ax1.autoscale_view()
                ax2.relim()
                ax2.autoscale_view()

                # Pause to update the graph in real time
                plt.pause(0.1)
                time_counter += 1

            except Exception as e:
                print(f"Error processing data: {e}")
        else:
            break

finally:
    client_socket.close()  # Close the socket when done

# Show the graph after the loop
plt.tight_layout()
plt.show()
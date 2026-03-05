import matplotlib.pyplot as plt
import socket
import time

# Replace with ESP32 IP address and port number
ESP32_IP = "192.168.0.121"
ESP32_PORT = 5000

# Create a socket connection to ESP32
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ESP32_IP, ESP32_PORT))

# Lists to store time, oxygenation, and deoxygenation data
time_data = []
oxygenation_data = []
deoxygenation_data = []

time_counter = 0  # Time counter to track data points

# Set up Matplotlib for dynamic plotting
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

# Plot settings for the graphs
ax1.set_title("Oxygenation vs. Time (Green Line)")
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Oxygenation (HbO₂)")
ax2.set_title("Deoxygenation vs. Time (Red Line)")
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Deoxygenation (Hb)")

# Reading data from ESP32 and plotting it
try:
    while True:
        # Receive data from ESP32
        data = client_socket.recv(1024).decode('utf-8')
        
        # Parse the data for OD and PWM
        if data:
            # Example: "OD:1.2345,PWM:200"
            data_parts = data.split(",")
            OD_value = float(data_parts[0].split(":")[1])
            # PWM_value = int(data_parts[1].split(":")[1])  # Not needed for this task

            # Increment time_counter (time in seconds)
            time_counter += 1

            # Calculate oxygenation (HbO₂) and deoxygenation (Hb) from OD
            oxygenation = 1 / OD_value  # Inversely related to OD
            deoxygenation = OD_value  # Directly related to OD

            # Append data to lists
            time_data.append(time_counter)
            oxygenation_data.append(oxygenation)
            deoxygenation_data.append(deoxygenation)

            # Plotting the graphs dynamically
            ax1.plot(time_data, oxygenation_data, 'g-', label="Oxygenation (HbO₂)")
            ax2.plot(time_data, deoxygenation_data, 'r-', label="Deoxygenation (Hb)")

            # Adjust the x-axis limits for better viewing
            ax1.set_xlim([min(time_data), max(time_data)])
            ax2.set_xlim([min(time_data), max(time_data)])

            # Redraw the graphs
            plt.draw()
            plt.pause(0.1)

except KeyboardInterrupt:
    # Close the socket and end the connection when the user presses Ctrl+C
    print("Terminating connection and closing the socket.")
    client_socket.close()

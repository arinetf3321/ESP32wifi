import serial
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Open the serial connection to the Arduino
arduino = serial.Serial('COM4', 115200)  # Change 'COM3' to your Arduino's port
time.sleep(2)  # Wait for the connection to establish

# Prepare lists to hold the data
time_data = []
voltage_data = []
sensor_data = []

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Read and plot data
try:
    while True:
        line = arduino.readline().decode('utf-8').strip()
        if "Sensor Value:" in line and "Voltage:" in line:
            parts = line.split("\t")
            sensor_value = int(parts[0].split(":")[1].strip())
            voltage = float(parts[1].split(":")[1].strip())
            
            # Append the data to the lists
            time_data.append(time.time())
            sensor_data.append(sensor_value)
            voltage_data.append(voltage)
            
            # Update the plot
            ax.clear()
            ax.scatter(time_data, sensor_data, voltage_data, c='r', marker='o')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Sensor Value')
            ax.set_zlabel('Voltage (V)')
            plt.draw()
            plt.pause(0.1)  # Pause to allow for updating the plot

except KeyboardInterrupt:
    print("Exiting...")
    arduino.close()
    plt.show()


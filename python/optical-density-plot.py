import serial
import numpy as np
import matplotlib.pyplot as plt

# Connect to Arduino serial port (adjust 'COM3' to your actual port)
arduino = serial.Serial('COM3', 115200)  # Change COM port as needed
arduino.flush()

# Number of sensor positions (10x10 grid)
grid_size = 10
OD_values = np.zeros((grid_size, grid_size))  # 10x10 grid to store OD values

# Read data from Arduino and populate OD map
while True:
    if arduino.in_waiting > 0:
        line = arduino.readline().decode('utf-8').strip()
        if line:
            sensor, OD_value = line.split(',')
            sensor_coords = sensor.split('_')[1:]  # Extract coordinates (x, y)
            x, y = int(sensor_coords[0]), int(sensor_coords[1])
            OD_values[x, y] = float(OD_value)  # Store OD value at the respective sensor location

    # After gathering the complete grid, plot the map
    if np.all(OD_values != 0):  # Check if all values are populated
        plt.imshow(OD_values, cmap='hot', interpolation='nearest')
        plt.colorbar(label='Optical Density (OD)')
        plt.title('Optical Density Map from NIR LED to Photodiode')
        plt.show()
        break  # Exit after displaying the map

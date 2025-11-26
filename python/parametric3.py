import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

# Connect to the Arduino's serial port
ser = serial.Serial('COM4', 115200)  # Adjust 'COM4' to the correct port for your system
data_buffer = []

# Define the size of the parametric image grid (e.g., 10x10)
grid_size = (10, 10)

# Initialize the figure
fig, ax = plt.subplots(figsize=(8, 6))

# Function to update the parametric image
def update_image(sensor_values):
    # Normalize the data to map it to a color scale
    norm = Normalize(vmin=np.min(sensor_values), vmax=np.max(sensor_values))

    # Create the parametric image (color-mapped grid)
    cp = ax.imshow(sensor_values, cmap='plasma', norm=norm)
    plt.colorbar(cp, ax=ax)

    # Set titles and labels
    ax.set_title('Parametric Image of Sensor Values')
    ax.set_xlabel('Sensor X')
    ax.set_ylabel('Sensor Y')

    # Show the plot
    plt.draw()
    plt.pause(0.1)

# Read data from Arduino and fill the 10x10 grid
try:
    while True:
        # Read a line from the Arduino
        line = ser.readline().decode('utf-8').strip()

        # Process the sensor value if the line is valid
        if line.startswith("Sensor Value:"):
            # Extract the numeric part, clean up the line
            try:
                sensor_value = int(line.split(":")[1].strip().split()[0])  # Get the number before the 'Voltage' part
                data_buffer.append(sensor_value)
            except ValueError:
                print(f"Invalid data received: {line}")  # Skip invalid lines

            # Once we have enough data, create the parametric image
            if len(data_buffer) >= grid_size[0] * grid_size[1]:
                # Reshape the data buffer to a 10x10 grid
                sensor_values = np.array(data_buffer[:grid_size[0] * grid_size[1]]).reshape(grid_size)

                # Update the parametric image
                update_image(sensor_values)

                # Clear the buffer for the next set of readings
                data_buffer = []

except KeyboardInterrupt:
    # Close the serial connection when done
    ser.close()
    print("Serial connection closed.")

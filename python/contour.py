import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import Normalize
import time

# Initialize serial communication (adjust the COM port and baud rate as needed)
ser = serial.Serial('COM4', 115200, timeout=1)  # Replace 'COM4' with your port

# Array to store sensor values (10x10 grid)
sensor_values = np.zeros((10, 10))

# Read data from Arduino
def read_data():
    global sensor_values
    line = ser.readline().decode('utf-8').strip()  # Read a line of data from the Arduino
    if line:  # If line contains sensor data
        values = line.split("\t")  # Split the line by tabs
        for i, value in enumerate(values):
            if i < 10:  # Ensure we don't exceed the 10 columns
                # Check if the value is numeric before converting it to an integer
                if value.isdigit():
                    sensor_values[i // 10, i % 10] = int(value)  # Store each sensor value in the grid
                else:
                    print(f"data: {value}")  # Print invalid data

# Save the current contour plot to a file
def save_contour_plot():
    norm = Normalize(vmin=np.min(sensor_values), vmax=np.max(sensor_values))
    fig, ax = plt.subplots(figsize=(8, 6))
    cp = ax.contourf(sensor_values, 50, cmap='plasma', norm=norm)  # Using 'plasma' colormap instead of black and white
    plt.colorbar(cp, ax=ax)  # Add color bar to indicate value scale
    ax.set_title('Live Contour Plot of Sensor Data')
    ax.set_xlabel('Sensor Index')
    ax.set_ylabel('Time Step')
    
    # Save the plot to a file
    fig.savefig('contour_plot.png')
    plt.close(fig)  # Close the plot to avoid it being displayed

# Generate the contour plot
def generate_contour_plot(frame):
    read_data()  # Continuously read data from Arduino

    # Normalize the color scale based on the data range with finer granularity
    norm = Normalize(vmin=np.min(sensor_values), vmax=np.max(sensor_values))
    
    # Clear previous contour plot
    ax.clear()

    # Use a higher number of contour levels to show more color changes
    cp = ax.contourf(sensor_values, 50, cmap='plasma', norm=norm)  # Using 'plasma' colormap instead of black and white
    plt.colorbar(cp, ax=ax)  # Add color bar to indicate value scale
    ax.set_title('Live Contour Plot of Sensor Data')
    ax.set_xlabel('Sensor Index')
    ax.set_ylabel('Time Step')

    # Show grid lines in yellow
    ax.grid(True, color='yellow')  # Set the grid color to yellow

    # After 30 seconds, save the plot and reset
    if frame == 30:
        save_contour_plot()
        print("Contour plot saved as 'contour_plot.png'. Resetting output...")
        time.sleep(30)  # Pause for 30 seconds before generating new output

# Main program
if __name__ == "__main__":
    print("Waiting for data from Arduino...")

    # Set up the plot
    fig, ax = plt.subplots(figsize=(8, 6))

    # Create an animated plot that updates every second
    ani = animation.FuncAnimation(fig, generate_contour_plot, interval=1000)  # Update every second

    plt.show()  # Display the live plot

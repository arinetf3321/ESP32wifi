import time
import serial
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Setup serial communication with Arduino
arduino = serial.Serial('COM4', 115200)  # Change COM port as needed
time.sleep(2)  # Wait for the serial connection to establish

# Grid size (same as Arduino)
grid_size = 10

# Initialize arrays for storing data
OD_values = np.zeros((grid_size, grid_size))
velocity_map = np.zeros((grid_size, grid_size))
phase_diff_map = np.zeros((grid_size, grid_size))

# Read data from Arduino
def read_arduino_data():
    data = []
    while True:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8').strip()
            if line.startswith('sensor_'):
                data.append(line)
            if len(data) >= grid_size * grid_size:
                break
    return data

# Process the data to calculate velocity and phase difference
def process_data(data):
    global OD_values, velocity_map, phase_diff_map
    for entry in data:
        parts = entry.split(',')
        sensor, OD_value = parts[0], float(parts[1])
        x, y = map(int, sensor.split('_')[1:3])
        OD_values[x, y] = OD_value

        # Simulate velocity (for demo purposes, using OD values for velocity map)
        velocity_map[x, y] = OD_value * 0.5  # Example calculation for velocity

        # Simulate phase difference (for demo purposes)
        phase_diff_map[x, y] = np.sin(OD_value / 10)  # Example phase calculation

# Generate the velocity and phase difference maps
def generate_maps():
    plt.figure(figsize=(12, 6))

    # Velocity Map
    plt.subplot(1, 2, 1)
    plt.imshow(velocity_map, cmap='hot', interpolation='nearest')
    plt.colorbar(label='Velocity (cm/s)')
    plt.title('Velocity Map')

    # Phase Difference Map
    plt.subplot(1, 2, 2)
    plt.imshow(phase_diff_map, cmap='jet', interpolation='nearest')
    plt.colorbar(label='Phase Diff (Radian)')
    plt.title('Phase Difference Map')

    # Save the generated images
    plt.tight_layout()
    plt.savefig('static/maps.png')  # Save the figure as a PNG file

# Route to render the maps
@app.route('/')
def index():
    # Read data from Arduino
    data = read_arduino_data()
    
    # Process the data
    process_data(data)
    
    # Generate maps
    generate_maps()

    # Serve the map image
    return render_template('index.html')

# Route to get the generated map images in JSON format (for AJAX, if needed)
@app.route('/get_maps', methods=['GET'])
def get_maps():
    return jsonify({
        'velocity_map': 'static/maps.png',
        'phase_diff_map': 'static/maps.png'
    })

if __name__ == '__main__':
    app.run(debug=True)
======
html-code
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Velocity and Phase Difference Maps</title>
</head>
<body>
    <h1>Velocity and Phase Difference Maps</h1>
    <div>
        <h2>Velocity Map</h2>
        <img src="{{ url_for('static', filename='maps.png') }}" alt="Velocity Map">
    </div>
    <div>
        <h2>Phase Difference Map</h2>
        <img src="{{ url_for('static', filename='maps.png') }}" alt="Phase Difference Map">
    </div>
</body>
</html>

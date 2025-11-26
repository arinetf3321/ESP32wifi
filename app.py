from flask import Flask, render_template
import serial
import threading
import time
import queue

# Create Flask app
app = Flask(__name__)

# Serial communication setup (adjust the port as per your system)
ser = serial.Serial('COM4', 115200)  # Update with the correct port for your system

# Queue to safely pass data from the serial reading thread to the main app
data_queue = queue.Queue()

# Function to read data from Arduino and update global variables
def read_data():
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            # Parse data from Arduino (assuming the Arduino sends data)
            if line:
                data_queue.put(line)  # Put data into the queue for Flask to access
        time.sleep(0.1)

# Start the data reading in a separate thread
data_thread = threading.Thread(target=read_data)
data_thread.daemon = True
data_thread.start()

# Route to display the dashboard
@app.route('/')
def index():
    # Retrieve data from the queue (if available)
    sensor_value, voltage, nir_led_state = "Not received", "Not received", "Not received"
    if not data_queue.empty():
        data = data_queue.get()
        # Assuming your data looks like "Sensor Value: [value] Voltage: [voltage] NIR LED Pin State: [state]"
        parts = data.split("\t")
        if len(parts) >= 3:
            sensor_value = parts[0].split(":")[1].strip()
            voltage = parts[1].split(":")[1].strip()
            nir_led_state = parts[2].split(":")[1].strip()

    return render_template('dashboard.html', sensor_value=sensor_value, voltage=voltage, nir_led_state=nir_led_state)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)

from flask import Flask, render_template_string
import serial, threading

app = Flask(__name__)
ser = serial.Serial('COM4', 115200)

latest_output = ""

def read_serial():
    global latest_output
    while True:
        line = ser.readline().decode('utf-8').strip()
        latest_output = line

# Run serial reading in background thread
threading.Thread(target=read_serial, daemon=True).start()

@app.route("/")
def index():
    return render_template_string("""
        <html>
        <head><title>ESP32 Monitor</title></head>
        <body>
            <h1>ESP32 Output</h1>
            <pre>{{output}}</pre>
        </body>
        </html>
    """, output=latest_output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

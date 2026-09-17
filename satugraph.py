import requests
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import time

# === Flask server settings ===
FLASK_URL = "http://192.168.17.133:8080/sensor-data"  # Replace with your PC IP

# === Lists to store data ===
time_data = []
spo2_data = []

start_time = time.time()

# === Set up plot ===
plt.ion()
fig, ax = plt.subplots(figsize=(10, 5))
line, = ax.plot(time_data, spo2_data, 'r-', label="Oxygen Saturation (%)")

ax.set_xlabel("Time (s)")
ax.set_ylabel("SpO₂ (%)")
ax.set_title("Cerebral Oxygenation Over Time")

# === Zoom in vertically for high sensitivity ===
# Center 50% and show only ±0.5% for 0.01% resolution visibility
ax.set_ylim(49.5, 50.5)  
ax.axhline(50, color='blue', linestyle='--', linewidth=1, label="50% reference")

# === Finer grid lines ===
ax.grid(which='major', color='gray', linestyle='-', linewidth=0.8)
ax.grid(which='minor', color='lightgray', linestyle=':', linewidth=0.5)

# Configure major and minor ticks for high sensitivity
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))     # major X every 5 s
ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))     # minor X every 1 s
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.2))   # major Y every 0.2%
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.01))  # minor Y every 0.01%

ax.legend(loc='upper right')

# === Function to map OD to SpO2 % ===
def od_to_spo2(od):
    # Use linear mapping
    spo2 = max(50, min(100, 100 - (od - 0.1) * 55))
    return spo2

try:
    while True:
        try:
            # Fetch latest sensor data from Flask
            response = requests.get(FLASK_URL, timeout=2)
            if response.status_code == 200:
                data = response.json()
                od_value = float(data.get("od", 0.0))
                spo2 = od_to_spo2(od_value)

                current_time = time.time() - start_time
                time_data.append(current_time)
                spo2_data.append(spo2)

                # Keep last 200 points
                time_data = time_data[-200:]
                spo2_data = spo2_data[-200:]

                # Update plot
                line.set_xdata(time_data)
                line.set_ydata(spo2_data)
                ax.set_xlim(max(0, current_time - 20), current_time + 1)

                plt.pause(0.05)
            else:
                print(f"HTTP error: {response.status_code}")

        except requests.exceptions.RequestException:
            print("Failed to fetch data from Flask")

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    plt.ioff()
    plt.show()
# app.py

import time
import statistics
import random
import threading
from flask import Flask, jsonify, render_template, request
from hw_layer import (measure_distance, analyze_absorption, read_color,
                      read_temperature, buzzer_beep, update_physical_oled) 

app = Flask(__name__)

# --- YOUR PERSONALIZED CALIBRATION ---
# This function is now tuned specifically to your hardware based on your tests.
def analyze_shape(sigma):
    """Calibrates a shape based on the standard deviation of distance readings."""
    if sigma < 0.175: return "Flat Surface"
    elif sigma < 0.204: return "Slightly Curved"
    else: return "Curved / Irregular"
# -------------------------------------

@app.route('/')
def index():
    """Serves the main dashboard page."""
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan_route():
    """Handles multi-reading scans using the robust 'macro sigma' method."""
    data = request.get_json()
    repetitions = data.get('repetitions', 20) # Dashboard buttons use 20
    repetitions = min(int(repetitions), 100)
    
    # --- NEW, MORE ROBUST MEASUREMENT METHOD ---
    all_distances = []
    for _ in range(repetitions):
        # Get one stable reading per loop
        avg, _ = measure_distance(samples=10)
        if avg > 0:
            all_distances.append(avg)
        time.sleep(0.05) # A small delay between stable readings
    
    if len(all_distances) < 2:
        return jsonify({"error": "Failed to get enough valid readings."}), 500
    
    scan_data = [{"reading": i + 1, "distance": dist} for i, dist in enumerate(all_distances)]
    
    # Calculate the single, overall sigma of the entire scan
    overall_sigma = round(statistics.stdev(all_distances), 3)
    avg_distance = round(statistics.mean(all_distances), 2)
    # --- END OF NEW METHOD ---

    # --- Analysis using your new calibration ---
    shape_result = analyze_shape(overall_sigma)
    # Material analysis can also use this more robust sigma value
    material_type = "Absorbing" if analyze_absorption(overall_sigma) == "High" else "Reflective"
    
    # --- Environmental Data ---
    temps = read_temperature()
    color = read_color()
    temp_diff = round(temps["object"] - temps["ambient"], 1)
    ultrasonic_speed = round(331.3 + 0.606 * temps["ambient"], 1)

    # Send primary results to the physical OLED display
    threading.Thread(
        target=update_physical_oled, 
        args=(f"{avg_distance} cm", shape_result, material_type)
    ).start()

    # --- Return all data to the web dashboard ---
    return jsonify({
        "scan_data": scan_data,
        "statistics": { "average": avg_distance, "sigma": overall_sigma },
        "shape_analysis": shape_result,
        "material_analysis": material_type,
        "environment": {
            "color": color["color_name"],
            "temp_difference": temp_diff,
            "ultrasonic_speed": ultrasonic_speed
        }
    })
    
@app.route('/measure_distance_single', methods=['POST'])
def measure_distance_single_route():
    """Handles the single 'Check Distance' button press."""
    avg, sigma = measure_distance(samples=10)
    
    threading.Thread(
        target=update_physical_oled, 
        args=(f"{avg} cm", "N/A", "N/A")
    ).start()
    
    return jsonify({ "distance": avg, "sigma": sigma })

@app.route('/buzzer', methods=['POST'])
def buzz_route():
    """Triggers the buzzer."""
    threading.Thread(target=buzzer_beep, args=(0.05,)).start()
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    # Remember to run with use_reloader=False to prevent GPIO busy errors
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

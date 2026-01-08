# app.py

import time
import statistics
import random
import threading
from flask import Flask, jsonify, render_template, request
# MODIFIED: Simplified imports
from hw_layer import (measure_distance, analyze_absorption, 
                      buzzer_beep, update_physical_oled) 

app = Flask(__name__)

# --- YOUR PERSONALIZED SHAPE CALIBRATION ---
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
    """Handles multi-reading scans for Shape and Material checks."""
    data = request.get_json()
    repetitions = data.get('repetitions', 20)
    repetitions = min(int(repetitions), 100)
    
    # --- Using the robust "macro sigma" measurement method ---
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
    # --- End of method ---

    # --- Analysis using your calibrations ---
    shape_result = analyze_shape(overall_sigma)
    material_type = "Absorbing" if analyze_absorption(overall_sigma) == "High" else "Reflective"
    
    # MODIFIED: Removed calls to temp/color sensors and use a standard value
    ultrasonic_speed_standard = 343.0 # Speed of sound in m/s at ~20°C

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
        # MODIFIED: Send simplified environmental data
        "environment": {
            "color": "N/A",
            "temp_difference": "N/A",
            "ultrasonic_speed": ultrasonic_speed_standard
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
    # Run with reloader disabled for stability with hardware
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

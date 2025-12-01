# calibrate.py

import time
import statistics
# MODIFIED: Removed the unused BUZZER_PIN import
from hw_layer import measure_distance, buzzer_beep

# --- CONFIGURATION ---
READINGS_PER_OBJECT = 50

# --- DATA STORAGE ---
calibration_data = {
    "flat": [],
    "slightly_curved": [],
    "curved_irregular": []
}

def run_calibration_test(shape_name, instructions):
    """
    A guided function to take multiple sensor readings for a specific shape.
    """
    print("\n" + "="*50)
    print(f"  CALIBRATION STEP: Testing a '{shape_name.upper()}' Object")
    print("="*50)
    print(f"\n  Instructions: {instructions}")
    
    input("\n  >>> Press Enter when you are ready to begin the test...")
    
    print(f"\n  Taking {READINGS_PER_OBJECT} readings. Please keep the object still...")
    
    sigmas = []
    for i in range(READINGS_PER_OBJECT):
        avg_dist, sigma = measure_distance(samples=2)
        
        if avg_dist > 0:
            sigmas.append(sigma)
            
        print(f"  Reading {i+1}/{READINGS_PER_OBJECT} -> Distance: {avg_dist:.2f} cm, Sigma: {sigma:.2f}")
        time.sleep(0.1)
        
    # MODIFIED: Corrected the function call to match the new definition
    buzzer_beep(0.2) # Beep to signal completion
    print("\n  ...Test complete for this object.")
    return sigmas


def analyze_results(data):
    """
    Analyzes the collected data and suggests new calibration thresholds.
    """
    print("\n" + "#"*60)
    print("  CALIBRATION ANALYSIS & CONCLUSION")
    print("#"*60)
    
    if not data["flat"]:
        print("\nERROR: No data was collected for the 'flat' object. Cannot generate conclusion.")
        return

    max_flat_sigma = max(data["flat"])
    print(f"\n- FLAT object readings produced sigmas from {min(data['flat']):.2f} to {max_flat_sigma:.2f}.")

    if not data["slightly_curved"]:
        print("\nNOTE: No data for 'slightly curved'. The conclusion will be less precise.")
        threshold1 = round(max_flat_sigma * 2.5, 2)
        threshold2 = round(threshold1 * 3, 2)
    else:
        min_slight_sigma = min(data["slightly_curved"])
        max_slight_sigma = max(data["slightly_curved"])
        print(f"- SLIGHTLY CURVED object readings produced sigmas from {min_slight_sigma:.2f} to {max_slight_sigma:.2f}.")
        threshold1 = round((max_flat_sigma + min_slight_sigma) / 2, 2)
        
        if not data["curved_irregular"]:
             print("\nNOTE: No data for 'curved/irregular'. The second threshold will be a guess.")
             threshold2 = round(max_slight_sigma * 2.5, 2)
        else:
            min_irregular_sigma = min(data["curved_irregular"])
            print(f"- CURVED/IRREGULAR object readings produced sigmas from {min_irregular_sigma:.2f} to {max(data['curved_irregular']):.2f}.")
            threshold2 = round((max_slight_sigma + min_irregular_sigma) / 2, 2)

    print("\n" + "*"*60)
    print("  SUGGESTED CALIBRATION CODE")
    print("*"*60)
    print("\nBased on your tests, it is recommended to replace the")
    print("'analyze_shape' function in your 'app.py' file with this code:\n")

    print("--- (Copy the code below) ------------------------------------")
    print("def analyze_shape(sigma):")
    print(f"    if sigma < {threshold1}: return \"Flat Surface\"")
    print(f"    elif sigma < {threshold2}: return \"Slightly Curved\"")
    print(f"    else: return \"Curved / Irregular\"")
    print("----------------------------------------------------------\n")


if __name__ == "__main__":
    print("="*50)
    print("  Smart Surface Detector - SHAPE CALIBRATION UTILITY")
    print("="*50)
    print("\nThis script will guide you through testing different objects")
    print("to generate the ideal calibration values for your sensor.")
    
    calibration_data["flat"] = run_calibration_test(
        "flat",
        "Place a hard, flat object (like a large book or a piece of wood) about 20-30 cm away from the sensor."
    )
    
    calibration_data["slightly_curved"] = run_calibration_test(
        "slightly_curved",
        "Place a gently curved object (like a large can, bottle, or pipe) in front of the sensor."
    )

    calibration_data["curved_irregular"] = run_calibration_test(
        "curved_irregular",
        "Place a very curved or irregular object (like a ball, a crumpled piece of paper, or your hand) in front of the sensor."
    )
    
    analyze_results(calibration_data)

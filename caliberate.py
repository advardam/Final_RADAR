# calibrate.py (NEW & IMPROVED METHODOLOGY)

import time
import statistics
from hw_layer import measure_distance, buzzer_beep

# --- CONFIGURATION ---
# The number of stable readings to collect for each object.
READINGS_PER_OBJECT = 50

# --- DATA STORAGE ---
# This will now hold a single, overall sigma value for each test.
calibration_results = {
    "flat": 0.0,
    "slightly_curved": 0.0,
    "curved_irregular": 0.0
}

def run_calibration_test(shape_name, instructions):
    """
    Guides the user through a test and returns the SINGLE standard deviation
    of all readings taken during that test.
    """
    print("\n" + "="*50)
    print(f"  CALIBRATION STEP: Testing a '{shape_name.upper()}' Object")
    print("="*50)
    print(f"\n  Instructions: {instructions}")
    
    input("\n  >>> Press Enter when you are ready to begin...")
    
    print(f"\n  Collecting {READINGS_PER_OBJECT} stable distance readings. Please keep the object still...")
    
    all_distances = []
    for i in range(READINGS_PER_OBJECT):
        # We now use a HIGH sample count to get one stable, reliable reading.
        avg_dist, _ = measure_distance(samples=10)
        
        if avg_dist > 0:
            all_distances.append(avg_dist)
            
        print(f"  Reading {i+1}/{READINGS_PER_OBJECT} -> Stable Distance: {avg_dist:.2f} cm")
        time.sleep(0.05) # A very small delay
        
    buzzer_beep(0.2)
    
    if len(all_distances) < 2:
        print("\n  ERROR: Not enough valid readings were taken to calculate a result.")
        return 0.0

    # --- THE NEW METHOD ---
    # Calculate the ONE standard deviation of the ENTIRE list of distances.
    overall_sigma = round(statistics.stdev(all_distances), 3) # Use 3 decimal places for more precision
    
    print(f"\n  ...Test complete. Overall Standard Deviation (σ) for this object is: {overall_sigma:.3f}")
    return overall_sigma


def analyze_results(results):
    """
    Analyzes the collected sigma values and helps the user create the code.
    """
    print("\n" + "#"*60)
    print("  CALIBRATION ANALYSIS & CONCLUSION")
    print("#"*60)
    
    flat_sigma = results["flat"]
    slight_sigma = results["slightly_curved"]
    irregular_sigma = results["curved_irregular"]

    print(f"\n- Your FLAT object produced an overall sigma of:      {flat_sigma:.3f}")
    print(f"- Your SLIGHTLY CURVED object produced a sigma of: {slight_sigma:.3f}")
    print(f"- Your IRREGULAR object produced a sigma of:     {irregular_sigma:.3f}")
    
    if flat_sigma == 0 or slight_sigma == 0 or irregular_sigma == 0:
        print("\nWARNING: One of your tests resulted in a sigma of 0.0.")
        print("This is unusual. Please ensure you are using different object shapes.")
        return
        
    if not (flat_sigma < slight_sigma < irregular_sigma):
        print("\nWARNING: The sigma values are not in the expected order (flat < slight < irregular).")
        print("This suggests a potential issue with the test setup (e.g., object angle, background echoes).")
        print("Please try re-running the calibration in a clear, stable environment.")

    # Suggest thresholds that are halfway between the measured values.
    threshold1 = round((flat_sigma + slight_sigma) / 2, 3)
    threshold2 = round((slight_sigma + irregular_sigma) / 2, 3)
    
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
    print("  Smart Surface Detector - SHAPE CALIBRATION UTILITY (v2)")
    print("="*50)
    
    calibration_results["flat"] = run_calibration_test(
        "flat", "Place a hard, FLAT object about 20-30 cm away."
    )
    
    calibration_results["slightly_curved"] = run_calibration_test(
        "slightly_curved", "Place a GENTLY CURVED object (like a large bottle) in the same position."
    )

    calibration_results["curved_irregular"] = run_calibration_test(
        "curved_irregular", "Place a VERY CURVED or IRREGULAR object (like a ball) in the same position."
    )
    
    analyze_results(calibration_results)

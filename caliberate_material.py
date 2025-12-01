# calibrate_material.py (NEW & IMPROVED METHODOLOGY)

import time
import statistics
from hw_layer import measure_distance, buzzer_beep

# --- CONFIGURATION ---
# The number of stable readings to collect for each material.
READINGS_PER_OBJECT = 50

# --- DATA STORAGE ---
# This will hold the single, overall sigma value for each test.
calibration_results = {
    "reflective": 0.0,
    "absorbent": 0.0
}

def run_calibration_test(material_type, instructions):
    """
    Guides the user through a test and returns the SINGLE standard deviation
    of all readings taken during that test.
    """
    print("\n" + "="*50)
    print(f"  CALIBRATION STEP: Testing a '{material_type.upper()}' Material")
    print("="*50)
    print(f"\n  Instructions: {instructions}")
    
    # CRITICAL: Use a flat surface for all tests to isolate the material's effect from its shape.
    print("  Please ensure the surface of the object is as FLAT as possible.")
    
    input("\n  >>> Press Enter when you are ready to begin...")
    
    print(f"\n  Collecting {READINGS_PER_OBJECT} stable distance readings. Please keep the object still...")
    
    all_distances = []
    for i in range(READINGS_PER_OBJECT):
        # We use a HIGH sample count to get one stable, reliable reading.
        avg, _ = measure_distance(samples=10)
        
        if avg > 0:
            all_distances.append(avg)
            
        print(f"  Reading {i+1}/{READINGS_PER_OBJECT} -> Stable Distance: {avg:.2f} cm")
        time.sleep(0.05)
        
    buzzer_beep(0.2)
    
    if len(all_distances) < 2:
        print("\n  ERROR: Not enough valid readings were taken to calculate a result.")
        return 0.0

    # Calculate the ONE standard deviation of the ENTIRE list of distances.
    overall_sigma = round(statistics.stdev(all_distances), 3)
    
    print(f"\n  ...Test complete. Overall Standard Deviation (σ) for this material is: {overall_sigma:.3f}")
    return overall_sigma


def analyze_results(results):
    """
    Analyzes the collected sigma values and generates the new function.
    """
    print("\n" + "#"*60)
    print("  MATERIAL CALIBRATION ANALYSIS & CONCLUSION")
    print("#"*60)
    
    reflective_sigma = results["reflective"]
    absorbent_sigma = results["absorbent"]
    
    if reflective_sigma == 0 or absorbent_sigma == 0:
        print("\nWARNING: One of your tests resulted in a sigma of 0.0.")
        print("This is unusual. Please ensure you used different material types.")
        return

    print(f"\n- Your REFLECTIVE material produced an overall sigma of: {reflective_sigma:.3f}")
    print(f"- Your ABSORBENT material produced a sigma of:     {absorbent_sigma:.3f}")

    if reflective_sigma >= absorbent_sigma:
        print("\nWARNING: The sigma for the reflective material is higher than or equal to the absorbent one.")
        print("This is unexpected. Ensure the reflective object was perfectly flat and stable,")
        print("and that the absorbent material was sufficiently soft.")
        # Suggest a threshold anyway, but with a warning
        threshold = round((reflective_sigma + absorbent_sigma) / 2, 3)
    else:
        # Suggest a threshold halfway between the two material types for a clear cutoff.
        threshold = round((reflective_sigma + absorbent_sigma) / 2, 3)

    print("\n" + "*"*60)
    print("  SUGGESTED CALIBRATION CODE")
    print("*"*60)
    print("\nBased on your tests, it is recommended to replace the")
    print("'analyze_absorption' function in your 'hw_layer.py' file with this code:\n")

    print("--- (Copy the code below) ------------------------------------")
    print("def analyze_absorption(sigma):")
    print(f"    # Calibrated threshold: a sigma above {threshold} suggests absorption.")
    print(f"    if sigma > {threshold}:")
    print(f"        return \"High\"  # Likely Absorbent")
    print(f"    else:")
    print(f"        return \"Low\"   # Likely Reflective")
    print("----------------------------------------------------------\n")


if __name__ == "__main__":
    print("="*60)
    print("  Smart Surface Detector - MATERIAL CALIBRATION UTILITY (v2)")
    print("="*60)
    
    calibration_results["reflective"] = run_calibration_test(
        "reflective",
        "Place a hard, FLAT object (wood, plastic, metal, or a thick book) about 20-30 cm away."
    )
    
    calibration_results["absorbent"] = run_calibration_test(
        "absorbent",
        "Place a soft, FLAT object (a sponge, thick towel, foam block, or carpet square) in the same position."
    )
    
    analyze_results(calibration_results)

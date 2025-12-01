# hw_layer.py

import time
import statistics
from gpiozero import Device, Buzzer, Button, DistanceSensor
from gpiozero.pins.lgpio import LGPIOFactory

# I2C libraries
import board
import busio
import adafruit_tcs34725
import adafruit_mlx90614

# Luma OLED libraries
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

# --- Set the modern pin factory for the Pi 5 ---
try:
    Device.pin_factory = LGPIOFactory()
    print("INFO: Successfully set pin factory to lgpio for Raspberry Pi 5.")
except Exception as e:
    print("--- FATAL ERROR ---")
    print("Could not set the lgpio pin factory. Ensure 'python3-lgpio' is installed.")
    print(f"Error: {e}")
    exit()

# --- HARDWARE PIN CONFIGURATION ---
ULTRASONIC_TRIG_PIN = 23
ULTRASONIC_ECHO_PIN = 24
BUZZER_PIN = 18
BUTTON_PIN = 17

# --- HARDWARE INITIALIZATION ---
# ... (Initialization code remains the same) ...
try:
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    mlx_sensor = adafruit_mlx90614.MLX90614(i2c_bus)
    tcs_sensor = adafruit_tcs34725.TCS34725(i2c_bus)
    oled_serial = i2c(port=1, address=0x3C)
    oled_device = ssd1306(oled_serial)
    distance_sensor_obj = DistanceSensor(echo=ULTRASONIC_ECHO_PIN, trigger=ULTRASONIC_TRIG_PIN)
    buzzer_obj = Buzzer(BUZZER_PIN)
    button_obj = Button(BUTTON_PIN, pull_up=True)
except Exception as e:
    print(f"ERROR during hardware initialization: {e}")


# --- CORE HARDWARE FUNCTIONS ---
# ... (get_color_name, read_temperature, etc. remain the same) ...
def get_color_name(rgb):
    r, g, b = rgb;
    if r > 200 and g > 200 and b > 200: return "White";
    if r < 30 and g < 30 and b < 30: return "Black";
    if r > g and r > b: return "Red";
    if g > r and g > b: return "Green";
    if b > r and b > g: return "Blue";
    if r > 100 and g > 100 and b < 50: return "Yellow";
    return "Unknown"

def read_temperature():
    if mlx_sensor:
        try:
            return {"ambient": round(mlx_sensor.ambient_temperature, 1), "object": round(mlx_sensor.object_temperature, 1)}
        except (OSError, IOError): return {"ambient": 0, "object": 0}
    return {"ambient": 25.0, "object": 25.0}

def read_color():
    if tcs_sensor:
        try: return {"color_name": get_color_name(tcs_sensor.color_rgb_bytes)}
        except Exception: return {"color_name": "Error"}
    return {"color_name": "N/A"}

def buzzer_beep(duration):
    if buzzer_obj: buzzer_obj.beep(on_time=duration, n=1)

def read_button():
    if button_obj: return not button_obj.is_pressed
    return True

def measure_distance(samples=10):
    if not distance_sensor_obj: return 0, 0
    readings = []
    for _ in range(samples):
        time.sleep(0.01)
        distance_cm = distance_sensor_obj.distance * 100
        if 2 < distance_cm < 400: readings.append(distance_cm)
    if not readings: return 0, 0
    avg = round(statistics.mean(readings), 2)
    std_dev = round(statistics.stdev(readings) if len(readings) > 1 else 0, 2)
    return avg, std_dev

# --- YOUR PERSONALIZED MATERIAL CALIBRATION ---
def analyze_absorption(sigma):
    # Calibrated threshold: a sigma above 0.096 suggests absorption.
    if sigma > 0.096:
        return "High"  # Likely Absorbent
    else:
        return "Low"   # Likely Reflective
# ---------------------------------------------

def update_physical_oled(distance, shape, material):
    if oled_device:
        try:
            with canvas(oled_device) as draw:
                draw.text((0, 0), f"Dist: {distance}", fill="white")
                draw.text((0, 12), f"Shape: {shape}", fill="white")
                draw.text((0, 24), f"Mat: {material}", fill="white")
        except Exception as e: print(f"Error writing to OLED: {e}")
    else:
        print(f"--- OLED Sim ---\nDist: {distance}\nShape: {shape}\nMat: {material}\n----------------")

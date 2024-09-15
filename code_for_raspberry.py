import time
import requests
import RPi.GPIO as GPIO

# Constants
FLASK_SERVER_URL = 'http://localhost:5000/update_location'
PRESSURE_SENSOR_PIN = 17  # Example GPIO pin for pressure sensor
ANGLE_SENSOR_PIN = 18    # Example GPIO pin for angle sensor
DISTANCE_SENSOR_TRIGGER_PIN = 23  # Example GPIO pin for sonar trigger
DISTANCE_SENSOR_ECHO_PIN = 24     # Example GPIO pin for sonar echo
DISTANCE_REDUCTION_PERCENT = 0.1  # 10%

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PRESSURE_SENSOR_PIN, GPIO.IN)
GPIO.setup(ANGLE_SENSOR_PIN, GPIO.IN)
GPIO.setup(DISTANCE_SENSOR_TRIGGER_PIN, GPIO.OUT)
GPIO.setup(DISTANCE_SENSOR_ECHO_PIN, GPIO.IN)

def get_pressure_sensor_data():
    # Replace with actual code to read from the pressure sensor
    return GPIO.input(PRESSURE_SENSOR_PIN)

def get_angle_sensor_data():
    # Replace with actual code to read from the angle sensor
    return GPIO.input(ANGLE_SENSOR_PIN)

def get_distance_sensor_data():
    # Trigger the distance sensor
    GPIO.output(DISTANCE_SENSOR_TRIGGER_PIN, True)
    time.sleep(0.00001)
    GPIO.output(DISTANCE_SENSOR_TRIGGER_PIN, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(DISTANCE_SENSOR_ECHO_PIN) == 0:
        start_time = time.time()

    while GPIO.input(DISTANCE_SENSOR_ECHO_PIN) == 1:
        stop_time = time.time()

    elapsed_time = stop_time - start_time
    distance = (elapsed_time * 34300) / 2  # Speed of sound is 34300 cm/s

    return distance

def get_speed():
    # Replace with actual code to calculate the car's speed
    return 50  # Example speed in km/h

def get_steering_angle():
    angle_data = get_angle_sensor_data()
    # Convert angle_data to actual angle
    return angle_data * 360 / 1024  # Example conversion

def send_data_to_flask(lat, lng, speed, steering_angle, force, front_car_speed):
    data = {
        'lat': lat,
        'lng': lng,
        'speed': speed,
        'steering_angle': steering_angle,
        'force': force,
        'front_car_speed': front_car_speed
    }
    try:
        response = requests.post(FLASK_SERVER_URL, json=data)
        if response.status_code == 200:
            print("Data sent successfully")
        else:
            print("Failed to send data:", response.status_code)
    except Exception as e:
        print("Error sending data:", e)

def calculate_front_car_speed(current_speed, initial_distance, new_distance, time_to_cover_10_percent):
    distance_reduction = initial_distance - new_distance
    if distance_reduction <= 0:
        return 0  # No movement detected

    time_to_cover_10_percent = time_to_cover_10_percent / 100.0  # Convert to percentage
    distance_to_cover = initial_distance * DISTANCE_REDUCTION_PERCENT
    if distance_reduction < distance_to_cover:
        return 0  # Not enough data to calculate speed

    speed_of_front_car = distance_to_cover / time_to_cover_10_percent
    return speed_of_front_car

def main():
    prev_distance = get_distance_sensor_data()
    prev_time = time.time()

    while True:
        current_distance = get_distance_sensor_data()
        current_time = time.time()

        # Calculate the time it took to cover 10% of the distance
        time_interval = current_time - prev_time

        # Calculate speed of the car in front
        front_car_speed = calculate_front_car_speed(get_speed(), prev_distance, current_distance, time_interval)

        # Replace these with actual latitude and longitude
        lat = 0.0
        lng = 0.0

        force = get_pressure_sensor_data()
        steering_angle = get_steering_angle()
        speed = get_speed()

        # Print data for debugging
        print(f"Latitude: {lat}, Longitude: {lng}, Speed: {speed}, Steering Angle: {steering_angle}, Force: {force}, Distance: {current_distance}, Front Car Speed: {front_car_speed}")

        # Send data to Flask server
        send_data_to_flask(lat, lng, speed, steering_angle, force, front_car_speed)

        # Update previous distance and time
        prev_distance = current_distance
        prev_time = current_time

        # Wait before sending the next data point
        time.sleep(1)

if __name__ == "__main__":
    main()

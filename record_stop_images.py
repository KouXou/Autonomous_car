import Jetson.GPIO as GPIO
from car.car import Car
from directory_manager.dir_manager import DirectoryManager
from mqtt_connection.mqtt_car import MqttCar
from distance_sensor.distance_sensor import DistanceSensor
from camera.car_camera import CarCamera
from led.single_led import SingleLED
import utils.constants as const
import sys
import os
import time
from utils.keyboard_reader import KeyboardReader

GPIO.setmode(GPIO.BCM)
# Create MQTT class
mqtt = MqttCar()
# Create directory manager class
dir_manager = DirectoryManager()
# Crete keyboard reader class
keyboard_reader = KeyboardReader()
# Create car camera class
car_camera = CarCamera(autopilot=False, record_stops=True)
# Create distance sensor class
distance_sensor = DistanceSensor(GPIO)
# Create car class
car = Car(GPIO, 65)
# Create LED class
led = SingleLED(GPIO)

# Set initial values
created_dir, start_rec = dir_manager.create_directory()
try:

    mqtt.start()
    led.onStartCarLEDs()
    car_camera.start()
    mqtt.publish(const.record_stop_dataset_mode, const.car_mode_topic)
    while True:
        key_pressed = keyboard_reader.readKey()

        if key_pressed == ' ':
            # Turn On green LED
            led.turnOn(const.green_LED_pin)
            time.sleep(0.5)
            led.turnOff(const.green_LED_pin)
            # Take photo
            car_camera.take_pic(created_dir=created_dir, start_rec=start_rec)
        elif key_pressed == 'p':
            car_camera.stop_photo_camera()
            car_camera.join()
            car_camera = None
        elif ord(key_pressed) == 3:
            break
        if car_camera is not None:
            car_camera.pass_csv_param(car_move=car.move,
                                      car_speed=car.speed,
                                      distance=distance_sensor.distance)
except KeyboardInterrupt:
    print('turn off')
    GPIO.cleanup()
    try:
        mqtt.disconnect()
        sys.exit(0)
    except SystemExit:
        os._exit(0)
finally:
    led.turnOff(const.green_LED_pin)
    if car_camera is not None:
        car_camera.stop()
        car_camera.join()
    GPIO.cleanup()

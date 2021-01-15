# This is a sample Python script.
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
from utils.keyboard_reader import KeyboardReader

# Set Jetson GPIO Mode
GPIO.setmode(GPIO.BCM)
# Create mqtt car class
mqtt = MqttCar()
# Create directory manager class
dir_manager = DirectoryManager()
# Crete keyboard reader class
keyboard_reader = KeyboardReader()
# Create LED class
led = SingleLED(GPIO)
# Create Car class
car = Car(GPIO, 65)
# Create Distance sensor class
distance_sensor = DistanceSensor(GPIO)
# Create car camera class
car_camera = CarCamera(autopilot=False, record_stops=False)

# Set initial values
created_dir = ''
start_rec = ''
try:
    # Start mqtt
    mqtt.start()
    # Led startup
    led.onStartCarLEDs()

    # Publish init values to relevant topics
    mqtt.publish(car.speed, 'car/speed/value')
    mqtt.publish(car.move, 'car/move')

    # Start camera parallel thread
    car_camera.start()

    while True:
        # Read keyboard input
        key_press = keyboard_reader.readKey()

        if key_press == 0:
            car.forward()
            mqtt.publish(car.move, 'car/move')
        elif key_press == 1:
            car.backward()
            mqtt.publish(car.move, 'car/move')
        elif key_press == 2:
            if car.direction == const.FWD:
                car.forwardRight()
                mqtt.publish(car.move, 'car/move')
            elif car.direction == const.BWD:
                car.backwardRight()
                mqtt.publish(car.move, 'car/move')
        elif key_press == 3:
            if car.direction == const.FWD:
                car.forwardLeft()
                mqtt.publish(car.move, 'car/move')
            elif car.direction == const.BWD:
                car.backwardLeft()
                mqtt.publish(car.move, 'car/move')
        elif key_press == ' ':
            car.stop()
            mqtt.publish(car.move, 'car/move')
        elif key_press == '0':
            car.stop()
            mqtt.publish(car.move, 'car/move')
        elif key_press == '1':
            car.low_speed()
            mqtt.publish(car.speed, 'car/speed/value')
        elif key_press == '2':
            car.medium_speed()
            mqtt.publish(car.speed, 'car/speed/value')
        elif key_press == '3':
            car.high_speed()
            mqtt.publish(car.speed, 'car/speed/value')
        elif key_press == 'o':
            created_dir, start_rec = dir_manager.create_directory()
            car_camera.start_recording(created_dir=created_dir, start_rec=start_rec)
            # Turn On Red LED
            led.turnOn(const.red_LED_pin)

        elif key_press == 'p':
            # Stop camera record
            car_camera.stop_recording()
            # Turn Off Red LED
            led.turnOff(const.red_LED_pin)

        elif key_press == 'q':
            car_camera.stop()
            car_camera.join()
            car_camera = None
        elif ord(key_press) == 3:
            break
        if car_camera is not None:
            car_camera.pass_csv_param(input_command=0,
                                      car_move=car.move,
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
    if car_camera is not None:
        car_camera.stop()
        car_camera.join()
    GPIO.cleanup()

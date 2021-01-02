# This is a sample Python script.
import Jetson.GPIO as GPIO
from car.car import Car
from mqtt_connection.mqtt_car import MqttCar
from distance_sensor.distance_sensor import DistanceSensor
from camera.car_camera import CarCamera
from led.single_led import SingleLED
import utils.constants as const
import sys
import termios
import tty
import os


def readChar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if ch == '0x03':
        raise KeyboardInterrupt
    return ch


def readKey(getchar_fn=None):
    getchar = getchar_fn or readChar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1
    c3 = getchar()
    return ord(c3) - 65  # 0=Up, 1=Down, 2=Right, 3=Left arrows


GPIO.setmode(GPIO.BCM)
mqtt = MqttCar()

car_camera = None
try:

    mqtt.start()
    led = SingleLED(GPIO)
    led.onStartCarLEDs()

    car = Car(GPIO)

    distance_sensor = DistanceSensor(GPIO)
    mqtt.publish(car.speed, 'car/speed/value')
    mqtt.publish(car.move, 'car/move')
    while True:
        keyp = readKey()
        # print(keyp)
        if keyp == 0:
            car.forward()
            mqtt.publish(car.move, 'car/move')
        elif keyp == 1:
            car.backward()
            mqtt.publish(car.move, 'car/move')
        elif keyp == 2:
            if car.direction == const.FWD:
                car.forwardRight()
                mqtt.publish(car.move, 'car/move')
            elif car.direction == const.BWD:
                car.backwardRight()
                mqtt.publish(car.move, 'car/move')
        elif keyp == 3:
            if car.direction == const.FWD:
                car.forwardLeft()
                mqtt.publish(car.move, 'car/move')
            elif car.direction == const.BWD:
                car.backwardLeft()
                mqtt.publish(car.move, 'car/move')
        elif keyp == ' ':
            car.stop()
            mqtt.publish(car.move, 'car/move')
        elif keyp == '0':
            car.stop()
            mqtt.publish(car.move, 'car/move')
        elif keyp == '1':
            car.low_speed()
            mqtt.publish(car.speed, 'car/speed/value')
        elif keyp == '2':
            car.medium_speed()
            mqtt.publish(car.speed, 'car/speed/value')
        elif keyp == '3':
            car.high_speed()
            mqtt.publish(car.speed, 'car/speed/value')
        elif keyp == 'o':
            car_camera = CarCamera(led)
            car_camera.start()
        elif keyp == 'p':
            car_camera.stop()
            car_camera.join()
            car_camera = None
        elif ord(keyp) == 3:
            break
        if car_camera is not None:
            car_camera.pass_csv_param(car.direction, car.move, car.speed, distance_sensor.distance)
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

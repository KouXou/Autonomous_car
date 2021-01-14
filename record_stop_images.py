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

mqtt.start()
led = SingleLED(GPIO)
led.onStartCarLEDs()
try:
    car = Car(GPIO, 65)

    distance_sensor = DistanceSensor(GPIO)
    car_camera = CarCamera(led, autopilot=False, record_stops=True)

    car_camera.start()

    while True:
        keyp = readKey()

        if keyp == ' ':
            car_camera.take_pic()
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
    led.turnOff(const.green_LED_pin)
    if car_camera is not None:
        car_camera.stop()
        car_camera.join()
    GPIO.cleanup()

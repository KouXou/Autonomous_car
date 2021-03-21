import torch
import Jetson.GPIO as GPIO
from car.car import Car
from mqtt_connection.mqtt_car import MqttCar
from led.single_led import SingleLED
from camera.car_camera import CarCamera
import sys
import os
import utils.constants as const
from utils.keyboard_reader import KeyboardReader
from utils.preprocessor import ImagePreProcessor
from torch2trt import TRTModule

class_names = const.output_classes
FILES_PATH = '/home/kostas/Autonomous_car/files/'
model_name = 'track21+22+23+speed+stop_1_model_state'
# model_name = 'track21+22+23_1_model_state'


def load_trt_model():
    print('Start loading TRT model')
    model_trt = TRTModule()
    model_trt.load_state_dict(torch.load(FILES_PATH + model_name + '_trt.pt'))
    print('TRT model loaded')
    return model_trt


GPIO.setmode(GPIO.BCM)
mqtt = MqttCar()

device = (torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'))
print(f"Training on device {device}.")
car_camera = None
try:
    loaded_model = load_trt_model()
    preprocessor = ImagePreProcessor(224, 224)

    mqtt.start()
    led = SingleLED(GPIO)
    led.onStartCarLEDs()

    car = Car(GPIO, speed=42)

    car_camera = CarCamera(autopilot=True, record_stops=False, video_output=True)
    car_camera.start()
    keyboard_reader = KeyboardReader()
    mqtt.publish(car.move, const.car_move_topic)
    mqtt.publish(car.speed, const.car_speed_topic)
    mqtt.publish(const.autopilot_mode, const.car_mode_topic)
    counter = 0
    output = 'stop'
    output_percent = 0
    speed_limit_detected = False
    while True:

        image = car_camera.read(showMoves=True, move=output, output_percent=output_percent)

        if mqtt.speed_value is not None:
            car.set_speed(mqtt.speed_value)

        if mqtt.autopilot_status == 'ON':
            led.turnOn(const.blue_LED_pin)
            res = loaded_model(preprocessor.preprocessImage(image).to(device=device).half())
            _, index = torch.max(res, 1)

            sortedRes, indices = torch.sort(res, descending=True)

            percentage = torch.nn.functional.softmax(res, dim=1)[0] * 100
            output = class_names[index[0]]
            output_percent = percentage[index[0]].item()
            print(class_names[index[0]], percentage[index[0]].item())

            if (output == 'speed_limit' and speed_limit_detected) or (output == 'speed_limit_end' and not speed_limit_detected):
                print(print(class_names[indices[0][1]], percentage[indices[0][1]].item()))
                output = class_names[indices[0][1]]

            counter = counter + 1
            if output == 'stop':
                if output != car.move:
                    mqtt.publish(output, const.car_move_topic)
                car.stop()

            elif output == 'forward_left':
                if output != car.move:
                    mqtt.publish(output, const.car_move_topic)
                car.forwardLeft()
            elif output == 'forward_right':
                if output != car.move:
                    mqtt.publish(output, const.car_move_topic)
                car.forwardRight()
            elif output == 'forward':
                if output != car.move:
                    mqtt.publish(output, const.car_move_topic)
                car.forward()
            elif output == 'speed_limit' and not speed_limit_detected:
                speed_limit_detected = True
                car.set_speed(40)
                mqtt.publish(40, const.car_speed_topic)
                led.turnOff(const.green_LED_pin)
                led.turnOn(const.red_LED_pin)
            elif output == 'speed_limit_end' and speed_limit_detected:
                speed_limit_detected = False
                car.set_speed(45)
                mqtt.publish(45, const.car_speed_topic)
                led.turnOff(const.red_LED_pin)
                led.turnOn(const.green_LED_pin)
            # else:
            #     if output != car.move:
            #         mqtt.publish(output, const.car_move_topic)
                # car.stop()
        else:
            mqtt.publish('stop', const.car_move_topic)
            car.stop()
            led.turnOff(const.blue_LED_pin)
except KeyboardInterrupt:
    print('turn off')

    GPIO.cleanup()
    if car_camera is not None:
        car_camera.stop()
        car_camera.join()
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

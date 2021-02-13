import torch
import torchvision.models as models
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
import jetson.inference

class_names = ['forward', 'stop', 'forward_left', 'forward_right']
FILES_PATH = '/home/kostas/Autonomous_car/files/'
# model_name = 'track5_2_model_rsnet_40ep'
# model_name = 'track5+6+8_2_model_mirror'
# model_name = 'track9+10+11+12+13_3_model_state'
model_name = 'track14+15+16+17_1_model_state'
net_name = 'ssd-mobilenet-v2'
net_params = [
    '--model=/home/kostas/jetson-inference/python/training/detection/ssd/models/sign/ssd-mobilenet.onnx',
    '--labels=/home/kostas/jetson-inference/python/training/detection/ssd/models/sign/labels.txt',
    '--input-blob=input_0',
    '--output-cvg=scores',
    '--output-bbox=boxes'
]

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
    net = jetson.inference.detectNet(net_name, net_params, 0.5)
    preprocessor = ImagePreProcessor(224, 224)

    mqtt.start()
    led = SingleLED(GPIO)
    led.onStartCarLEDs()

    car = Car(GPIO, speed=42)

    car_camera = CarCamera(autopilot=True, record_stops=False, video_output=True)
    car_camera.start()
    keyboard_reader = KeyboardReader()
    mqtt.publish(car.move, 'car/move')
    mqtt.publish(car.speed, 'car/speed/value')
    mqtt.publish(const.autopilot_mode, 'car/mode')
    counter = 0
    output = 'stop'
    output_percent = 0
    while True:

        image = car_camera.read(showMoves=True, move=output, output_percent=output_percent)

        if mqtt.speed_value is not None:
            car.set_speed(mqtt.speed_value)

        if mqtt.autopilot_status == 'ON':
            led.turnOn(const.blue_LED_pin)
            res = loaded_model(preprocessor.preprocessImage(image).to(device=device).half())
            _, index = torch.max(res, 1)

            percentage = torch.nn.functional.softmax(res, dim=1)[0] * 100
            output = class_names[index[0]]
            output_percent = percentage[index[0]].item()
            print(class_names[index[0]], percentage[index[0]].item())

            if output != car.move and percentage[index[0]].item() < 95:
                continue
            # if mqtt.obj_detection_status == 'ON':
            if mqtt.obj_detection_status == 'ON' and (counter % 3) == 0:
                # detect objects in the image (with overlay)
                detections = net.Detect(image, overlay='box,labels,conf')

                for detection in detections:
                    # print(detection)
                    if detection.ClassID == 1:
                        car.set_speed(35)
                        mqtt.publish(35, 'car/speed/value')
                        led.turnOff(const.green_LED_pin)
                    elif detection.ClassID == 2:
                        car.set_speed(42)
                        mqtt.publish(42, 'car/speed/value')
                        led.turnOn(const.green_LED_pin)

            counter = counter + 1

            if output == 'stop':
                if output != car.move:
                    mqtt.publish(output, 'car/move')
                car.stop()

            elif output == 'forward_left':
                if output != car.move:
                    mqtt.publish(output, 'car/move')
                car.forwardLeft()
            elif output == 'forward_right':
                if output != car.move:
                    mqtt.publish(output, 'car/move')
                car.forwardRight()
            elif output == 'forward':
                if output != car.move:
                    mqtt.publish(output, 'car/move')
                car.forward()
            else:
                if output != car.move:
                    mqtt.publish(output, 'car/move')
                car.stop()
        else:
            mqtt.publish('stop', 'car/move')
            car.stop()
            led.turnOff(const.blue_LED_pin)

        # car_camera.video_out(image, showMoves=True, move=output, output_percent=output_percent)
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

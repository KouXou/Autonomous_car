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
from utils.preprocessor import ImagePreProcessor
from torch2trt import TRTModule
import jetson.utils

class_names = ['forward', 'stop', 'forward_left', 'forward_right']
FILES_PATH = '/home/kostas/Autonomous_car/files/'
# model_name = 'track5_2_model_rsnet_40ep'
# model_name = 'track5+6+8_2_model_mirror'
model_name = 'track9+10+11+stop_2_model_mirror'
# track5_1_model_mirror_trt.pt
# def create_model(device):
#     print('Start model creation')
#     loaded_model = models.resnet18(pretrained=True)
#     loaded_model.fc = torch.nn.Linear(512, len(class_names))
#
#     loaded_model = loaded_model.to(device)
#     return loaded_model
#
#
# def load_pretrained_weights(loaded_model):
#     print('Load pretrained model')
#     loaded_model.load_state_dict(torch.load(FILES_PATH + 'track2_3_model.pt'))
#     loaded_model = loaded_model.eval().half()
#     return loaded_model


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
    # loaded_model = create_model(device)
    # loaded_model = load_pretrained_weights(loaded_model)
    loaded_model = load_trt_model()

    preprocessor = ImagePreProcessor(336, 224)

    mqtt.start()
    led = SingleLED(GPIO)
    led.onStartCarLEDs()

    car = Car(GPIO, speed=55)

    car_camera = CarCamera(autopilot=True, record_stops=False)
    car_camera.start()

    # input = jetson.utils.videoSource('csi://0')
    # output = jetson.utils.videoOutput('rtp://192.168.1.101:1234')

    mqtt.publish(car.move, 'car/move')
    mqtt.publish(car.speed, 'car/speed/value')
    while True:

        # img = input.Capture()
        # output.Render(img)

        if mqtt.speed_value is not None:
            car.set_speed(mqtt.speed_value)

        if mqtt.autopilot_status == 'ON':
            led.turnOn(const.blue_LED_pin)
            image = car_camera.camera.read()
            res = loaded_model(preprocessor.preprocessImage(image).to(device=device).half())
            _, index = torch.max(res, 1)

            percentage = torch.nn.functional.softmax(res, dim=1)[0] * 100
            output = class_names[index[0]]
            print(class_names[index[0]], percentage[index[0]].item())

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
except KeyboardInterrupt:
    print('turn off')

    GPIO.cleanup()
    if car_camera is not None:
        car_camera.camera.release()
        car_camera.join()
    try:
        mqtt.disconnect()
        sys.exit(0)
    except SystemExit:
        os._exit(0)
finally:

    if car_camera is not None:
        car_camera.camera.release()
        car_camera.join()
    GPIO.cleanup()

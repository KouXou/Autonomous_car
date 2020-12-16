import utils.constants as const
import time
import paho.mqtt.publish as publish
from threading import Thread


class DistanceSensor(Thread):
    def __init__(self, gpio, distance=0):
        self.distance = distance
        self.gpio = gpio
        self.gpio.setup(const.trigger_pin, self.gpio.OUT)
        self.gpio.setup(const.echo_pin, self.gpio.IN)
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def send_trigger_pulse(self):
        self.gpio.output(const.trigger_pin, True)
        time.sleep(0.00001)
        self.gpio.output(const.trigger_pin, False)

    def wait_for_echo(self, value, timeout):
        count = timeout
        while self.gpio.input(const.echo_pin) != value and count > 0:
            count = count - 1

    def run(self):
        while True:
            self.send_trigger_pulse()
            self.wait_for_echo(True, 10000)
            start = time.time()
            self.wait_for_echo(False, 10000)
            finish = time.time()
            pulse_len = finish - start
            distance_cm = pulse_len / 0.000058

            publish.single("distance/value", distance_cm, hostname=const.mqtt_hostname)
            time.sleep(1)

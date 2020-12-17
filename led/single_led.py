import utils.constants as const
import time


class SingleLED:
    def __init__(self, gpio):
        self.gpio = gpio
        self.gpio.setup(const.green_LED_pin, self.gpio.OUT)
        self.gpio.setup(const.red_LED_pin, self.gpio.OUT)
        self.gpio.setup(const.blue_LED_pin, self.gpio.OUT)
        print('LED')

    def turnOn(self, led):
        self.gpio.output(led, True)

    def turnOff(self, led):
        self.gpio.output(led, False)

    def onStartCarLEDs(self):
        self.turnOn(const.green_LED_pin)
        time.sleep(1)
        self.turnOn(const.red_LED_pin)
        time.sleep(1)
        self.turnOn(const.blue_LED_pin)
        time.sleep(1)
        self.turnOff(const.green_LED_pin)
        self.turnOff(const.red_LED_pin)
        self.turnOff(const.blue_LED_pin)

    def flashing(self, led):
        try:
            while True:
                self.turnOn(led)
                time.sleep(1)
                self.turnOff(led)
                time.sleep(1)
        except KeyboardInterrupt:
            self.turnOff(led)

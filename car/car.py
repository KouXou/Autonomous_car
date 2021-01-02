import utils.constants as const


class Car:

    def __init__(self, gpio, speed, direction='forward', move='stop'):
        self.direction = direction
        self.move = move

        self.gpio = gpio
        self.speed = speed

        gpio.setup(const.backward_right_pin, self.gpio.OUT)
        self.gpio.setup(const.forward_left_pin, self.gpio.OUT)
        self.gpio.setup(const.backward_left_pin, self.gpio.OUT)
        self.gpio.setup(const.forward_right_pin, self.gpio.OUT)
        self.pw1 = self.gpio.PWM(const.pw1_pin, 1000)
        self.pw2 = self.gpio.PWM(const.pw2_pin, 1000)
        self.pw1.start(self.speed)
        self.pw2.start(self.speed)

    def go(self, backward_right, forward_left, backward_left, forward_right, direction, move):
        self.direction = direction
        self.move = move
        self.gpio.output(const.backward_right_pin, backward_right)
        self.gpio.output(const.forward_left_pin, forward_left)
        self.gpio.output(const.backward_left_pin, backward_left)
        self.gpio.output(const.forward_right_pin, forward_right)
        # print(self.direction)
        # print(self.turn)

    def set_speed(self, speed):
        self.speed = speed
        self.pw1.ChangeDutyCycle(self.speed)
        self.pw2.ChangeDutyCycle(self.speed)
        # print(self.speed)

    def set_speed_left(self, speed_left=20):
        self.pw2.ChangeDutyCycle(speed_left)

    def set_speed_right(self, speed_right=20):
        self.pw1.ChangeDutyCycle(speed_right)

    def backward(self):
        self.go(True, False, True, False, const.BWD, 'backward')

    def backwardLeft(self):
        self.go(False, False, True, False, const.BWD, 'backward_left')

    def backwardRight(self):
        self.go(True, False, False, False, const.BWD, 'backward_right')

    def forward(self):
        self.go(False, True, False, True, const.FWD, 'forward')

    def forwardLeft(self):
        self.go(False, True, False, False, const.FWD, 'forward_left')

    def forwardRight(self):
        self.go(False, False, False, True, const.FWD, 'forward_right')

    def stop(self):
        self.go(False, False, False, False, const.STOP, 'stop')

    def low_speed(self):
        self.set_speed(50)

    def medium_speed(self):
        self.set_speed(75)

    def high_speed(self):
        self.set_speed(100)

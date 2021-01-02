import paho.mqtt.client as mqtt
import utils.constants as const


class MqttCar:
    def __init__(self):
        self.state_field = None
        self.state = '-'
        self.autopilot_status = 'OFF'
        self.speed_value = 65
        self._establish_mqtt_connection()

    def start(self):
        self.client.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        print('Connected with result code ' + str(rc))
        # client.subscribe('car/move')
        client.subscribe('autopilot/status')
        client.subscribe('car/speed/value')

    def _on_log(self, client, userdata, level, buf):
        print('log: ', buf)

    def _on_message(self, client, userdata, msg):
        # print(msg.topic + ' ' + str(msg.payload))
        if msg.topic == 'autopilot/status':
            self.autopilot_status = str(msg.payload.decode('utf-8'))
            print(self.autopilot_status)
        elif msg.topic == 'car/speed/value':
            self.speed_value = int(msg.payload.decode('utf-8'))
            print(self.speed_value)

    def _establish_mqtt_connection(self):
        print('Trying to connect to MQTT server...')
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        # self.client.on_log = self._on_log
        self.client.on_message = self._on_message
        # self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe
        self.client.connect(const.mqtt_hostname, const.mqtt_port)

    def disconnect(self, args=None):
        self.client.disconnect()

    def on_publish(self, client, userdata, mid):
        print("Message published ")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("Subscription ok")

    def publish(self, msg, topic):
        self.client.publish(topic, msg, retain=False)

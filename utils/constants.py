# Drive Car Pins
forward_left_pin = 22
forward_right_pin = 24
backward_left_pin = 23
backward_right_pin = 17
pw1_pin = 12
pw2_pin = 13

# Direction Constants
FWD = 'forward'
BWD = 'backward'
STOP = 'stop'

# MQTT Constants
mqtt_hostname = '192.168.1.103'
mqtt_port = 1883
# mqtt_port = 9001

# Distance Sensor Constants
trigger_pin = 16
echo_pin = 20

# Camera Constants
camera_flip = 2
image_width = 224  # 336 #640 # 1280
image_height = 224  #480 #800
camera_fps = 30
camera_save_files_path = '/home/kostas/Autonomous_car/files/'
image_quality = 90  # from 0 to 100
# video_output_url = 'rtp://192.168.1.104:1234'
video_output_url = 'rtp://192.168.1.103:1234'

# Track Info
track_name = 'track5'

# LEDs Constants
green_LED_pin = 6
red_LED_pin = 4
blue_LED_pin = 9

# Mode Constants
record_dataset_mode = 1
record_stop_dataset_mode = 2
autopilot_mode = 3

# MQTT Topics
car_move_topic = 'car/move'
car_speed_topic = 'car/speed/value'
car_mode_topic = 'car/mode'
distance_topic = 'distance/value'
autopilot_topic = 'autopilot/status'

# Classification model constants
output_classes = ['forward', 'stop', 'forward_left', 'forward_right',
                  'speed_limit', 'speed_limit_end']

from machine import Pin, deepsleep, wake_reason, PIN_WAKE
import esp32
from umqtt.simple import MQTTClient
from ubinascii import b2a_base64
import time
import wlan
import mqtt
import camera
import urandom
import ujson

sensor = Pin(2, Pin.IN)
led = Pin(33, Pin.OUT)
flash = Pin(13, Pin.OUT)
esp32.wake_on_ext0(pin=sensor, level=esp32.WAKEUP_ANY_HIGH)

def wait_sensor_off():
    while sensor.value() == 1:
        time.sleep(0.5)

if wake_reason() != PIN_WAKE:
    print('Unjustified wakeup.')
    wait_sensor_off()
    deepsleep()

# Indicate successful power-on
led.value(0)
time.sleep(0.5)
led.value(1)

ssid, key = wlan.get_config()
status = wlan.connect(ssid, key, led)
if not status:
    if status is None:
        led.value(0)
        time.sleep(10)
        deepsleep()
    else:
        print('Unable to connect WLAN. Abort process.')
        for i in range(10):
            time.sleep(0.5)
            led.value(led.value() ^ 0x01)
            deepsleep()
            
urandom.seed(time.localtime()[5])
battery = urandom.randint(1,100)
print('battery %d' %battery)
config = mqtt.get_config()
broker,port,user,node,passwd,topic = config
client = MQTTClient(node, broker, user=user, password=passwd, port=port, ssl=False)
client.connect()

try:
    camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
    camera.framesize(camera.FRAME_SVGA)
    camera.quality(10)
    flash.value(1)
    image = camera.capture()
    flash.value(0)
    camera.deinit()
    image_b64 = b2a_base64(image)
    str = ujson.dumps({
        'battery': battery,
        'image': image_b64})
    client.publish(topic, str)
    time.sleep(1)
except Exception as e:
    led.value(0)
finally:
    client.disconnect()
    while sensor.value() == 1:
        time.sleep(1)
    deepsleep()


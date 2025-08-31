from machine import Pin
from umqtt.simple import MQTTClient
import time
import wlan
import mqtt
import camera

interrupted = False

def sensor_interrupt(pin):
    interrupted = True

sensor = Pin(13, Pin.IN)
sensor.irq(handler=sensor_interrupt, trigger=Pin.IRQ_RISING)
led = Pin(33, Pin.OUT)
flash = Pin(2, Pin.OUT)

led.value(0)
time.sleep(0.5)
led.value(1)

ssid, key = wlan.get_config()
station = wlan.connect(ssid, key, led)

config = mqtt.get_config()
broker,port,user,node,passwd,topic = config
client = MQTTClient(node, broker, user=user, password=passwd, port=port, ssl=False)
client.connect()

try:
    while True:
        if interrupted:
            interrupted = False
            camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
            camera.framesize(camera.FRAME_SVGA)
            camera.quality(10)
            flash.value(1)
            image = camera.capture()
            flash.value(0)
            camera.deinit()
        time.sleep(1)
except Exception as e:
    led.value(0)
finally:
    client.disconnect()

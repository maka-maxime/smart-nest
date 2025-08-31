from machine import Pin
from umqtt.simple import MQTTClient
import time
import wlan
import mqtt

interrupted = False

def sensor_interrupt(pin):
    interrupted = True

sensor = Pin(2, Pin.IN)
sensor.irq(handler=sensor_interrupt, trigger=Pin.IRQ_RISING)
led = Pin(33, Pin.OUT)
flash = Pin(13, Pin.OUT)

led.value(0)
time.sleep(0.5)
led.value(1)

ssid, key = wlan.get_config()
station = wlan.connect(ssid, key, led)

config = mqtt.get_config()
broker,port,user,node,passwd,topic = config
client = MQTTClient(node, broker, user=user, password=passwd, port=port, ssl=False)
client.connect()

client.publish(topic, b'HELLO')

try:
    while True:
        if interrupted:
            interrupted = False
            flash.value(1)
            client.publish(topic, b'TRIGGER')
            flash.value(0)
        time.sleep(1)
except Exception as e:
    led.value(0)
finally:
    client.disconnect()

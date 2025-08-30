from machine import Pin
from umqtt.simple import MQTTClient
import time
import wlan
import mqtt

led = Pin(33, Pin.OUT)
led.value(0)
time.sleep(0.5)
led.value(1)

ssid, key = wlan.get_config()
station = wlan.connect(ssid, key, led)

config = mqtt.get_config()
broker,port,user,node,passwd,topic = config
client = MQTTClient(node, broker, user=user, password=passwd, port=port, ssl=False)
client.connect()
client.publish(topic, b'hello there')
client.disconnect()


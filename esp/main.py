from machine import Pin
import time
import wlan

led = Pin(33, Pin.OUT)
led.value(0)
time.sleep(0.5)
led.value(1)

ssid, key = wlan.get_config()
station = wlan.connect(ssid, key, led)
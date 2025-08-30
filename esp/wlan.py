from machine import Pin
import network
import time

def get_config():
    try:
        with open('wlan.cfg','r') as file:
            config = file.readlines()
            ssid = None
            key = None
            for line in config:
                if line.startswith('SSID='):
                    ssid = line.strip().split('=')[1]
                elif line.startswith('WPA2='):
                    key = line.strip().split('=')[1]
            if ssid and key:
                return ssid,key
            else:
                raise ValueError('Unable to fetch WLAN config.')
    except Exception as ex:
        print('Unable to read config file: ', e)
        return None,None

def connect(ssid, key, led):
    station = network.WLAN(network.STA_IF)
    station.active(False)
    station.active(True)
    nets = station.scan()
    try:
        if not station.isconnected():
            station.connect(ssid, key)   
            while not station.isconnected():
                time.sleep(0.5)
                led.value(led.value() ^ 0x01)
        led.value(1)
        status = station.status()
        if status == network.STAT_GOT_IP:
            print('ipv4: %s' %station.ifconfig()[0])
        else:
            for i in range(0,10):
                led.value(i & 0x01)
                time.sleep(0.1)    
    except OSError as e:
        print(e)
        led.value(0)
    finally:
        return station
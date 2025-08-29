import configparser
from time import localtime, strftime
import paho.mqtt.client as mqtt

config = configparser.ConfigParser()

def on_connect(client, userdata, flags, rc):
    topic = config.get('MQTT', 'Topic')
    client.subscribe(topic)
    print(f'Subscribed to topic: {topic}')

def on_message(client, userdata, msg):
    print('Message received')
    prefix = config.get('MQTT', 'ImageFolder')
    name = strftime('%Y-%m-%d-%H%M%S.jpg', localtime())
    name = prefix + '/' + name
    with open(name, 'wb') as f:
        f.write(msg.payload)

def main():

    config.read('config.ini')
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(config.get('MQTT', 'Broker'), config.getint('MQTT', 'Port'))
    client.loop_start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print('\n')
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    main()
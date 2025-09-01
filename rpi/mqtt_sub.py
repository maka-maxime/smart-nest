#!/usr/bin/python3
import base64
import configparser
from io import BytesIO
import paho.mqtt.client as mqtt
from PIL import Image
import socket
from time import localtime, strftime
import json

config = configparser.ConfigParser()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def center_crop(image):
    image.convert("RGB")
    width, height = image.size
    min_dimension = min(width, height)
    left = (width - min_dimension) // 2
    right = left + min_dimension
    top = (height - min_dimension) // 2
    bottom = top + min_dimension
    return image.crop((left, top, right, bottom))

def create_thumbnail(byte_image, size=(256,256)):
    input_stream = BytesIO(byte_image)
    output_stream = BytesIO()
    image = Image.open(input_stream)
    cropped = center_crop(image).resize(size, Image.LANCZOS)
    cropped.save(output_stream, format="JPEG")
    return output_stream.getvalue()

def on_connect(client, userdata, flags, rc):
    topic = config.get('MQTT', 'Topic')
    client.subscribe(topic)
    print(f'Subscribed to topic: {topic}')

def on_message(client, userdata, msg):
    print('Message received')
    timestamp = localtime()

    data_json = json.loads(msg.payload)
    image_bytes = base64.b64decode(data_json['image'])
    battery = data_json['battery']
    print(f'battery: {battery}')
    thumbnail = create_thumbnail(image_bytes)
    # N0 for 'Nest 0', subject to change if more than one nest
    #   and fetch nest-id from topic
    battery_bytes = base64.b64encode(f'{battery:03}'.encode('utf-8'))
    print(battery_bytes)
    sock.sendall(battery_bytes)
    name = strftime('N0-%Y-%m-%d-%H%M%S.jpg', timestamp)
    image_id = base64.b64encode(name.encode('utf-8'))
    sock.sendall(image_id)
    print('Image ID sent.')
    sock.sendall(len(thumbnail).to_bytes(4, 'big'))
    sock.sendall(thumbnail)
    print('Thumbnail sent.')
    sock.sendall(len(image_bytes).to_bytes(4, 'big'))
    sock.sendall(image_bytes)
    print('Image sent.')

def main():
    config.read('config.ini')

    stream_config = (config.get('ImageServer', 'Host'), config.getint('ImageServer','Port'))
    sock.connect(stream_config)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(config.get('MQTT', 'User'), config.get('MQTT', 'Passwd'))
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
        sock.close()

if __name__ == '__main__':
    main()
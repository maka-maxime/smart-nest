#!/usr/bin/python3
import configparser
from time import localtime, strftime
import paho.mqtt.client as mqtt
from PIL import Image
from io import BytesIO

config = configparser.ConfigParser()

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
    prefix = config.get('MQTT', 'ImageFolder')

    # generate name locally (subject to change)
    name = strftime('%Y-%m-%d-%H%M%S.jpg', localtime())
    image_name = prefix + '/' + name
    thumbnail_name = prefix + '/thumb-' + name

    thumbnail = create_thumbnail(msg.payload)

    # currently store images locally
    # TODO: send image and thumbnail to remote server
    with open(image_name, 'wb') as f:
        f.write(msg.payload)
    with open(thumbnail_name, 'wb') as f:
        f.write(thumbnail)    

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
#!/usr/bin/python3
import base64
import configparser
from io import BytesIO
from PIL import Image
import socket

config = configparser.ConfigParser()
config.read('config.ini')
host = '0.0.0.0'
port = config.getint('Network', 'ImagePort')
images_folder = config.get('Storage', 'Images')
thumbs_folder = config.get('Storage', 'Thumbnails')

listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listening_sock.bind((host, port))
listening_sock.listen(1)
print(f"Image server listening on {host}:{port}...")

service_sock, peer_address = listening_sock.accept()
print(f'Peer connected: {peer_address}')

while True:
    try:
        print('Waiting for data...')
        image_id64 = service_sock.recv(32)
        if len(image_id64) < 32:
            print('Peer disconnected.')
            break
        image_id = base64.b64decode(image_id64).decode('utf-8')

        for i in range(0,2):
            size_bytes = service_sock.recv(4)
            if not size_bytes:
                print('Peer disconnected before EOC.')
                break
        
            image_size = int.from_bytes(size_bytes, 'big')
            print(f'Data received: length of {image_size} bytes.')

            image_bytes = b""
            while len(image_bytes) < image_size:
                chunk = service_sock.recv(1024)
                if not chunk:
                    print('Peer disconnected before EOC.')
                    break
                image_bytes += chunk
        
            input_stream = BytesIO(image_bytes)
            image = Image.open(input_stream)
            if i == 0:
                name = f'{thumbs_folder}/{image_id}'
            else:
                name = f'{images_folder}/{image_id}'
            image.save(name, format='JPEG')
            print('Picture received and saved.')

    except Exception as e:
        print(f'Unable to receive data: {e}')
        break

service_sock.close()
listening_sock.close()
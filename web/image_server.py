#!/usr/bin/python3
import base64
import configparser
from io import BytesIO
from PIL import Image
import socket
import json

config = configparser.ConfigParser()
config.read('config.ini')
host = '0.0.0.0'
port = config.getint('Network', 'ImagePort')
images_folder = config.get('Storage', 'Images')
thumbs_folder = config.get('Storage', 'Thumbnails')
battery_file = config.get('Storage', 'Battery')

listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listening_sock.bind((host, port))
listening_sock.listen(1)
print(f"Image server listening on {host}:{port}")
service_sock = None
try:
    print('Waiting for a client...')
    while True:
        service_sock, peer_address = listening_sock.accept()
        print(f'Peer connected: {peer_address}')

        while True:
            try:
                print('Waiting for data...')
                battery_b64 = service_sock.recv(4)
                print(battery_b64)
                if len(battery_b64) < 4:
                    print('Peer disconnected.')
                    break
                battery = base64.b64decode(battery_b64).decode('utf-8')
                print(f'battery {battery}')
                with open(battery_file, 'w') as f:
                    f.write(battery)

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
except KeyboardInterrupt as e:
    print('\nStopping the server...', end='')
except Exception as e:
    print(e)
finally:
    if service_sock is not None:
        service_sock.close()
    listening_sock.close()
    print(' DONE.')
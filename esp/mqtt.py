from umqtt.simple import MQTTClient
import files

def get_config():
    broker = None
    port = 0
    user = None
    node = None
    passwd = None
    topic = None
    try:
        config = files.read_config('mqtt.cfg')
        for line in config:
            if line.startswith('BROKER='):
                broker = line.strip().split('=')[1].encode('utf-8')
            elif line.startswith('PORT='):
                port = int(line.strip().split('=')[1])
            elif line.startswith('USER='):
                user = line.strip().split('=')[1].encode('utf-8')
            elif line.startswith('NODE='):
                node = line.strip().split('=')[1].encode('utf-8')
            elif line.startswith('PWD='):
                passwd = line.strip().split('=')[1].encode('utf-8')
            elif line.startswith('TOPIC='):
                topic = line.strip().split('=')[1].encode('utf-8')
        if broker and port and user and node and passwd and topic:
            return (broker,port,user,node,passwd,topic)
        else:
            raise ValueError('Unable to fetch WLAN config.')
    except Exception as ex:
        print('Unable to read config file: ', ex)
        return (None,0,None,None,None,None)

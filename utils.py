import random
import json
import redis
import random
import time
from websocket import WebSocketException

mood_to_color = {
    1: (255, 255, 255),  # neutral: white
    2: (0, 0, 255),      # calm: blue
    3: (255, 255, 0),    # happy: yellow
    4: (128, 0, 128),    # sad: purple
    5: (255, 0, 0),      # angry: red
    6: (0, 128, 0),      # fearful: green
    7: (165, 42, 42),    # disgust: brown
    8: (255, 192, 203)   # surprised: pink
}

genre_to_strobe = {
    'blues': 0,
    'classical': 0,
    'country': 0,
    'disco': 10,
    'hiphop': 5,
    'jazz': 0,
    'metal': 20,
    'pop': 5,
    'reggae': 0,
    'rock': 10
}

def angle_to_dmx(angle):
    return 170 + angle * 80 / 180

def volume_to_dimmer(volume):
    return max(min(volume, 255), 0)

def bpm_to_speed(bpm):
    return max(min(bpm, 255), 0)

def json_dmx_parser(song):
    dmx_instructions = []
    
    for timestamp in song:
        dmx_data = {}
        dmx_data["timestamp"] = timestamp["timestamp"]
        dmx_data["DMX_1_Pan"] = angle_to_dmx(random.randint(-180, 180))
        dmx_data["DMX_2_Tilt"] = random.randint(0, 255)
        dmx_data["DMX_3_Dimmer"] = volume_to_dimmer(timestamp["volume"])
        dmx_data["DMX_4_Strobe"] = genre_to_strobe.get(timestamp["genre"], 0)
        dmx_data["DMX_5_Color"] = mood_to_color.get(timestamp["mood"].index(max(timestamp["mood"])), (255, 255, 255))
        dmx_data["DMX_6_Gobo"] = 0
        dmx_data["DMX_7_Pan_Fine"] = 0
        dmx_data["DMX_8_Tilt_Fine"] = 0
        dmx_data["DMX_9_Speed"] = bpm_to_speed(timestamp["bpm"])
        dmx_instructions.append(dmx_data)

    return dmx_instructions



def send_messages(package, ws):
        try:
            for message in package:
                if message['channel'] == 19 or  message['channel'] == 20 or  message['channel'] == 39 or  message['channel'] == 40:
                    continue  
                formated_message = f"CH|{message['channel']}|{message['value']}"
                ws.send(formated_message)
        except WebSocketException as e:
            print(f"WebSocket Handshake: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

def connect_to_redis():
    try:
        redis_client = redis.Redis(
            host= '130.61.189.22',
            port=6379,      
            db=0       
        )
        
        redis_client.ping()
        print("Connected to Redis!")
        return redis_client
    except redis.ConnectionError as e:
        print(f"Failed to connect to Redis: {e}")
        return None



def calculate_start_point(schedule):
    pass
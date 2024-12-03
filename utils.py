import random
import json
import redis
import random
import time
from websocket import WebSocketException

mood_to_color = {
    1: (236, 236, 236), # neutral: white
    2: (98, 154, 231),  # calm: blue
    3: (255, 221, 68),  # happy: yellow
    4: (43, 61, 149),   # sad: purple
    5: (214, 39, 40),   # angry: red
    6: (119, 17, 202),  # fearful: green
    7: (119, 227, 155), # disgust: brown
    8: (255, 127, 14)   # surprised: pink
}

genre_to_strobe = {
    'blues': 0,
    'classical': 0,
    'country': 0,
    'disco': 100,
    'hiphop': 50,
    'jazz': 0,
    'metal': 200,
    'pop': 50,
    'reggae': 0,
    'rock': 100
}

genre_to_gobo = {
    'blues': 61,
    'classical': 61,
    'country': 71,
    'disco': 51,
    'hiphop': 41,
    'jazz': 61,
    'metal': 41,
    'pop': 21,
    'reggae': 31,
    'rock': 11
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
        # dmx_data["timestamp"] = timestamp["timestamp"]
        dmx_data["DMX_1_Pan"] = angle_to_dmx(random.randint(-180, 180))
        dmx_data["DMX_2"] = 0
        dmx_data["DMX_3_Tilt"] = random.randint(0, 255)
        dmx_data["DMX_4"] = 0
        dmx_data["DMX_5_Speed"] = bpm_to_speed(timestamp["bpm"])
        dmx_data["DMX_6_Dimmer"] = volume_to_dimmer(timestamp["volume"])
        dmx_data["DMX_7_Strobe"] = genre_to_strobe.get(timestamp["genre"], 0)
        dmx_data["DMX_8_Color_R"] = mood_to_color.get(timestamp["mood"].index(max(timestamp["mood"])), (255, 255, 255))[0]
        dmx_data["DMX_9_Color_G"] = mood_to_color.get(timestamp["mood"].index(max(timestamp["mood"])), (255, 255, 255))[1]
        dmx_data["DMX_10_Color_B"] = mood_to_color.get(timestamp["mood"].index(max(timestamp["mood"])), (255, 255, 255))[2]
        dmx_data["DMX_11_Color_W"] = 0
        dmx_data["DMX_12"] = 0
        dmx_data["DMX_13"] = 0
        dmx_data["DMX_14_Spot_Dimmer"] = volume_to_dimmer(timestamp["volume"])
        dmx_data["DMX_15_Spot_Strobe"] = genre_to_strobe.get(timestamp["genre"], 0)
        dmx_data["DMX_16"] = 0
        dmx_data["DMX_17"] = genre_to_gobo.get(timestamp["genre"], 0)
        dmx_data["DMX_18"] = 0
        dmx_data["DMX_19"] = 0
        dmx_data["DMX_20"] = 0

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


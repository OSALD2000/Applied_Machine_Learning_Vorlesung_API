import random
import redis
import random
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
    'disco': 5,
    'hiphop': 2,
    'jazz': 0,
    'metal': 15,
    'pop': 5,
    'reggae': 0,
    'rock': 2
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

genre_to_wait_time = {
    'blues': 4,
    'classical': 4,
    'country': 4,
    'disco': 2,
    'hiphop': 3,
    'jazz': 4,
    'metal': 1,
    'pop': 3,
    'reggae': 4,
    'rock': 2
}

def angle_to_dmx(angle):
    return 170 + angle

def volume_to_dimmer(volume):
    return min(abs(volume)*10, 255)

def bpm_to_speed(bpm):
    return max(min((bpm+(bpm*0.35)), 255), 0)

def json_dmx_parser(song):
    dmx_instructions = []
    wait_time = 0
    pan_angle = random.randint(-180, 180)
    tilt_angle = random.randint(0, 255)
    
    for timestamp in song:
        dmx_data = {}

        pan_angle = random.randint(-180, 180)

        dmx_data["DMX_1_Pan"] = angle_to_dmx(pan_angle)
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
        dmx_data["DMX_14_Spot_Dimmer"] = 255
        dmx_data["DMX_15_Spot_Strobe"] = 0
        dmx_data["DMX_16"] = dimmer_spot
        dmx_data["DMX_17"] = genre_to_gobo.get(timestamp["g"], 0)
        dmx_data["DMX_18"] = 255
        dmx_data["DMX_19"] = 0
        dmx_data["DMX_20"] = 0

        dmx_data["DMX_21_Pan"] = angle_to_dmx(pan_angle)
        dmx_data["DMX_22"] = angle_to_dmx(pan_angle)
        dmx_data["DMX_23_Tilt"] = dmx_data["DMX_3_Tilt"]
        dmx_data["DMX_24"] = dmx_data["DMX_4"]
        dmx_data["DMX_25_Speed"] = dmx_data["DMX_5_Speed"]
        dmx_data["DMX_26_Dimmer"] = dimmer
        dmx_data["DMX_27_Strobe"] = dmx_data["DMX_7_Strobe"]
        dmx_data["DMX_28_Color_R"] = r
        dmx_data["DMX_29_Color_G"] = g
        dmx_data["DMX_30_Color_B"] = b
        dmx_data["DMX_31_Color_W"] = 0
        dmx_data["DMX_32"] = 0
        dmx_data["DMX_33"] = 0
        dmx_data["DMX_34_Spot_Dimmer"] = 255
        dmx_data["DMX_35_Spot_Strobe"] = 0
        dmx_data["DMX_36"] = dimmer_spot
        dmx_data["DMX_37"] = dmx_data["DMX_17"]
        dmx_data["DMX_38"] = 255
        dmx_data["DMX_39"] = 0
        dmx_data["DMX_40"] = 0
        
        dmx_instructions.append(dmx_data)
        wait_time += 1

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



def create_package(dmx_data):
    return [
    {"channel": 1, "value": int(dmx_data["DMX_1_Pan"])},
    {"channel": 2, "value": int(dmx_data["DMX_2"])},
    {"channel": 3, "value": int(dmx_data["DMX_3_Tilt"])},
    {"channel": 4, "value": int(dmx_data["DMX_4"])},
    {"channel": 5, "value": int(dmx_data["DMX_5_Speed"])},
    {"channel": 6, "value": int(dmx_data["DMX_6_Dimmer"])},
    {"channel": 7, "value": int(dmx_data["DMX_7_Strobe"])},
    {"channel": 8, "value": int(dmx_data["DMX_8_Color_R"])},
    {"channel": 9, "value": int(dmx_data["DMX_9_Color_G"])},
    {"channel": 10, "value": int(dmx_data["DMX_10_Color_B"])},
    {"channel": 11, "value": int(dmx_data["DMX_11_Color_W"])},
    {"channel": 12, "value": int(dmx_data["DMX_12"])},
    {"channel": 13, "value": int(dmx_data["DMX_13"])},
    {"channel": 14, "value": int(dmx_data["DMX_14_Spot_Dimmer"])},
    {"channel": 15, "value": int(dmx_data["DMX_15_Spot_Strobe"])},
    {"channel": 16, "value": int(dmx_data["DMX_16"])},
    {"channel": 17, "value": int(dmx_data["DMX_17"])},
    {"channel": 18, "value": int(dmx_data["DMX_18"])},
    {"channel": 19, "value": int(dmx_data["DMX_19"])},
    {"channel": 20, "value": int(dmx_data["DMX_20"])},
    {"channel": 21, "value": int(dmx_data["DMX_21_Pan"])},
    {"channel": 22, "value": int(dmx_data["DMX_22"])},
    {"channel": 23, "value": int(dmx_data["DMX_23_Tilt"])},
    {"channel": 24, "value": int(dmx_data["DMX_24"])},
    {"channel": 25, "value": int(dmx_data["DMX_25_Speed"])},
    {"channel": 26, "value": int(dmx_data["DMX_26_Dimmer"])},
    {"channel": 27, "value": int(dmx_data["DMX_27_Strobe"])},
    {"channel": 28, "value": int(dmx_data["DMX_28_Color_R"])},
    {"channel": 29, "value": int(dmx_data["DMX_29_Color_G"])},
    {"channel": 30, "value": int(dmx_data["DMX_30_Color_B"])},
    {"channel": 31, "value": int(dmx_data["DMX_31_Color_W"])},
    {"channel": 32, "value": int(dmx_data["DMX_32"])},
    {"channel": 33, "value": int(dmx_data["DMX_33"])},
    {"channel": 34, "value": int(dmx_data["DMX_34_Spot_Dimmer"])},
    {"channel": 35, "value": int(dmx_data["DMX_35_Spot_Strobe"])},
    {"channel": 36, "value": int(dmx_data["DMX_36"])},
    {"channel": 37, "value": int(dmx_data["DMX_37"])},
    {"channel": 38, "value": int(dmx_data["DMX_38"])},
    {"channel": 39, "value": int(dmx_data["DMX_39"])},
    {"channel": 40, "value": int(dmx_data["DMX_40"])},
]

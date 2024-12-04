import random
import redis
import random
from websocket import WebSocketException
import math
import logging
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define mood-to-color mapping
mood_to_color = {
    1: (236, 236, 236),  # neutral: white
    2: (98, 154, 231),   # calm: blue
    3: (255, 221, 68),   # happy: yellow
    4: (43, 61, 149),    # sad: purple
    5: (214, 39, 40),    # angry: red
    6: (119, 17, 202),   # fearful: green
    7: (119, 227, 155),  # disgust: brown
    8: (255, 127, 14)    # surprised: pink
}

ranges = [
    (1, 23, "weiß"),       
    (25, 49, "rot"),       
    (51, 74, "gelb"),      
    (76, 99, "halbblau"), 
    (101, 124, "grün"),    
    (126, 149, "bernsteinfarbe"),
    (151, 174, "violett"),
    (176, 199, "blau")
]


def euclidean_distance(color1, color2):
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)))

def get_closest_mood_color(input_color):
    closest_mood = None
    min_distance = float('inf')
    
    for mood, color in mood_to_color.items():
        distance = euclidean_distance(input_color, color)
        if distance < min_distance:
            min_distance = distance
            closest_mood = mood
    
    mood_index = closest_mood - 1
    return ranges[mood_index]

def color_to_value(input_color):
    closest_range = get_closest_mood_color(input_color)
    return closest_range


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
    'disco': 10,
    'hiphop': 5,
    'jazz': 0,
    'metal': 20,
    'pop': 5,
    'reggae': 0,
    'rock': 10
}

genre_to_gobo = {
    'blues': [61, 41, 21],
    'classical': [61, 11, 51],
    'country': [71, 31, 41],
    'disco': [51, 71, 61],
    'hiphop': [41, 51, 21],
    'jazz': [61, 31, 11],
    'metal': [41, 71, 61],
    'pop': [21, 41, 11],
    'reggae': [31, 21, 51],
    'rock': [11, 41, 61]
}

def angle_to_dmx(angle):
    return 170 + angle

def volume_to_dimmer(volume):
    return min(abs(volume)*10, 255)

def bpm_to_speed(bpm):
    return max(min((bpm-(bpm*0.5)), 3), 0)

def json_dmx_parser(song):
    dmx_instructions = []
    idx = 0
    gobo_idx = 0

    for song_chunk in song:
        dmx_data = {}

        pan_angle = int(random.random() * 45)
        
        mood_index = song_chunk["m"].index(max(song_chunk["m"]))
        mood_color = mood_to_color.get(mood_index + 1, (255, 255, 255))

        r = min(255, max(0, mood_color[0] + random.randint(-1, 1)))
        g = min(255, max(0, mood_color[1] + random.randint(-1, 1)))
        b = min(255, max(0, mood_color[2] + random.randint(-1, 1)))

        dimmer = volume_to_dimmer(song_chunk["vo"])
        dimmer_spot = int(random.random() * color_to_value(mood_to_color.get(song_chunk["m"].index(max(song_chunk["m"])), (255, 255, 255)))[1])
        
        if idx == 16:
            idx = 0
            gobo_idx += 1
            gobo_idx = 0 if gobo_idx == 3 else gobo_idx

        gobo = genre_to_gobo.get(song_chunk["g"], 0)[gobo_idx]

        dmx_data["DMX_1_Pan"] = angle_to_dmx(-pan_angle)
        dmx_data["DMX_2"] = 0
        dmx_data["DMX_3_Tilt"] = random.randint(0, 90)
        dmx_data["DMX_4"] = 0
        dmx_data["DMX_5_Speed"] = bpm_to_speed(song_chunk["b"])
        dmx_data["DMX_6_Dimmer"] = dimmer
        dmx_data["DMX_7_Strobe"] = genre_to_strobe.get(song_chunk["g"], 0)
        dmx_data["DMX_8_Color_R"] = r
        dmx_data["DMX_9_Color_G"] = g
        dmx_data["DMX_10_Color_B"] = b
        dmx_data["DMX_11_Color_W"] = 0
        dmx_data["DMX_12"] = 0
        dmx_data["DMX_13"] = 0
        dmx_data["DMX_14_Spot_Dimmer"] = 255
        dmx_data["DMX_15_Spot_Strobe"] = 0
        dmx_data["DMX_16"] = dimmer_spot
        dmx_data["DMX_17"] = gobo
        dmx_data["DMX_18"] = 255
        dmx_data["DMX_19"] = 0
        dmx_data["DMX_20"] = 0

        dmx_data["DMX_21_Pan"] = angle_to_dmx(pan_angle)
        dmx_data["DMX_22"] = 0
        dmx_data["DMX_23_Tilt"] = random.randint(0, 90)
        dmx_data["DMX_24"] = 0
        dmx_data["DMX_25_Speed"] = bpm_to_speed(song_chunk["b"])
        dmx_data["DMX_26_Dimmer"] = dimmer
        dmx_data["DMX_27_Strobe"] = genre_to_strobe.get(song_chunk["g"], 0)
        dmx_data["DMX_28_Color_R"] = r
        dmx_data["DMX_29_Color_G"] = g
        dmx_data["DMX_30_Color_B"] = b
        dmx_data["DMX_31_Color_W"] = 0
        dmx_data["DMX_32"] = 0
        dmx_data["DMX_33"] = 0
        dmx_data["DMX_34_Spot_Dimmer"] = 255
        dmx_data["DMX_35_Spot_Strobe"] = 0
        dmx_data["DMX_36"] = dimmer_spot
        dmx_data["DMX_37"] = gobo
        dmx_data["DMX_38"] = 255
        dmx_data["DMX_39"] = 0
        dmx_data["DMX_40"] = 0
        
        dmx_instructions.append(dmx_data)

        idx += 1
    return dmx_instructions



def send_messages_moving_heads(package, ws):
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

async def send_messages_leds(package):
    url = "http://192.168.171.27/win"
    
    brightness = package[5]['value']
    red = package[7]['value']
    green = package[8]['value']
    blue = package[9]['value']
    effect = random.randint(10, 90)
    effect_speed =  255 - package[4]['value']
    effect_intensity = package[6]['value']
    turn_on = brightness > 0
    
    params = {
        'T': turn_on,
        'A': brightness,  # Brightness (0-255)
        'R': red,         # Red (0-255)
        'G': green,       # Green (0-255)
        'B': blue,        # Blue (0-255)
        'FX': effect,     # Effect Index (0-101)
        'SX': effect_speed,  # Effect Speed (0-255)
        'IX': effect_intensity  # Effect Intensity (0-255)
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    logging.info("LED settings updated successfully.")
                else:
                    logging.warning(f"Failed to update LED settings. Status code: {response.status}")
        except aiohttp.ClientError as e:
            logging.error(f"Error while sending LED settings: {e}")

        

def connect_to_redis():
    try:
        redis_client = redis.Redis(
            host= '130.61.189.22',
            port=6379,      
            db=0       
        )
        redis_client.ping()
        logging.info("Connected to Redis.")
        return redis_client
    except redis.ConnectionError as e:
        logging.info(f"Failed to connect to Redis: {e}")        
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

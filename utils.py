#   {
#      "timestamp": "00:02:36.000-00:02:36.500",
#      "bpm": 120,
#      "genre": "ToDo",
#      "mood": [0.2, 0.1, 0.15, 0.2, 0.25, 0.1],
#      "frequency": [
#          {"frequency": 100, "amplitude": 0.7},
#          {"frequency": 200, "amplitude": 0.5},
#          {"frequency": 300, "amplitude": 0.4},
#          {"frequency": 400, "amplitude": 0.6}
#      ],
#      "volume": 83.0,
#      "instruments": [true, false, true, true, false]
#  }

# the Json file should parsed to DMX Instructions
# We will use the 8-Port modes for the DMX
# 8-Port mode:
#       Channel 1: Pan Controls the horizontal movement of the head
#       Channel 2: Tilt Controls the vertical movement of the head
#       Channel 3: Dimmer Controls the brightness of the light
#       Channel 4: Strobe Controls the speed of the strobe effect
#       Channel 5: Color Controls the color of the light
#       Channel 6: Gobo Controls the gobo pattern
#       Channel 7: Pan Fine 
#       Channel 8: Tilt Fine
# {
#     "timestamp": "00:02:36.000-00:02:36.500",
#     "values":[(channel, value)*20]        
# }
# 

import random

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
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

def json_dmx_parser(song):
    dmx_instructions = []
    
    for timestap in song:
        dmx_data = {}
        dmx_data["timestamp"] = timestap["timestamp"] 
        dmx_instructions.append(dmx_data)

    return dmx_instructions
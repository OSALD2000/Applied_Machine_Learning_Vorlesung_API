import random
import time
from websocket import create_connection, WebSocketException
from utils import json_dmx_parser, connect_to_redis, send_messages, load_song, calculate_start_point
import enum
import logging
import time
from datetime import datetime, timedelta, timezone

logging.basicConfig(level=logging.INFO)

    
redis_client = connect_to_redis()

CURRENT_SONG_STATE = SONG_STATE.STOP
OLD_SONG_STATE = SONG_STATE.STOP

CURRENT_SCHEDULE_STATE = STATE.NO_SONG
OLD_SCHEDULE_STATE = STATE.NO_SONG


while True:    
    try:
        schedule = redis_client.get("2:HeavyIsTheCrown:so")
        
        song = redis_client.get("2:using the song name")

        if schedule and schedule["st"] != "Stop":
            # get the package using the transformation function
            # Transfom the AI Json data to Pin instructions 
            package = [{"channel": number, "value": int (random.random() * 255)} for number in range(1, 41)]
            send_messages(package=package, ws=ws)
            time.sleep(0.5)

    except KeyboardInterrupt:
            package = [{"channel": number, "value": 0} for number in range(1, 41)]
            send_messages(package=package)
            break
    

def main(args):
    try:
        ws = create_connection("ws://127.0.0.1:9999/qlcplusWS")
        logging.info("Connected to QLC+ WebSocket")
        
        song = []
        idx = 0
        old_schedule = None
        
        while True:
            try:
                schedule = redis_client.get("2:HeavyIsTheCrown:so")
                
                if schedule == None or (schedule != None and schedule == old_schedule and CURRENT_SCHEDULE_STATE == STATE.NO_SONG):
                    logging.info("No schedule found")
                    time.sleep(0.5)
                    continue
                else:
                    CURRENT_SONG_STATE = SONG_STATE(schedule["st"])
                    CURRENT_SCHEDULE_STATE = STATE.NEW_SONG if (CURRENT_SCHEDULE_STATE == STATE.NO_SONG or CURRENT_SONG_STATE != OLD_SONG_STATE) else STATE.NO_CHANGE
                    logging.info(f"Schedule: {schedule}")
                
                if not (CURRENT_SCHEDULE_STATE == STATE.NO_CHANGE):
                    if CURRENT_SCHEDULE_STATE == STATE.NEW_SONG and OLD_SCHEDULE_STATE == STATE.NO_SONG:
                        song = load_song(schedule["name"], redis_client)
                    
                    if CURRENT_SONG_STATE == SONG_STATE.STOP:
                        continue
                    
                    while datetime.now(timezone.utc) < schedule['t']:
                        time.sleep(0.1)

                if idx >= len(song):
                        CURRENT_SCHEDULE_STATE = STATE.NO_SONG

                if CURRENT_SCHEDULE_STATE == STATE.NEW_SONG or CURRENT_SCHEDULE_STATE == STATE.START_AFTER_PAUSE:
                    idx = calculate_start_point(schedule)
                    
                package = json_dmx_parser(song[idx])
                
                send_messages(package, ws)
                
                idx += 1
                
                old_schedule = schedule
            
                OLD_SCHEDULE_STATE = CURRENT_SCHEDULE_STATE
                OLD_SONG_STATE = CURRENT_SONG_STATE
                
                time.sleep(0.2)
                        
            except KeyboardInterrupt:
                logging.info("Closing connection to QLC+ WebSocket")
                ws.close()
            
    except WebSocketException as  e1:
        logging.error(f"WebSocket error: {e1}")
        logging.info("Reconnecting to QLC+ WebSocket")
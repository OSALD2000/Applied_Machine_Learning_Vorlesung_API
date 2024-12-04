import time
import logging
import asyncio

from websocket import create_connection, WebSocketException
from utils import connect_to_redis, send_messages_moving_heads, create_package, send_messages_leds
from schedule import ScheduleManager, STATE
from datetime import datetime, timezone


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    ws = create_connection("ws://127.0.0.1:9999/qlcplusWS")
    logging.info("Connected to WebSocket.")
except WebSocketException as e:
    logging.error(f"WebSocket connection failed: {e}")
    exit(1)

redis_client = connect_to_redis()

schedule_manager = ScheduleManager(redis_client)

# Initial Schedule Example
schedule = {
    "t": time.time(),
    "song_name": "test",
    "c": 1,
    "d": 5,
    "st": "Play"
}

def create_reset_package():
    package =  [{"channel": number, "value": 0 } for number in range(1, 41)]
    
    package[0]['value'] = 150
    package[2]['value'] = 40
    package[20]['value'] = 150
    package[22]['value'] = 40
    
    return package

try:
    while True:
        schedule_manager.update(schedule=schedule)

        if schedule_manager.state in {STATE.NEW_SONG, STATE.START_AFTER_PAUSE}:
            sleep_time = time.time() - schedule_manager.current_schedule['t']
            if sleep_time < 0:
                time.sleep(abs(sleep_time))

        if schedule_manager.state not in {STATE.NO_SONG, STATE.END}:
            chunk = schedule_manager.get_chunk()
            package = create_package(chunk)
            logging.info(f"Current Index: {schedule_manager.idx}")
            send_messages_moving_heads(package=package, ws=ws)
            asyncio.run(send_messages_leds(package))
        
            time.sleep(0.45)

        if schedule_manager.state == STATE.END:
            logging.info("Song ended. Resetting channels.")
            send_messages_moving_heads(package=create_reset_package(), ws=ws)
            
            user_input_start = int(input("Enter new start index (0 to exit): "))
            user_input_end = int(input("Enter new end index: "))
            
            if user_input_start != 0:
                schedule = {
                    "t": time.time(),
                    "song_name": "test",
                    "c": user_input_start,
                    "d": user_input_end,
                    "st": "Play"
                }
            else:
                logging.info("Exiting song loop.")
                break

except KeyboardInterrupt:
    logging.info("Keyboard interrupt detected. Resetting channels and exiting.")
    send_messages_moving_heads(package=create_reset_package(), ws=ws)

except Exception as e:
    logging.error(f"Unexpected error: {e}")

finally:
    if ws:
        ws.close()
    logging.info("WebSocket connection closed.")

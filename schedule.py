import json
from utils import json_dmx_parser
import enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class STATE(enum.Enum):
    NEW_SONG = "NewSong"
    RUN = "Run"
    START_AFTER_PAUSE = "StartAfterPause"
    NO_CHANGE = "NoChange"
    NO_SONG = "NoSong"
    END = "End"
    
class ScheduleManager():
    def __init__(self, redis_client):
        self.has_song = False
        self.song_instructions = []
        self.idx = 0
        self.stop_idx = 0
        self.current_schedule = None
        self.old_schedule = None
        self.state = STATE.NO_SONG
        self.old_state = STATE.NO_SONG
        self.redis_client = redis_client
        self.song_stop = False
        self.songs = []
        
    def compare_schedules(self) -> bool:
        return self.current_schedule['song_name'] == self.old_schedule['song_name'] and \
                self.current_schedule['c'] == self.old_schedule['c']  and \
                self.current_schedule['d'] == self.old_schedule['d']
    
    def loud_song(self):
        self.songs.append(self.current_schedule['song_name'])
        key = f"2:{self.current_schedule['song_name']}"
        obj = self.redis_client.get(key)
        self.song_instructions = json_dmx_parser(json.loads(obj))

    def calculate_start_point(self):
        self.idx = int(self.current_schedule['c']) * 2

    def calculate_stop_point(self):
        self.stop_idx = int(self.current_schedule['d']) * 2
    
    
    def get_chunk(self):
        song_snippet = self.song_instructions[self.idx]
        self.idx += 1
        return song_snippet
    
    def reset_song_state(self, new_state):
        self.state = new_state
        self.idx = 0
        self.stop_idx = 0
        self.song = []
        self.has_song = False
        self.old_state = None

    def is_end_of_song(self):
        return (
            (self.state not in {STATE.NO_SONG, STATE.END} and self.idx >= len(self.song_instructions)) or 
            (self.idx != 0 and self.stop_idx != 0 and self.idx == self.stop_idx)
        )

    def prepare_new_song(self):
        self.loud_song()
        self.calculate_start_point()
        self.calculate_stop_point()
        self.has_song = True

    def update(self, schedule):
        self.old_state = self.state
        self.current_schedule = schedule
        
        if schedule is None:
            self.reset_song_state(STATE.NO_SONG)
            return
        
        if self.is_end_of_song():
            self.reset_song_state(STATE.END)
            return
        
        if (((self.old_schedule is not None or self.current_schedule['song_name'] in self.songs) and self.compare_schedules())) :
            self.state = STATE.NO_CHANGE
            return
        
        self.state = STATE.NEW_SONG
        self.old_schedule = self.current_schedule

        if not self.has_song:
            self.prepare_new_song()
            return
        
        if self.old_state in {STATE.NO_CHANGE, STATE.NEW_SONG}:
            if schedule["st"].upper() == "STOP":
                self.song_stop = True
                return
            
            if self.old_schedule["song_name"] != schedule["song_name"]:
                self.reset_song_state(STATE.NEW_SONG)
                return
            
            if self.old_schedule["st"].upper() == "STOP" and schedule["st"].upper() == "PLAY":
                self.state = STATE.START_AFTER_PAUSE
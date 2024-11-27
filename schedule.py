import json
from utils import json_dmx_parser
import enum

class STATE(enum.Enum):
    NEW_SONG = "NewSong"
    RUN = "Run"
    START_AFTER_PAUSE = "StartAfterPause"
    NO_CHANGE = "NoChange"
    NO_SONG = "NoSong"
    
class ScheduleManager():
    def __init__(self, redis_client):
        self.has_song = False
        self.song_instructions = []
        self.idx = 0
        self.current_schedule = None
        self.old_schedule = None
        self.state = STATE.NO_SONG
        self.old_state = STATE.NO_SONG
        self.redis_client = redis_client
        self.song_stop = False
        
    def compare_schedules(self) -> bool:
        return self.current_schedule['song_name'] == self.old_schedule ['song_name']
    
    def loud_song(self):
        key = f"2:{self.current_schedule['song_name']}:song_features"
        self.song_instructions = json_dmx_parser(json.loads(self.redis_client.get(key)))

    def calculate_start_point(self):
        self.idx = int(self.current_schedule['c']) * 2
    
    def get_chunk(self):
        song_snippet = self.song_instructions[self.idx]
        self.idx += 1
        return song_snippet
    
    def update(self, schedule):
        self.old_state = self.state
        self.current_schedule = schedule
        
        if schedule == None:
            self.has_song = False
            self.state = STATE.NO_SONG
            return
        
        if self.old_schedule != None and self.compare_schedules():
            self.state = STATE.NO_CHANGE
            return
        
        self.state = STATE.NEW_SONG
        self.old_schedule = self.current_schedule

        if not self.has_song:
            self.loud_song()
            self.calculate_start_point()
            self.has_song = True
            return
        
        if self.old_state == STATE.NO_CHANGE or self.old_state == STATE.NEW_SONG:
            if schedule["st"] == "STOP":
                self.song_stop = True
                return
            
            if self.old_schedule["name"] != schedule["name"]:
                self.state = STATE.NEW_SONG
                self.song = []
                self.idx = 0
                self.has_song = False
                self.old_schedule = None
                self.old_state = STATE.NO_SONG
                return
            
            if self.old_schedule["st"] == "Stop" and schedule["st"] == "Play":
                self.state = STATE.START_AFTER_PAUSE
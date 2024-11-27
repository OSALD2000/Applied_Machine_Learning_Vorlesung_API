import random
import time
from websocket import create_connection, WebSocketException
from utils import json_dmx_parser, connect_to_redis, send_messages, load_song, calculate_start_point
import enum
import logging
import time
from datetime import datetime, timedelta, timezone

class STATE(enum.Enum):
    NEW_SONG = "NewSong"
    RUN = "Run"
    START_AFTER_PAUSE = "StartAfterPause"
    NO_CHANGE = "NoChange"
    NO_SONG = "NoSong"
    
class Schedule():
    def __init__(self):
        self.has_song = False
        self.song = []
        self.idx = 0
        self.current_schedule = None
        self.old_schedule = None
        
        self.state = STATE.NO_SONG
        self.old_state = STATE.NO_SONG
        
        self.song_stop = False
        
    def compare_schedules(self) -> bool:
        pass
    
    def loud_song(self):
        pass
    
    def calculate_start_point(self):
        pass
    
    def update(self, schedule, ws):
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
        self.current_schedule = schedule
        
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
                return
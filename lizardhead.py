# The Cave
# so many runs through the lizard head will start 'gorby rage' mode goals to be determined

import procgame
import locale
import logging
import random

from procgame import *
#from hand_of_fate import *


base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/GrandLizard/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class lizardhead(game.Mode):

    def __init__(self, game, priority):
        super(lizardhead, self).__init__(game, priority)
        self.log = logging.getLogger('gl.lizardhead')
        self.lamps = ['indyI','indyN','indyD','indyY']
        self.ramp_count = 0
        self.chuteTime = 0
        self.score_amnt = 500

    def reset(self):
        self.ramp_count = 0
        self.reset_lamps()
        
    def mode_started(self):
        print("LizardHead mode Started")
        #update lamp states
        self.update_lamps()
    
    def mode_stopped(self):
        pass
        #save player specific data

    def mode_tick(self):
        pass

    def clear(self):
        self.layer = None
        
    def sw_rampTongue_active(self, sw):
        
        #if (self.game.switches.rightChutetoTop.hw_timestamp-self.chuteTime)>500:
            self.ramp_count+=1
            #self.game.set_status("RAMP Count")
            self.game.set_status(str(self.ramp_count), row=1, align='left')
            self.game.score(self.score_amnt)
            self.chuteTime = self.game.switches.rightChutetoTop.hw_timestamp
            
    def reset_lamps(self):
        for i in range(len(self.lamps)):
            self.game.effects.drive_lamp(self.lamps[i],'off')
            
    
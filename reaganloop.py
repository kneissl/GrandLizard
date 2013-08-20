# The Cave
# so many runs through the right lane will start 'commie bomb' mode goals to be determined

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

class reaganloop(game.Mode):

    def __init__(self, game, priority):
        super(reaganloop, self).__init__(game, priority)
        self.log = logging.getLogger('gl.reaganloop')
        #self.lamps = ['indyI','indyN','indyD','indyY']
        self.loop_count = 0
        self.score_amnt = 50
        self.chuteTime = 0

    def reset(self):
        #self.reset_lamps()
        self.score_amnt = 0
        self.loop_count = 0
        
    def mode_started(self):
        print("Reagan loop mode Started")
        #update lamp states
        self.update_lamps()
    
    def mode_stopped(self):
        pass
        #save player specific data
        
    def update_lamps(self):
        pass

    def mode_tick(self):
        pass
    
    def sw_rightChutetoTop_active(self, sw):
        if (self.game.switches.rightChutetoTop.hw_timestamp-self.chuteTime)>1000:
            self.loop_count+=1
            self.game.set_status("RIGHT  HOOK")
            if self.loop_count==1:
                self.game.set_status(str(self.loop_count) + "   Loop", row=1, align='right')
            else:
                self.game.set_status(str(self.loop_count) + "  Loops", row=1, align='right')
            self.game.score(self.score_amnt*self.loop_count)
            self.chuteTime = self.game.switches.rightChutetoTop.hw_timestamp
        print ("chute time:" + str(self.game.switches.rightChutetoTop.hw_timestamp))
            
    def clear(self):
        self.layer = None
            
    def reset_lamps(self):
        for i in range(len(self.lamps)):
            self.game.effects.drive_lamp(self.lamps[i],'off')
            
    
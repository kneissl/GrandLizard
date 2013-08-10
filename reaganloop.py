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
        self.lamps = ['indyI','indyN','indyD','indyY']

    def reset(self):
        self.reset_lamps()
        
    def mode_started(self):
        print("Cave mode Started")
        #update lamp states
        self.update_lamps()
    
    def mode_stopped(self):
        pass
        #save player specific data

    def mode_tick(self):
        pass

    def clear(self):
        self.layer = None
            
    def reset_lamps(self):
        for i in range(len(self.lamps)):
            self.game.effects.drive_lamp(self.lamps[i],'off')
            
    
# The Cave
# so many runs through the cave will start 'cave in' mode goals to be determined

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

class cave(game.Mode):

    def __init__(self, game, priority):
        super(cave, self).__init__(game, priority)
        self.log = logging.getLogger('gl.cave')
        self.lamps = ['turn10K','turn20K','turn40K']
        self.cave_value = 500
        self.caves_explored = 0
        self.droptarget_points = 350

    def reset(self):
        self.cave_value = 500
        self.droptarget_points = 350
        self.caves_explored = 0
        self.game.coils.threeBank.pulse(50)   
        self.reset_lamps()
        
    def mode_started(self):
        print("Cave mode Started")
        self.game.coils.threeBank.pulse(50)  
        self.update_lamps()
        
    def sw_threeBank1_active(self, sw):
        self.game.score(self.droptarget_points)
        if self.game.switches.threeBank2.is_active() and self.game.switches.threeBank3.is_active():
            self.increment_cave_value()
            self.game.coils.threeBank.pulse(50)
            
    def sw_threeBank2_active(self, sw):
        self.game.score(self.droptarget_points)
        if self.game.switches.threeBank1.is_active() and self.game.switches.threeBank3.is_active():
            self.increment_cave_value()
            self.game.coils.threeBank.pulse(50)
                    
    def sw_threeBank3_active(self, sw):
        self.game.score(self.droptarget_points)
        if self.game.switches.threeBank2.is_active() and self.game.switches.threeBank1.is_active():
            self.increment_cave_value()
            self.game.coils.threeBank.pulse(50)
            
    def sw_turnaround_active(self, sw):
        self.game.score(self.cave_value)
        self.caves_explored += 1
        if self.caves_explored==1:
            self.game.set_status(str(self.caves_explored)+" Cave  Explored")
        else:
            self.game.set_status(str(self.caves_explored)+" Caves Explored")
            
    def increment_cave_value(self):
        if self.cave_value==500:
            self.cave_value=1000
            self.game.lamps.turn10K.enable()
            self.game.set_status("CAVE  INCREASE")
        elif self.cave_value==1000:
            self.cave_value=2000
            self.game.lamps.turn20K.enable()
            self.game.set_status("CAVE  INCREASE")
        elif self.cave_value==2000:
            self.cave_value=4000
            self.game.lamps.turn40K.enable()
            self.game.set_status("CAVE  INCREASE")
    
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
            
    
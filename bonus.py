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

class bonus(game.Mode):

    def __init__(self, game, priority):
        super(bonus, self).__init__(game, priority)
        self.log = logging.getLogger('gl.bonus')
        self.singleslamps = ['one','two','three','four','five','six','seven','eight','nine']
        self.tenslamps = ['ten','twenty']
        self.multiplierlamps = ['twoX','threeX','fourX','fiveX','tenX']
        self.bonus_value = 0
        self.multiplier = 1

    def reset(self):
        self.bonus_value = 0
        self.multiplier = 1
        self.reset_lamps()
        
    def payout(self):
        pass
        
    def update_lamps(self):
        self.reset_lamps()
        tempbonus=0
        if self.bonus_value>=30:
            tempbonus=self.bonus_value
            self.bonus_value=29
        if self.bonus_value<10:
            for i in range(self.bonus_value):
                self.game.effects.drive_lamp(self.singleslamps[i],'on')
        if self.bonus_value>=10 and self.bonus_value<20:
            self.game.effects.drive_lamp(self.tenslamps[0],'on')
            for i in range(self.bonus_value-10):
                self.game.effects.drive_lamp(self.singleslamps[i],'on')
        if self.bonus_value>=20:
            for i in range(2):
                self.game.effects.drive_lamp(self.tenslamps[i],'on')
            for i in range(self.bonus_value-10):
                self.game.effects.drive_lamp(self.singleslamps[i],'on')
        for i in range(self.multiplier-1): # must be less than 5
            self.game.effects.drive_lamp(self.multiplierlamps[i],'on')
        if tempbonus>0:
            self.bonus_value=tempbonus
            
    def incrementBonus(self):
        self.bonus+=1
        self.update_lamps()
    
    def incrementMultiplier(self):
        if self.multiplier<5:
            self.multiplier+=1
            self.update_lamps()
            
    def mode_started(self):
        print("bonus mode Started")
        #update lamp states
        self.update_lamps()
    
    def mode_stopped(self):
        pass
        #save player specific data

    def mode_tick(self):
        pass

    def clear(self):
        self.layer = None
    
    def sw_leftOutlane_active(self, sw):
        self.bonus_value+=3
        self.update_lamps()
        
    def sw_rightOutlane_active(self, sw):
        self.bonus_value+=3
        self.update_lamps()
        
    def sw_topRightStandup_active(self, sw):
        self.bonus_value+=3
        self.update_lamps()
        
    def sw_leftReturnLane_active(self, sw):
        self.bonus_value+=1
        self.update_lamps()
        
    def sw_rightReturnLane_active(self, sw):
        self.bonus_value+=1
        self.update_lamps()
        
    def sw_turnaround_active(self, sw):
        self.bonus_value+=1
        self.update_lamps()
    
    def sw_rampTongue_active(self, sw):
        #self.bonus_value+=1
        self.update_lamps() 
    
    def reset_lamps(self):
        for i in range(len(self.tenslamps)):
            self.game.effects.drive_lamp(self.tenslamps[i],'off')
        for i in range(len(self.multiplierlamps)):
            self.game.effects.drive_lamp(self.multiplierlamps[i],'off')
        for i in range(len(self.singleslamps)):
            self.game.effects.drive_lamp(self.singleslamps[i],'off')
            
    
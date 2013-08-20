# The Cave
# so many runs through the cave will start 'cave in' mode goals to be determined

import procgame
import locale
import logging
import random
import time

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
        self.topBankLamps = ['bank20K', 'bank40K', 'bank60K', 'bank80K', 'bank100K']
        #self.cave_combo = ['turnaround','topRightStandup']
        
        self.rotateLamp = 5
        self.cave_value = 500
        self.caves_explored = 0
        self.droptarget_points = 350
        self.gametime=0
        self.cave_combo=False
        self.rightcombo_on=False
        self.combo_depth=0
        self.chuteTime = 0

    def reset(self):
        self.cave_value = 500
        self.rotateLamp = 5
        self.cave_combo=False
        self.rightcombo_on=False
        self.droptarget_points = 350
        self.caves_explored = 0
        self.combo_depth=0
        self.game.coils.threeBank.pulse(50)
        self.game.coils.fourBank1.pulse(150)
        self.game.coils.fourBank2.pulse(150)
        self.reset_TopBanks=False
        self.reset_lamps()
        
    def mode_started(self):
        print("Cave mode Started")
        self.game.coils.threeBank.pulse(50)
        self.game.coils.fourBank1.pulse(150)
        self.game.coils.fourBank2.pulse(150)
        self.reset_TopBanks=False
        self.update_lamps()
        self.lights_moving=True
        self.delay_move = self.delay(delay=1, handler=self.move_light)
    
    def move_light(self):
        self.rotateLamp+=1
        if self.rotateLamp>=5:
            self.rotateLamp=0
        self.update_lamps()
        #self.check_topdrops_down()
        if self.lights_moving==True:
            self.delay_move = self.delay(delay=1, handler=self.move_light)
        
    def update_lamps(self):
        for i in range(len(self.topBankLamps)):
            if i == self.rotateLamp:
                self.game.effects.drive_lamp(self.topBankLamps[i],'fast')
            else:
                self.game.effects.drive_lamp(self.topBankLamps[i],'off')
        
    def sw_threeBank1_active(self, sw):
        self.combo_end()
        self.game.score(self.droptarget_points)
        if self.game.switches.threeBank2.is_active() and self.game.switches.threeBank3.is_active():
            self.increment_cave_value()
            self.game.coils.threeBank.pulse(50)
            
    def sw_threeBank2_active(self, sw):
        self.combo_end()
        self.game.score(self.droptarget_points)
        if self.game.switches.threeBank1.is_active() and self.game.switches.threeBank3.is_active():
            self.increment_cave_value()
            self.game.coils.threeBank.pulse(50)
                    
    def sw_threeBank3_active(self, sw):
        self.combo_end()
        self.game.score(self.droptarget_points)
        if self.game.switches.threeBank2.is_active() and self.game.switches.threeBank1.is_active():
            self.increment_cave_value()
            self.game.coils.threeBank.pulse(50)
            
    def sw_topRightStandup_active(self, sw):
        if self.cave_combo==True and (time.time()-self.gametime)<2:
            if self.rightcombo_on==True:
                self.game.score(self.cave_value*3)
                self.game.set_status("TRIPLE  COMBO")
            else:
                self.game.set_status("*CAVE  COMBO*")    
            self.game.sound.play('bonus', loops=self.combo_depth-1)
            self.game.score(self.cave_value*3)
            print ("saved time:" + str(self.gametime))
            print ("combo depth:" + str(self.combo_depth))
           # if self.game.trough.num_balls_in_play>1:
            #    self.game.set_status("SUPER JACKPOT")
             #   self.game.run_modecall('multiball','super_jackpot')
              #  self.game.score(15000)
            
    def sw_rightChutetoTop_active(self, sw):
        if (self.game.switches.rightChutetoTop.hw_timestamp-self.chuteTime)>1000:
            self.chuteTime = self.game.switches.rightChutetoTop.hw_timestamp
            self.gametime=time.time()
            self.rightcombo_on=True
            self.cave_combo=False
            
    def combo_end(self):
        self.cave_combo=False
        self.rightcombo_on=False
        self.combo_depth=0
            
    def sw_fourBank1_active(self, sw):
        self.combo_end()
        self.check_topdrops_down()
        
    def sw_fourBank2_active(self, sw):
        self.combo_end()
        self.check_topdrops_down()
        
    def sw_fourBank3_active(self, sw):
        self.combo_end()
        self.check_topdrops_down()
        
    def sw_fourBank4_active(self, sw):
        self.combo_end()
        self.check_topdrops_down()
    
    def check_topdrops_down(self):
        topdroplist=['fourBank1','fourBank2','fourBank3','fourBank4']
        dropcount=0
        for i in range(len(topdroplist)):
            if self.game.switches[topdroplist[i]].is_active():
                dropcount+=1
        if dropcount>=1:
            self.cancel_delayed(self.delay_move)
            self.lights_moving=False
            if self.reset_TopBanks==False:
                self.delay_reset = self.delay(delay=5, handler=self.topdrop_reset)
                self.reset_TopBanks=True
        if dropcount>=4:
            if self.reset_TopBanks==True:
                self.cancel_delayed(self.delay_reset)
            self.topdrop_reset()
            self.game.score((self.rotateLamp+1)*20000)
            self.game.set_status("Killed   GUARDS")
            
            
    def topdrop_reset(self):
        self.game.coils.fourBank1.pulse(150)
        self.game.coils.fourBank2.pulse(150)
        self.lights_moving=True
        self.reset_TopBanks=False
        self.delay_move = self.delay(delay=1, handler=self.move_light)
  
    def sw_turnaround_active(self, sw):
        self.combo_depth=1
        if self.cave_combo==False and self.rightcombo_on==True and (time.time()-self.gametime)<2:
            self.game.sound.play('bonus')
            self.combo_depth=2
        self.cave_combo=True
        self.gametime=time.time()
        self.game.score(self.cave_value)
        self.caves_explored += 1
        if self.caves_explored==1:
            self.game.set_status(str(self.caves_explored)+" Cave  CRUSHd")
        else:
            self.game.set_status(str(self.caves_explored)+" Caves CRUSHd")
            
    def increment_cave_value(self):
        if self.cave_value==500:
            self.cave_value=1000
            self.game.lamps.turn10K.enable()
            self.game.set_status("CAVE   BOOST")
        elif self.cave_value==1000:
            self.cave_value=2000
            self.game.lamps.turn20K.enable()
            self.game.set_status("CAVE   BOOST")
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
            
    
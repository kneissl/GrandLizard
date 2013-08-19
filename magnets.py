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

class magnets(game.Mode):

    def __init__(self, game, priority):
        super(magnets, self).__init__(game, priority)
        self.log = logging.getLogger('gl.lizardhead')
        self.lamps = ['L','I','Z','A','R','D','leftMagnetLow','leftMagnetMid','leftMagnetTop','rightMagnetLow','rightMagnetMid','rightMagnetTop']
        self.rightclaw=3
        self.leftclaw=3
        self.L=False
        self.I=False
        self.Z=False
        self.A=False
        self.R=False
        self.D=False

    def reset(self):
        self.game.coils.rightMagnet.disable()
        self.game.coils.leftMagnet.disable()
        self.game.set_player_stats('rightClaw',self.rightclaw)
        self.game.set_player_stats('leftClaw',self.leftclaw)
        self.L=False
        self.I=False
        self.Z=False
        self.A=False
        self.R=False
        self.D=False
        self.reset_lamps()
        self.update_lamps()
        
    def mode_started(self):
        print("Magnet mode Started")
        self.rightclaw=self.game.get_player_stats('rightClaw')
        self.leftclaw=self.game.get_player_stats('leftClaw')
        #update lamp states
        self.update_lamps()
    
    def mode_stopped(self):
        self.game.set_player_stats('rightClaw',self.rightclaw)
        self.game.set_player_stats('leftClaw',self.leftclaw)
        self.game.coils.rightMagnet.disable()
        self.game.coils.rightMagnet.disable()
        #save player specific data
        
    def update_lamps(self):
        if self.L==True:
            self.game.lamps.L.enable()
        else:
            self.game.lamps.L.disable()
        if self.I==True:
            self.game.lamps.I.enable()
        else:
            self.game.lamps.I.disable()
        if self.Z==True:
            self.game.lamps.Z.enable()
        else:
            self.game.lamps.Z.disable()
        if self.A==True:
            self.game.lamps.A.enable()
        else:
            self.game.lamps.A.disable()
        if self.R==True:
            self.game.lamps.R.enable()
        else:
            self.game.lamps.R.disable()
        if self.D==True:
            self.game.lamps.D.enable()
        else:
            self.game.lamps.D.disable()
        if self.leftclaw==0:
            self.game.lamps.leftMagnetLow.disable()
            self.game.lamps.leftMagnetMid.disable()
            self.game.lamps.leftMagnetTop.disable()
        if self.leftclaw==1:
            self.game.lamps.leftMagnetLow.enable()
            self.game.lamps.leftMagnetMid.disable()
            self.game.lamps.leftMagnetTop.disable()
        if self.leftclaw==2:
            self.game.lamps.leftMagnetLow.enable()
            self.game.lamps.leftMagnetMid.enable()
            self.game.lamps.leftMagnetTop.disable()
        if self.leftclaw==3:
            self.game.lamps.leftMagnetLow.enable()
            self.game.lamps.leftMagnetMid.enable()
            self.game.lamps.leftMagnetTop.enable()
        if self.rightclaw==0:
            self.game.lamps.rightMagnetLow.disable()
            self.game.lamps.rightMagnetMid.disable()
            self.game.lamps.rightMagnetTop.disable()
        if self.rightclaw==1:
            self.game.lamps.rightMagnetLow.enable()
            self.game.lamps.rightMagnetMid.disable()
            self.game.lamps.rightMagnetTop.disable()
        if self.rightclaw==2:
            self.game.lamps.rightMagnetLow.enable()
            self.game.lamps.rightMagnetMid.enable()
            self.game.lamps.rightMagnetTop.disable()
        if self.rightclaw==3:
            self.game.lamps.rightMagnetLow.enable()
            self.game.lamps.rightMagnetMid.enable()
            self.game.lamps.rightMagnetTop.enable()
            
    def check_LIZ(self):
        if self.L==True and self.I==True and self.Z==True:
            self.leftclaw+=1
            self.L=False
            self.I=False
            self.Z=False
            self.update_lamps()
        if self.leftclaw>3:
            self.leftclaw=3
        
    def check_ARD(self):
        if self.A==True and self.R==True and self.D==True:
            self.rightclaw+=1
            self.A=False
            self.R=False
            self.D=False
            self.update_lamps()
        if self.rightclaw>3:
            self.rightclaw=3
        
    
    def sw_L_closed(self,sw):
        self.game.sound.play('3boink')
        self.game.score(500)
        self.game.lamps.L.enable()
        self.L=True
        self.check_LIZ()
        return True
    
    def sw_I_closed(self,sw):
        self.game.sound.play('3boink')
        self.game.score(500)
        self.game.lamps.I.enable()
        self.I=True
        self.check_LIZ()
        return True
    
    def sw_Z_closed(self,sw):
        self.game.sound.play('3boink')
        self.game.score(500)
        self.game.lamps.Z.enable()
        self.Z=True
        self.check_LIZ()
        return True
    
    def sw_A_closed(self,sw):
        self.game.sound.play('3boink')
        self.game.score(500)
        self.game.lamps.A.enable()
        self.A=True
        self.check_ARD()
        return True
    
    def sw_R_closed(self,sw):
        self.game.sound.play('3boink')
        self.game.score(500)
        self.game.lamps.R.enable()
        self.R=True
        self.check_ARD()
        return True

    def sw_D_closed(self,sw):
        self.game.sound.play('3boink')
        self.game.score(500)
        self.game.lamps.D.enable()
        self.D=True
        self.check_ARD()
        return True
    
    def check_rightMagnet(self):
        if self.rightclaw<1:
            self.game.coils.rightMagnet.disable()
    
    def check_leftMagnet(self):
        if self.leftclaw<1:
            self.game.coils.leftMagnet.disable()
    
    def sw_leftMagnet_closed(self, sw):
        if self.leftclaw>0:
            self.game.coils.leftMagnet.enable()
            self.leftclaw-=1
            self.update_lamps()
        
    def sw_rightMagnet_closed(self, sw):
        if self.rightclaw>0:
            self.game.coils.rightMagnet.enable()
            self.rightclaw-=1
            self.update_lamps()
        
    def sw_leftMagnet_open(self, sw):
        self.game.coils.leftMagnet.disable()
        
    def sw_rightMagnet_open(self, sw):
        self.game.coils.rightMagnet.disable()
    
    def sw_leftMagnet_closed_for_1s(self, sw):
        self.leftclaw-=1
        self.update_lamps()
        self.check_leftMagnet()
    
    def sw_leftMagnet_closed_for_2s(self, sw):
        self.leftclaw-=1
        self.update_lamps()
        self.check_leftMagnet()
    
    def sw_leftMagnet_closed_for_3s(self, sw):
        self.leftclaw-=1
        self.update_lamps()
        self.check_leftMagnet()
    
    def sw_rightMagnet_closed_for_1s(self, sw):
        self.rightclaw-=1
        self.update_lamps()
        self.check_rightMagnet()
    
    def sw_rightMagnet_closed_for_2s(self, sw):
        self.rightclaw-=1
        self.update_lamps()
        self.check_rightMagnet()
    
    def sw_rightMagnet_closed_for_3s(self, sw):
        self.rightclaw-=1
        self.update_lamps()
        self.check_rightMagnet()

    def mode_tick(self):
        pass

    def clear(self):
        self.layer = None
            
    def reset_lamps(self):
        for i in range(len(self.lamps)):
            self.game.effects.drive_lamp(self.lamps[i],'off')
            
    
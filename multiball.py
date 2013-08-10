import procgame
import pinproc
import locale
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/GrandLizard/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Multiball(game.Mode):

    def __init__(self, game, priority):
        super(Multiball, self).__init__(game, priority)
        self.balls_needed = 3
        self.balls_in_play = 1
        self.lock_ball_score = 5000
        self.jackpot_base = 25000
        self.jackpot_boost = 2000
        self.jackpot_value = self.jackpot_base
        self.jackpot_x = 1
        self.jackpot_collected = 0
        self.jackpot_lamps = ['arkJackpot','stonesJackpot','grailJackpot']
        self.super_jackpot_enabled = False
        self.super_jackpot_value = 10000
        self.next_ball_ready = False
        self.lock_lit = False
        self.mode_running = False
        self.balls_locked = 0
        self.multiball_running = False
        
        self.reset()
            
    def reset(self):
        self.update_lamps()

    def mode_started(self):
        #set player stats for mode
        self.balls_locked = self.how_many_locked()
        self.lock_lit = self.game.get_player_stats('lock_lit')
        self.mode_running = self.game.get_player_stats('mode_running')
        self.balls_locked = self.game.get_player_stats('balls_locked')
        self.multiball_running = self.game.get_player_stats('multiball_running')

    def mode_tick(self):
        pass


    def lock_ball(self):
        if self.lock_lit==False:
            self.delayed_name = self.delay(delay=0.25, handler=self.eject_lock)
        if self.multiball_running==True:
            self.game.coils.lockupEject.pulse(15)
            return
        self.balls_locked = self.how_many_locked()
        self.game.score(self.lock_ball_score)
        
        if self.balls_locked==3:
            self.game.coils.lockupEject.pulse(15)
            self.balls_locked -= 1
        else:
            self.game.set_status("Lock    "+str(self.balls_locked))
            self.launch_next_ball()
            
        self.game.set_player_stats('balls_locked',self.balls_locked)
            
    def launch_next_ball(self):
            self.game.set_status("Trough")
            self.game.trough.launch_balls(1,stealth=True) #set stealth to true so balls in play does not increase from lock
            self.next_ball_ready = True
            print("balls locked:"+ str(self.balls_locked))
            print("balls in play:" + str(self.balls_in_play))
            #self.game.ball_save.start(time=5)

    def multiball_start(self):
        #jackpot build
        #ball tracking

        #animations
        self.game.set_status("!MULTI  BALL!") #debug

        #self.game.lampctrl.play_show('ball_lock', repeat=False,callback=self.game.update_lamps)#self.restore_lamps
        self.game.score(self.lock_ball_score)

        #start multiball music
        #self.game.sound.play_music('multiball_play', loops=-1)

        self.balls_locked=0  
        self.game.set_player_stats('balls_locked',self.balls_locked)

        #empty idol
        #temp whilst no animation
        #self.delay(name='mt_loop', event_type=None, delay=3, handler=self.game.idol.empty)
                
        #turn on ball save
        #self.game.ball_save.start(num_balls_to_save=3,allow_multiple_saves=True,time=10)

        #start tracking
        #print ('start tracking')
        #self.multiball_tracking()
    
    def end_multiball(self):
        self.lock_lit = False
        self.num_locks_lit = 0
        self.jackpot(status='reset_jackpot')
        self.update_lamps()
    
    def is_active(self):
        return self.multiball_running



    def multiball_tracking(self):
        
        self.balls_in_play = self.game.trough.num_balls_in_play

        if self.balls_in_play==self.balls_needed:

            #debug
            #self.game.set_status("Tracking BallsInPlay:" + str(self.balls_in_play))
            if self.game.switches.multiBall3.is_active():
                self.game.coils.lockupEject.pulse(15)
            #track end
            if self.balls_in_play==1:
                self.multiball_running=False
                print ('stopping multiball')
                self.game.set_player_stats('multiball_running',self.multiball_running)
            
                #self.game.sound.stop_music()
                #self.game.sound.play_music('general_play', loops=-1)

                #light jackpot if not collected during multiball otherwise cancel
                if self.jackpot_collected==0:
                    self.jackpot('lit')
                    self.delay(name='jackpot_timeout', event_type=None, delay=10, handler=self.jackpot, param='cancelled')
                else:
                    self.jackpot('cancelled')

                self.cancel_delayed('mt_loop')

            else:
                self.delay(name='mt_loop', event_type=None, delay=0, handler=self.multiball_tracking)

        else:
            self.delay(name='mt_loop', event_type=None, delay=0, handler=self.multiball_tracking)


    def jackpot(self,status=None):

        #if self.multiball_running:
            if status=='lit':
                self.game.coils.lockupFlasher.disable()
                self.game.coils.eyesFlasher.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)

            elif status=='unlit':
                self.game.coils.lockupFlasher.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
                #self.game.coils.divertorHold.disable()
                #self.game.coils.topLockupHold.disable()
            elif status=='made':
                self.game.coils.eyesFlasher.disable()
                #self.game.lampctrl.play_show('jackpot', repeat=False,callback=self.game.update_lamps)#self.restore_lamps

   #            anim = dmd.Animation().load(game_path+"dmd/lock_animation_"+self.balls_locked+".dmd")
   #            self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,frame_time=2)
#                   self.animation_layer.add_frame_listener(-1,self.clear)
#                   self.layer = dmd.GroupedLayer(128, 32, [self.animation_layer,self.text_layer])

                #self.jackpot_x = self.game.idol.balls_in_idol+1

                self.game.score(self.jackpot_value*self.jackpot_x)
                self.jackpot_collected+=1
                #self.game.effects.drive_lamp(self.jackpot_lamps[self.jackpot_collected],'smarton')
                if self.jackpot_collected==3:
                    self.super_jackpot()
                else:
                    self.delay(name='reset_jackpot', event_type=None, delay=1, handler=self.jackpot, param='unlit')

            elif status=='cancelled':
                self.game.coils.flasherLiteJackpot.disable()
                self.game.coils.eyesFlasher.disable()
                #self.game.coils.divertorHold.disable()
                #self.game.coils.topLockupHold.disable()
                
    def super_jackpot(self):
        self.game.coils.flasherSuperJackpot.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
        self.super_jackpot_enabled = True

    def lock_enabled(self):
        #temp add in rules for enabling lock
        self.lock_lit = True;
        #self.game.idol.lock_lit=  self.lock_lit
        self.game.set_player_stats('lock_lit',self.lock_lit)

        self.update_lamps()

    def update_lamps(self):
        if self.lock_lit:
            #pass
            self.game.lamps.multiBallLow.schedule(schedule=0x000F000F, cycle_seconds=0, now=False)
            self.game.lamps.multiBallMid.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=False)
            self.game.lamps.multiBallTop.schedule(schedule=0x0FFF0FFF, cycle_seconds=0, now=False)
        else:
            #pass
            self.game.lamps.multiBallLow.disable()
            self.game.lamps.multiBallMid.disable()
            self.game.lamps.multiBallTop.disable()
            #self.game.effects.drive_lamp('multiBallLow','off')
            
    def delayed_clear(self,timer=2):
        self.delay(name='clear_delay', event_type=None, delay=timer, handler=self.clear)
        
    def clear(self):
        self.layer = None
        
    def sw_topRightStandup_active(self, sw):
        self.lock_enabled()
        if self.how_many_locked() > 0:
            self.multiball_running=True
            
        
    def sw_rightSpecialArrow_active(self, sw):
        self.lock_enabled()

    def sw_rampTongue_active(self, sw):
        if self.multiball_running:
            self.jackpot('lit')
            self.game.score(50000)
            
    def sw_multiBall1_active(self, sw):
        # play sound?
        self.delayed_name = self.delay(delay=1.5, handler=self.lock_ball)
        
    def eject_lock(self):
        self.game.coils.lockupEject.pulse(15)
        
    def sw_multiBall3_active(self, sw):
        if self.multiball_running==True:
            self.delayed_name = self.delay(delay=0.25, handler=self.eject_lock)
        
    
    def how_many_locked(self):
        if self.game.switches.multiBall1.is_active():
            return 3
        elif self.game.switches.multiBall2.is_active():
            return 2
        elif self.game.switches.multiBall3.is_active():
            return 1
        else:
            return 0
    



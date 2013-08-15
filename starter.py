# Setup logging first thing in case any of the modules log something as they start:
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

import sys
sys.path.append(sys.path[0]+'/../..') # Set the path so we can find procgame.  We are assuming (stupidly?) that the first member is our directory.
import procgame
import pinproc
from procgame import *
from threading import Thread
from random import *
from effects import *
from multiball import *
from reaganloop import *
from magnets import *
from cave import *
from scoredisplay import AlphaScoreDisplay
import string
import time
import locale
import math
import copy
import yaml

locale.setlocale(locale.LC_ALL, "") # Used to put commas in the score.
base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/GrandLizard/"
settings_path = game_path +"config/settings.yaml"
game_data_path = game_path +"config/game_data.yaml"
game_data_template_path = game_path +"config/game_data_template.yaml"
settings_template_path = game_path +"config/settings_template.yaml"
#dmd_path = "../../../shared/dmd/"
sound_path = game_path +"sound/"
music_path = "../../../shared/music/"
#font_tiny7 = dmd.font_named("04B-03-7px.dmd")
#font_jazz18 = dmd.font_named("Jazz18-18px.dmd")
lampshow_files = ["../../../shared/lamps/attract1.lampshow", \
                  "../../../shared/lamps/attract2.lampshow" \
                  ]
 
class Attract(game.Mode):
    """docstring for AttractMode"""
    def __init__(self, game):
        super(Attract, self).__init__(game, 1)
        #self.press_start = dmd.TextLayer(128/2, 7, font_jazz18, "center", opaque=True).set_text("Press Start")
        #self.proc_banner = dmd.TextLayer(128/2, 7, font_jazz18, "center", opaque=True).set_text("pyprocgame")
        #self.game_title = dmd.TextLayer(128/2, 7, font_jazz18, "center", opaque=True).set_text("Starter")
        #self.splash = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(dmd_path+'gl.dmd').frames[0])
        #self.layer = dmd.ScriptedLayer(128, 32, [{'seconds':2.0, 'layer':self.splash}, {'seconds':2.0, 'layer':self.proc_banner}, {'seconds':2.0, 'layer':self.game_title}, {'seconds':2.0, 'layer':self.press_start}, {'seconds':2.0, 'layer':None}])
        
        
    def mode_topmost(self):
        pass
    
    def mode_started(self):
        self.game.sound.register_music('background', music_path+"congas.WAV")
        self.game.sound.play_music('background', loops=-1)
        self.game.lampctrl.play_show(self.game.lampshow_keys[1], repeat=True)
        # Blink the start button to notify player about starting a game.
        self.game.lamps.gameOver.schedule(schedule=0x00ff00ff, cycle_seconds=0, now=False)
        #self.game.alpha_display.display(['abcdefghijklmnop', '1234567890123456'])
        #self.game.alpha_display.display([' !\'/\*#0 "?&%@$ ', ' 1234567 1234567'])
        #self.game.score_display.test()
        #self.delay(name='locked_balls', event_type=None, delay=2, handler=self.release_balls)
        self.game.score_display.set_ballmatch('11','00')
        self.game.score_display.set_text("Game  Over",0,justify='center',opaque=True,blink_rate=1,seconds=0)
        print("Trough is full?:" +str(self.game.trough.is_full()))
    # Turn on minimal GI lamps
    # Some games don't have controllable GI's (ie Stern games)
    #self.game.lamps.gi01.pulse(0)
    #self.game.lamps.gi02.disable()
    def change_lampshow(self):
        shuffle(self.game.lampshow_keys)
        self.game.lampctrl.play_show(self.game.lampshow_keys[0], repeat=True)
        self.delay(name='lampshow', event_type=None, delay=10, handler=self.change_lampshow)
    
    def release_balls(self):
        if self.game.switches.multiBall3.is_active():
            self.game.coils.lockupEject.pulse(15)
        if self.game.switches.outhole.is_active():
            self.game.coils.outhole.pulse(40)
    
    def mode_stopped(self):
        self.game.lampctrl.stop_show()
    
    def mode_tick(self):
        self.release_balls()
    
    # Enter service mode when the enter button is pushed.
    def sw_enter_active(self, sw):
        for lamp in self.game.lamps:
            lamp.disable()
        #self.game.modes.add(self.game.service_mode)
        return True
    
    def sw_exit_active(self, sw):
        return True
    
    # Outside of the service mode, up/down control audio volume.
    def sw_down_active(self, sw):
        volume = self.game.sound.volume_down()
        self.game.set_status("Volume Down : " + str(volume))
        return True
    
    def sw_up_active(self, sw):
        volume = self.game.sound.volume_up()
        self.game.set_status("Volume Up : " + str(volume))
        return True
    
    # Start button starts a game if the trough is full.  Otherwise it
    # initiates a ball search.
    # This is probably a good place to add logic to detect completely lost balls.
    # Perhaps if the trough isn't full after a few ball search attempts, it logs a ball
    # as lost?
    def sw_startButton_active(self, sw):
        print("Start Pressed - Trough:" +str(self.game.trough.is_full()))
        if self.game.trough.is_full():
            # Remove attract mode from mode queue - Necessary?
            self.game.modes.remove(self)
            # Initialize game
            self.game.start_game()
            # Add the first player
            self.game.add_player()
            # Start the ball.  This includes ejecting a ball from the trough.
            self.game.score_display.set_text("Grand Lizard",0,justify='center',opaque=True,blink_rate=0,seconds=2)
            
            self.game.start_ball()
        else:
            self.game.set_status("Ball Search!")
            self.game.ball_search.perform_search(5)
            self.release_balls()
        return True


class BaseGameMode(game.Mode):
    """docstring for AttractMode"""
    def __init__(self, game):
        super(BaseGameMode, self).__init__(game, 2)
        #self.tilt_layer = dmd.TextLayer(128/2, 7, font_jazz18, "center").set_text("TILT!")
        self.layer = None # Presently used for tilt layer
        self.ball_starting = True
    
    def mode_started(self):
        
        # Disable any previously active lamp
        for lamp in self.game.lamps:
            lamp.disable()
        
        self.game.sound.play_music('background', loops=-1)
        # Turn on the GIs
        # Some games don't have controllable GI's (ie Stern games)
        #self.game.lamps.gi01.pulse(0)
        #self.game.lamps.gi02.pulse(0)
        #self.game.lamps.gi03.pulse(0)
        #self.game.lamps.gi04.pulse(0)
        self.add_basic_modes()
        # Enable the flippers
        #self.game.enable_flippers(enable=True)
        self.game.coils.flipperEnable.enable()
        
        # Put the ball into play and start tracking it.
        # self.game.coils.trough.pulse(40)
        self.game.trough.launch_balls(1, self.ball_launch_callback)
        
        # Enable ball search in case a ball gets stuck during gameplay.
        #self.game.ball_search.enable()
        
        # Reset tilt warnings and status
        self.times_warned = 0;
        self.tilt_status = 0
        
        # In case a higher priority mode doesn't install it's own ball_drained
        # handler.
        self.game.trough.drain_callback = self.ball_drained_callback
        
        # Each time this mode is added to game Q, set this flag true.
        self.ball_starting = True
    
    def add_basic_modes(self):
        
        # High Priority Basic
        #self.effects = Effects(self.game)
        self.multiball = Multiball(self.game, 60)
        self.reaganloop = reaganloop(self.game, 35)
        self.cave = cave(self.game, 37)
        self.magnets = magnets(self.game, 90)
        self.lizardhead = lizardhead(self.game, 40)
        self.bonus = bonus(self.game)
        #self.game.modes.add(self.effects)
        self.game.modes.add(self.multiball)
        self.game.modes.add(self.reaganloop)
        self.game.modes.add(self.cave)
        self.game.modes.add(self.magnets)
        self.game.modes.add(self.bonus)
        self.game.modes.add(self.lizardhead)
    
    def ball_launch_callback(self):
        if self.ball_starting:
            self.game.ball_save.start_lamp()
        else:
            pass #self.game.set_status('!! Ball Saved !!')
            
    
    def mode_stopped(self):
        
        # Ensure flippers are disabled
        #self.game.enable_flippers(enable=False)
        self.game.coils.flipperEnable.disable()
        self.game.modes.remove(self.multiball)
        self.game.modes.remove(self.reaganloop)
        self.game.modes.remove(self.magnets)
        self.game.modes.remove(self.cave)
        self.game.modes.remove(self.bonus)
        self.game.modes.remove(self.lizardhead)
        
        # Deactivate the ball search logic son it won't search due to no
        # switches being hit.
        self.game.ball_search.disable()
    
    def ball_drained_callback(self):
        if self.multiball.is_active() and self.game.trough.num_balls_in_play==1:
            self.multiball.end_multiball()
        self.multiball.ball_drained()
        # End the ball
        if self.game.trough.num_balls_in_play == 0:
            self.finish_ball()
            self.reaganloop.reset()
            self.magnets.reset()
            self.cave.reset()
    
    def finish_ball(self):
        
        # Turn off tilt display (if it was on) now that the ball has drained.
        if self.tilt_status and self.layer == self.tilt_layer:
            self.layer = None
        
        self.end_ball()
        #print ('Ball:'+str(self.game.ball))
        #self.game.set_status('Ball     ' + str(self.game.ball))
       #self.game.alpha_display.display(['  GRAND  LIZARD ', ' 1234567 1234567'])

        #self.game.alpha_display.display([' GRAND   LIZARD ', ' 8ALL '+str(self.game.ball)+'  '+str(self.game.current_player().score)])
        self.game.set_status("finishball")
    
    def mode_tick(self):
        pass
        #self.game.alpha_display.display([' GRAND   LIZARD ', ' 8ALL '+str(self.game.ball)+'  '+str(self.game.current_player().score)])
        
    def end_ball(self):
        # Tell the game object it can process the end of ball
        # (to end player's turn or shoot again)
        self.game.end_ball()
    
    def sw_startButton_active(self, sw):
        if self.game.ball == 1:
            p = self.game.add_player()
            self.game.set_status(p.name + " added")
    
    def sw_shooterLane_open_for_1s(self,sw):
        if self.ball_starting:
            self.ball_starting = False
            ball_save_time = 10
            self.game.ball_save.start(num_balls_to_save=1, time=ball_save_time, now=True, allow_multiple_saves=False)
    #else:
    #    self.game.ball_save.disable()
    
    # Note: Game specific item
    # Set the switch name to the launch button on your game.
    # If manual plunger, remove the whole section.
    def sw_outhole_active(self, sw):

        self.game.coils.outhole.pulse(40)
        self.game.set_status("Trough")
     #   print ("balls in play" + str(self.game.trough.num_balls_in_play))
    #    def sw_shooterLane_active(self, sw):
    #        if self.game.switches.shooterR.is_active():
    #            self.game.coils.shooterR.pulse(50)
    
    
    # Allow service mode to be entered during a game.
    def sw_enter_active(self, sw):
        self.game.modes.add(self.game.service_mode)
        return True
    
    def sw_plubBobTilt_active(self, sw):
        if self.times_warned == 2:
            self.tilt()
        else:
            self.times_warned += 1
            #play sound
            #add a display layer and add a delayed removal of it.
            self.game.sound.play('service_exit')
            self.game.set_status("Tilt  Warn " + str(self.times_warned))

    def tilt(self):
        # Process tilt.
        # First check to make sure tilt hasn't already been processed once.
        # No need to do this stuff again if for some reason tilt already occurred.
        if self.tilt_status == 0:
            
            # Display the tilt graphic
            #self.layer = self.tilt_layer
            
            # Disable flippers so the ball will drain.
            #self.game.enable_flippers(enable=False)
            self.game.coils.flipperEnable.disable()
            
            # Make sure ball won't be saved when it drains.
            self.game.ball_save.disable()
            #self.game.modes.remove(self.ball_save)
            
            # Make sure the ball search won't run while ball is draining.
            self.game.ball_search.disable()
            
            # Ensure all lamps are off.
            for lamp in self.game.lamps:
                lamp.disable()
                
            #self.game.alpha_display.display([' TILTED  LIZARD ', '                '])
            
            # Kick balls out of places it could be stuck.
            #if self.game.switches.shooterR.is_active():
            #    self.game.coils.shooterR.pulse(50)
            #if self.game.switches.shooterL.is_active():
            #    self.game.coils.shooterL.pulse(20)
            self.tilt_status = 1
#play sound
#play video



class Game(game.BasicGame):
    """docstring for Game"""
    def __init__(self, machine_type):
        super(Game, self).__init__(machine_type)
        self.sound = procgame.sound.SoundController(self)
        self.lampctrl = procgame.lamps.LampController(self)
        self.settings = {}
    
    def save_settings(self):
        #self.write_settings(settings_path)
        super(Game, self).save_settings(settings_path)
        #pass

    def save_game_data(self):
        super(Game, self).save_game_data(game_data_path)

    def create_player(self, name):
        return mpcPlayer(name)
    
    def setup(self):
        """docstring for setup"""
        #setup score display
        self.score_display = AlphaScoreDisplay(self, 0)
        
        self.load_config(self.yamlpath)
        #self.load_settings(settings_path, user_settings_path)
        self.load_settings(settings_template_path, settings_path)
        
        self.setup_ball_search()
        self.load_game_data(game_data_template_path, game_data_path)
        
        # Instantiate basic game features
        self.effects = Effects(self)
        self.modes.add(self.effects)
        self.attract_mode = Attract(self)
        self.base_game_mode = BaseGameMode(self)

        # Note - Game specific item:
        # The last parameter should be the name of the game's ball save lamp
        self.ball_save = procgame.modes.BallSave(self, self.lamps.shootAgain, 'shooterLane')
        
        trough_switchnames = []
        # Note - Game specific item:
        # This range should include the number of trough switches for
        # the specific game being run.  In range(1,x), x = last number + 1.
        for i in range(1,4):
            trough_switchnames.append('ballTrough' + str(i))
        early_save_switchnames = ['rightOutlane', 'leftOutlane']
        
        # Note - Game specific item:
        # Here, trough6 is used for the 'eject_switchname'.  This must
        # be the switch of the next ball to be ejected.  Some games
        # number the trough switches in the opposite order; so trough1
        # might be the proper switchname to user here.
        self.trough = procgame.modes.Trough(self,trough_switchnames,'ballTrough1','ballFeed', early_save_switchnames, 'shooterLane', self.drain_callback)
        
        # Link ball_save to trough
        self.trough.ball_save_callback = self.ball_save.launch_callback
        self.trough.num_balls_to_save = self.ball_save.get_num_balls_to_save
        self.ball_save.trough_enable_ball_save = self.trough.enable_ball_save
        
        # Setup and instantiate service mode
        
        self.sound.register_sound('service_enter', sound_path+"menu_in.wav")
        self.sound.register_sound('service_exit', sound_path+"menu_out.wav")
        self.sound.register_sound('service_next', sound_path+"next_item.wav")
        self.sound.register_sound('service_previous', sound_path+"previous_item.wav")
        self.sound.register_sound('service_switch_edge', sound_path+"switch_edge.wav")
        self.sound.register_sound('service_save', sound_path+"save.wav")
        self.sound.register_sound('service_cancel', sound_path+"cancel.wav")
        self.sound.register_sound('bonus', sound_path+"bonus.wav")
        self.sound.register_sound('3boink', sound_path+"3bonks.wav")
        #self.service_mode = procgame.service.ServiceMode(self,100,font_tiny7,[])
        
        # Setup fonts
        #self.fonts = {}
        #self.fonts['tiny7'] = font_tiny7
        #self.fonts['jazz18'] = font_jazz18
        
        self.lampshow_keys = []
        key_ctr = 0
        for file in lampshow_files:
            key = 'attract' + str(key_ctr)
            self.lampshow_keys.append(key)
            self.lampctrl.register_show(key, file)
            key_ctr += 1
    
        # Instead of resetting everything here as well as when a user
        # initiated reset occurs, do everything in self.reset() and call it
        # now and during a user initiated reset.
        self.reset()

    def reset(self):
        # Reset the entire game framework
        super(Game, self).reset()
        
        # Add the basic modes to the mode queue
        self.modes.add(self.attract_mode)
        self.modes.add(self.ball_search)
        self.modes.add(self.ball_save)
        self.modes.add(self.trough)
        
        # Make sure flippers are off, especially for user initiated resets.
        #self.enable_flippers(enable=False)
        super(Game, self).coils.flipperEnable.disable()
    #self.game.coils.flipperEnable.disable();
    
    # Empty callback just incase a ball drains into the trough before another
    # drain_callback can be installed by a gameplay mode.
    def drain_callback(self):
        self.game.coils.outhole.pulse(40)
    
    def ball_saved_callback(self):
        self.game.set_status("*Ball Saved*")
    
    def ball_starting(self):
        super(Game, self).ball_starting()
        self.modes.add(self.base_game_mode)
    
    def ball_ended(self):
        self.modes.remove(self.base_game_mode)
        super(Game, self).ball_ended()
    
    def game_ended(self):
        super(Game, self).game_ended()
        self.modes.remove(self.base_game_mode)
        self.set_status("Game    Over")
        self.modes.add(self.attract_mode)
    
    def set_status(self, text, row=0, align='center'):
        #self.dmd.set_message(text, 3)
        if row==0:
            self.score_display.set_text(text,0,justify=align,opaque=True,blink_rate=0,seconds=2)
        else:
            self.score_display.set_text(text,0,justify=align,opaque=True,blink_rate=0,seconds=2)
        print(text)
    
    def set_player_stats(self,id,value):
            p = self.current_player()
            p.player_stats[id]=value

    def get_player_stats(self,id):
            p = self.current_player()
            return p.player_stats[id]
    
    def extra_ball(self):
        p = self.current_player()
        p.extra_balls += 1
    
    def setup_ball_search(self):
        # No special handlers in starter game.
        special_handler_modes = []
        self.ball_search = procgame.modes.BallSearch(self, priority=100, \
                                                     countdown_time=10, coils=self.ballsearch_coils, \
                                                     reset_switches=self.ballsearch_resetSwitches, \
                                                     stop_switches=self.ballsearch_stopSwitches, \
                                                     special_handler_modes=special_handler_modes)
class mpcPlayer(game.Player):

    def __init__(self, name):
        super(mpcPlayer, self).__init__(name)

                #create player stats
        self.player_stats = {}
        
        #set player stats defaults
        self.player_stats['status']=''
        self.player_stats['bonus_x']=1
        self.player_stats['friends_collected']=0
        self.player_stats['loops_completed']=0
        self.player_stats['loops_made']=0
        self.player_stats['loop_value']=1000000 #1M default
        self.player_stats['ramps_made']=0
        self.player_stats['adventure_letters_collected']=0
        self.player_stats['burps_collected']=0
        self.player_stats['soc_baskets_searched']=0
        self.player_stats['stones_collected']=0
        self.player_stats['current_mode_num']=0
        self.player_stats['mode_enabled']=False
        self.player_stats['mode_running'] = False
        self.player_stats['mode_status_tracking']= [0,0,0,0,0,0,0,0,0,0,0,0]
        self.player_stats['lock_lit'] = False                
        self.player_stats['multiball_running'] = False
        self.player_stats['balls_locked'] = 0
        self.player_stats['pit_value'] = 0
        self.player_stats['indy_lanes_flag']= [False,False,False,False]
        self.player_stats['indy_lanes_letters_spotted'] = 0
        self.player_stats['poa_flag']= [False,False,False,False,False,False,False,False,False]
        self.player_stats['adventure_letters_spotted']=0
        self.player_stats['last_mode_score']=0
        self.player_stats['get_the_idol_score']=0
        self.player_stats['castle_grunwald_score']=0
        self.player_stats['monkey_brains_score']=0
        self.player_stats['streets_of_cairo_score']=0
        self.player_stats['steal_the_stones_score']=0
        self.player_stats['leftClaw']=3
        self.player_stats['rightClaw']=3



def main():
    if len(sys.argv) < 2:
        print("Usage: %s <yaml>"%(sys.argv[0]))
        return
    else:
        yamlpath = sys.argv[1]
        if yamlpath.find('.yaml', 0) == -1:
            print("Usage: %s <yaml>"%(sys.argv[0]))
            return
    
    config = yaml.load(open(yamlpath, 'r'))
    machine_type = config['PRGame']['machineType']
    config = 0
    game = None
    try:
         game = Game(machine_type)
         game.yamlpath = yamlpath
         game.setup()
         game.run_loop()
    finally:
        del game

if __name__ == '__main__': main()

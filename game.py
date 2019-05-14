#!/usr/bin/python
# game.py
# Contains the main game loop code, and loads the menu scene
#
# (c) 2010 Alex Hixon <alex@alexhixon.com>

import pygame

from libscene import SceneManager
from settings import SettingManager
from menu import MenuScene
from highscores import HighScoreManager

class Game():
    def __init__ (self, width, height, default_scene=None):
        self.width = width
        self.height = height
        self.resolution = (width, height)
        self.running = True
        
        self.setup()
        if default_scene is not None:
            self.load_scene(default_scene)
        
        self.post_init()

    def post_init(self):
        # this can be overwritten by children classes
        pass

    def setup (self):
        pygame.init()
        self.set_man = SettingManager()
        self.hscore_man = HighScoreManager()
        
        self.fullscreen = self.set_man.setdict["fullscreen"]
        if self.fullscreen:
            self.screen = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.resolution)

        self.scene_man = SceneManager(self.screen)
        self.clock = pygame.time.Clock()

    def load_scene (self, scene):
        self.scene_man.current_scene = scene
        
    def loop (self):
        while self.running:
            if self.scene_man.process_events() == False:
                # returns false if we should be quitting
                return

            # see if running state has changed after an event
            if not self.running:
                break
            
            self.scene_man.render()
            pygame.display.update()
            self.clock.tick(60) # 60 fps

    def switch_fullscreen (self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            print "switching to fullscreen..."
            self.screen = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
        else:
            print "switching to window..."
            self.screen = pygame.display.set_mode(self.resolution)
        self.set_man.setdict["fullscreen"] = self.fullscreen
        self.set_man.save_settings()
        
    def quit (self):
        self.running = False
        pygame.quit()

if __name__ == "__main__":
    g = Game (640, 480)
    g.load_scene (MenuScene(g))
    g.loop()
    g.quit()
    
    print "No reverse on this, Smithy!"

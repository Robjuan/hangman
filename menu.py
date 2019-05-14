import random

import libscene
import hangman
import settings
import highscores
import pygame

class MenuScene(libscene.MenuScene):
    def __init__ (self, game):
        libscene.MenuScene.__init__ (self, game, 121, 160, 60, 8, {
            "normal": (238, 238, 236),
            "highlight": (46, 52, 54),
            "disabled": (85, 87, 83)
        }, "resources/menu/selectbg.png")
        
    def load_scene (self):
        self.add_escape_keybind ()
        self.add_background ("resources/menu/background.png", -3)
        
        self.add_button ("play", "Play", lambda x: self.load_next_scene (hangman.GameScene(self.game, True)))
        self.add_button ("highscores", "Highscores",lambda x: self.load_next_scene(highscores.ScoreScene(self.game)))
        self.add_button ("settings", "Settings", lambda x: self.load_next_scene (settings.SettingScene(self.game)))
        self.add_button ("credits", "Credits", lambda x: self.load_next_scene (CreditsScene(self.game)))
        self.add_button ("quit", "Quit", lambda x: self.game.quit())
        
        self.add_image ("logo", (22, 36), "resources/menu/logo.png")
        
    ########## CLOUD BELOW ###########

        # add animated clouds
        self.cloud_speeds = {
            "cloud1" : 1,
            "cloud2" : 2
        }
        
        self.add_object ("cloud1", "image", (random.randint(300, 600) * -1, random.randint(0, self.game.height/3)), {
                "path": "resources/menu/cloud1.png",
                "layer": -2
            }, {
                "render": lambda: self.move_cloud ("cloud1", self.cloud_speeds["cloud1"])
            })
        
        self.add_object ("cloud2", "image", (random.randint(300, 600) * -1, random.randint(0, self.game.height/3)), {
                "path": "resources/menu/cloud2.png",
                "layer": -2
            }, {
                "render": lambda: self.move_cloud ("cloud2", self.cloud_speeds["cloud2"])
            })
        
        # move the selection sprite into place
        self.move_selection ()
    
    def move_cloud (self, name, speed):
        obj = self.objects[name]
        x, y = obj.pos
        x += speed
        
        if x > self.game.width:
            x = random.randint(300, 600) * -1
            y = random.randint(0, self.game.height/3)
            self.cloud_speeds[name] = random.randint(1, 2)
        
        obj.pos = (x, y)

class CreditsScene(libscene.Scene):
    def load_scene(self):
        pygame.mixer.music.load("resources/game/credits.wav")
        self.add_prevscene_keybind()
        
        self.add_object ("background", "background", (0, 0), {
            "color": (0,0,0),
            "layer": -1
        })
        
        self.add_object ("credits", "textarea", (50, 500), {
            "fontfile": "resources/fonts/danielbd.ttf",
            "color": (255, 255, 255),
            "fontsize": 42,
            "text": "Authors\n\nAlex Hixon\nRob Swan\n\n\nSoftware Mavericks\n2010"
        }, {
            "render": self.move_credits
        })
        
        pygame.mixer.music.play(-1)
    
    def move_credits(self):
        x, y = self.objects["credits"].pos
        y -= 1
        if y < -400:
            y = 500
        
        self.objects["credits"].pos = (x, y)
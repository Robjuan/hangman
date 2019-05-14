import libscene
import phrases
from pygame.locals import *

class SettingManager():
    def __init__(self,filename="resources/config/settings.txt"):
        self.filename = filename       
        self.load_settings()
        
    def load_settings(self):
        f = open(self.filename,'r')
        self.setdict = {}
        for line in f:
            key,value = line.split('=')
            key = key.strip()
            value = value.strip()
            if value == "True":
                value = True
            elif value == "False":
                value = False
            self.setdict[key] = value
        f.close()

    def save_settings(self):        
        f = open(self.filename,'w')
        for key in self.setdict:
            writeline = str(key) + '=' + str(self.setdict[key]) + '\n'
            f.write(writeline)
        f.close()

class SettingScene(libscene.MenuScene):
    def __init__ (self, game):
        libscene.MenuScene.__init__ (self, game, 121, 160, 60, 8, {
            "normal": (238, 238, 236),
            "highlight": (46, 52, 54),
            "disabled": (85, 87, 83)
        }, "resources/menu/selectbg.png")
        
    def load_scene (self):
        self.add_prevscene_keybind()
        self.add_background ("resources/menu/generic_background.png", -3)
        
        self.add_button ("phrases", "Setup Phrases", lambda x: self.load_next_scene(phrases.PhraseScene(self.game)))
        self.add_button ("name", "Player Name",lambda x: self.load_next_scene(NameScene(self.game)))
        self.add_button ("difficulty","Difficulty: easy", self.swap_difficulty)
        
        fullscreen = "off"
        if not self.game.fullscreen:
            fullscreen = "on"

        self.difficulty = self.game.set_man.setdict["difficulty"]
        
        self.add_button ("fullscreen", "Fullscreen %s" % fullscreen, self.swap_fullscreen)
        
        self.add_button ("back", "< back", self.load_prev_scene)

    def swap_fullscreen (self, evt):
        self.game.switch_fullscreen()
        
        fullscreen = "off"
        if not self.game.fullscreen:
            fullscreen = "on"
        
        self.objects["fullscreen"].obj.update_text ("Fullscreen %s" % fullscreen)

    def swap_difficulty(self, event):
        if self.difficulty == "easy":
            self.difficulty = "medium"
            print self.game.set_man.setdict["difficulty"]
        elif self.difficulty == "medium":
            self.difficulty = "hard"
            print self.game.set_man.setdict["difficulty"]
        elif self.difficulty == "hard":
            self.difficulty = "easy"
            print self.game.set_man.setdict["difficulty"]
        self.game.set_man.setdict["difficulty"] = self.difficulty
        self.objects["difficulty"].obj.update_text("Difficulty: " + self.difficulty)
                         
        
class NameScene(libscene.MenuScene):
    def __init__(self,game):
        libscene.MenuScene.__init__ (self, game, 50, 320, 60, 8, {
            "normal": (238, 238, 236),
            "highlight": (46, 52, 54),
            "disabled": (85, 87, 83)
        }, "resources/menu/selectbg.png")
        
    def load_scene (self):
        self.game.set_man.load_settings()
        self.add_background("resources/menu/generic_background.png", -3)
        self.add_label ("name",(50,50),"resources/fonts/Harabara.ttf","Name:",(255,255,255))
        self.add_object ("namedisp","textbox",(60,90),{"color":(255,255,255),
                                                       "nocolor":(200,200,200),
                                                       "fontfile":"resources/fonts/Harabara.ttf",
                                                       "fontsize":36,
                                                       "text":self.game.set_man.setdict["name"]})
        self.set_focus(self.objects["namedisp"])
        self.add_button ("save","Apply",self.send_name)
        self.add_button ("main","< back",self.load_prev_scene)
        self.add_prevscene_keybind()

    def send_name(self,event):
        self.game.set_man.setdict["name"] = self.objects["namedisp"].obj.text
        self.game.set_man.save_settings()
        print "[setdict]", self.game.set_man.setdict

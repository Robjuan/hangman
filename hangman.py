import pygame
from pygame.locals import *
from libscene import Scene
import menu

import string
import random
from threading import Timer

class GameScene(Scene):
    def __init__ (self, game, timed=False, prev_scene=None):
        self.timed = timed
        Scene.__init__ (self, game, prev_scene=prev_scene)
    
    def load_scene (self):
        pygame.mixer.music.load("resources/game/scribble.wav")
        self.add_prevscene_keybind()
        
        self.add_background ("resources/game/background.jpg")
        
        self.add_object ("phrase", "label", (30, 60), {
            "fontsize": 38,
            "fontfile": "resources/fonts/danielbk.ttf",
        })
        
        self.add_object ("entry", "textbox", (300, 230), {
            "fontsize": 48,
            "fontfile": "resources/fonts/danielbd.ttf",
            "nocolor": (85, 87, 83),
        }, {
            "click": self.textbox_click,
            "submit": self.textbox_submit,
            "blur": self.textbox_blur,
            "keydown": self.textbox_keydown
        })
        
        self.set_focus (self.objects["entry"])
        
        self.add_object ("used", "label", (30, 400), {
            "fontsize": 32,
            "fontfile": "resources/fonts/danielbd.ttf",
        })

        self.add_object ("guessbtn", "label", (300, 285), {
            "fontsize": 24,
            "fontfile": "resources/fonts/danielbd.ttf",
            "fgcolor": (0,0,0),
            "nocolor": (85, 87, 83),
            "text": "guess"
        }, {
            "click": self.guess_click,
            "hover_on": self.hover_on,
            "hover_off": self.hover_off
        })

        self.add_object ("hintbtn", "label", (300, 325), {
            "fontsize": 24,
            "fontfile": "resources/fonts/danielbd.ttf",
            "fgcolor": (0,0,0),
            "nocolor": (85, 87, 83),
            "text": "hint"
        }, {
            "click": self.hint_click,
            "hover_on": self.hover_on,
            "hover_off": self.hover_off
        })
        
        self.add_object ("yourguess", "label", (300, 200), {
            "text": "Your guess:",
            "fontsize": 24,
            "fontfile": "resources/fonts/danielbd.ttf",
            "fgcolor": (0,0,0),
            "visible": False
        })
        
        self.tried_letters = []
        self.wrong_letters = []
        self.last_try = ""
        self.guessing = False

        self.letters_left = []
        self.lives = 6
        self.max_lives = 6
        self.lives_path = "resources/game/paper_%d.jpg"
        
        self.load_phrase()
        # XXX: remove; just for debugging
        print "phrase:", self.phrase
        
        # show a clock if we're in timed mode
        if self.timed:
            self.add_object ("clock", "label", (545, 20), {
                "fontsize": 32,
                "fontfile": "resources/fonts/Harabara.ttf",
                "fgcolor": (0,0,0),
                "text": "00:00"
            })
            
            self.timer_started = False
            self.timer = Timer(1, self.update_clock)
            self.ticks = 0
        
        # and start the game
        self.check_state()

    def hint_click(self, evt):
        letters = self.get_hint_letters()
        for letter in letters:
            self.tried_letters.append (letter)

        # start timer if use hits hint first
        if self.timed and not self.timer_started:
            self.timer_started = True
            self.timer.start ()
    
        self.lives -= 2
        
        if self.lives < 0:
            self.lives = 0
        
        self.check_state()

    def get_num_hint_letters(self):
        num_letters = 2
        if len(self.letters_left) == 1:
            return 0
        elif len(self.letters_left) == 2:
            num_letters = 1

        return num_letters

    def get_hint_letters (self):
        letters = []
        num_letters = self.get_num_hint_letters()

        # pick some letters to use
        use_letters = []
        for i in xrange(0, num_letters):
            letter = random.choice(self.letters_left)
            while letter in use_letters:
                letter = random.choice(self.letters_left)

            use_letters.append (letter)

        return use_letters

    def update_clock (self):
        self.ticks += 1
        
        min = 0
        sec = self.ticks
        if self.ticks > 60:
            min = self.ticks / 60
            sec = self.ticks % 60
            
        self.objects["clock"].obj.update_text ("%02d:%02d" % (min, sec))
                
        # start timer again only if we're in the game scene
        if self.game.scene_man.current_scene.__class__ == GameScene:
            self.timer = Timer (1, self.update_clock)
            self.timer.start()

    def hover_on (self, event):
        obj = event.target
        obj.obj.update_color ((60,60,60))
      
    def hover_off (self, event):
        obj = event.target
        obj.obj.update_color ((0,0,0))

    def guess_click (self, event):
        self.guessing = True
        self.objects["guessbtn"].visible = False
        self.objects["yourguess"].visible = True
        self.set_focus (self.objects["entry"])
    
    def check_state (self):
        # make sure guess button is visible
        if self.guessing:
            self.guessing = False
            self.objects["guessbtn"].visible = True
        
        self.dotted = self.get_dotted_phrase ()
        if self.dotted == self.phrase:
            # win game
            beats_time = self.game.hscore_man.beat_prev_time (self.game.set_man.setdict['name'], self.ticks)
            self.load_next_scene (WinScene(self.game, beats_time))
            self.game.hscore_man.update_score (self.game.set_man.setdict['name'], self.ticks)
            return

        if self.last_try != "" and self.last_try == self.dotted:
            self.lives -= 1

            if self.lives <= 0:
                # lose game
                self.load_next_scene (LoseScene(self.game,self.phrase))
                self.game.hscore_man.update_score (self.game.set_man.setdict['name'], self.ticks, win=False)
                return
                
        elif self.last_try == "":
            self.last_try = self.dotted

        # update GUI objects
        self.objects["background"].obj = pygame.image.load(self.lives_path % (self.max_lives - self.lives)).convert()
        self.objects["phrase"].obj.update_text(self.dotted)
        
        self.wrong_letters = []
        for letter in self.tried_letters:
            if letter.lower() not in self.phrase and letter in string.ascii_letters:
                self.wrong_letters.append (letter)
                
        self.objects["used"].obj.update_text(''.join (self.wrong_letters))
        self.objects["yourguess"].visible = False

        num_hints = self.get_num_hint_letters()
        if num_hints == 0:
            self.objects["hintbtn"].visible = False
        else:
            self.objects["hintbtn"].obj.update_text ("hint %d letters" % num_hints)
        
    def get_dotted_phrase(self, tried=None):
        if tried == None:
            tried = self.tried_letters
        
        self.letters_left = []
        dotted_phrase = ""
        for letter in self.phrase:
            if letter.lower() in tried:
                dotted_phrase += letter
            elif letter in string.ascii_letters:
                dotted_phrase += "_"
                if self.letters_left.count(letter) == 0:
                    self.letters_left.append (letter)
            else:
                dotted_phrase += letter

        return dotted_phrase
    
    def load_phrase (self):
        f = open('resources/config/phrases.txt')
        l = f.readlines()
        f.close()

        self.phrase = random.choice(l).strip()

    def textbox_click (self, evt):
        if evt.target.obj.text == "click me":
            evt.target.obj.update_text("")
    
    def textbox_blur (self, evt):
        if evt.target.obj.text == "":
            evt.target.obj.update_text("click me")
    
    def textbox_submit (self, evt):
        if len(evt.text) == 0:
            return

        if not self.guessing:
            letter = evt.text[0]
            evt.target.obj.update_text("")
            if letter in self.tried_letters:
                return
                
            self.tried_letters.append (letter)
            self.last_try = self.dotted
        else:
            if evt.text.strip().lower() == self.phrase.lower():
                # win after guessing
                self.load_next_scene (WinScene(self.game))
                return
            else:
                # lose a turn
                self.lives -= 1
                evt.target.obj.update_text("")
        
        # start time if necessary
        if self.timed and not self.timer_started:
            self.timer_started = True
            self.timer.start ()
        
        # clear out text box on guess
        evt.target.obj.update_text("")
        
        # play scribble, and then update score/time/check state
        pygame.mixer.music.play()
        self.check_state()

    def textbox_keydown (self, evt):
        obj = evt.target.obj
        if len(obj.text) > 1 and not self.guessing:
            obj.update_text(obj.text[0])

class WinScene(Scene):
    def __init__ (self, game, highscore):
        self.highscore = highscore
        Scene.__init__ (self, game)
        
    def load_scene(self):
        self.add_prevscene_keybind()
        self.add_background ("resources/game/background.jpg")
        
        self.add_object ("wintext", "label", (120, 80), {
            "text": "Congratulations,",
            "fontsize": 48,
            "fontfile": "resources/fonts/daniel.ttf",
        })
        
        self.add_object ("wintext2", "label", (200, 140), {
            "text": "you won!",
            "fontsize": 48,
            "fontfile": "resources/fonts/daniel.ttf",
        })
        
        self.add_object ("again", "label", (60, 400), {
            "text": "Play again",
            "fontsize": 42,
            "fontfile": "resources/fonts/danielbd.ttf",
        }, {
            "click": lambda x: self.game.load_scene(GameScene (self.game, timed=self.prev_scene.timed, prev_scene=self.prev_scene.prev_scene)),
            "hover_on": self.hover_on,
            "hover_off": self.hover_off
        })
        
        self.add_object ("return", "label", (430, 400), {
            "text": "Menu",
            "fontsize": 42,
            "fontfile": "resources/fonts/danielbd.ttf",
        }, {
            "click": self.load_prev_scene,
            "hover_on": self.hover_on,
            "hover_off": self.hover_off
        })
        
        if self.highscore:
            self.add_object ("highscore", "label", (200, 300), {
                "text": "New best time!",
                "fontsize": 32,
                "fontfile": "resources/fonts/danielbd.ttf",
            })
    
    def load_prev_scene (self, *kargs):
        # go back 2 scenes instead of 1
        dest = self.prev_scene.prev_scene
        print "[hangman.py] going to scene", dest
        self.game.load_scene (dest)
    
    def hover_on (self, event):
        obj = event.target
        obj.obj.update_color ((60,60,60))
      
    def hover_off (self, event):
        obj = event.target
        obj.obj.update_color ((0,0,0))

class LoseScene(Scene):
    def __init__(self,game,phrase):
        self.losephrase = phrase
        Scene.__init__(self,game)
    def load_scene(self):
        self.add_prevscene_keybind()
        self.add_background ("resources/game/background.jpg")
        
        self.add_object ("wintext", "label", (120, 80), {
            "text": "Bad luck, you lost.",
            "fontsize": 48,
            "fontfile": "resources/fonts/daniel.ttf",
        })
        
        self.add_object ("wintext2", "label", (150, 140), {
            "text": "The word was:",
            "fontsize": 48,
            "fontfile": "resources/fonts/daniel.ttf",
        })
        
        self.add_object ("wintext3", "label", (250, 240), {
            "text": str(self.losephrase),
            "fontsize": 48,
            "fontfile": "resources/fonts/daniel.ttf",
        })
        
        self.add_object ("again", "label", (60, 400), {
            "text": "Play again",
            "fontsize": 42,
            "fontfile": "resources/fonts/danielbd.ttf",
        }, {
            "click": lambda x: self.game.load_scene(GameScene (self.game, timed=self.prev_scene.timed, prev_scene=self.prev_scene.prev_scene)),
            "hover_on": self.hover_on,
            "hover_off": self.hover_off
        })
        
        self.add_object ("return", "label", (430, 400), {
            "text": "Menu",
            "fontsize": 42,
            "fontfile": "resources/fonts/danielbd.ttf",
        }, {
            "click": self.load_prev_scene,
            "hover_on": self.hover_on,
            "hover_off": self.hover_off
        })
    
    def load_prev_scene (self, *kargs):
        # go back 2 scenes instead of 1
        dest = self.prev_scene.prev_scene
        print "[hangman.py] going to scene", dest
        self.game.load_scene (dest)

    def hover_on (self, event):
        obj = event.target
        obj.obj.update_color ((60,60,60))
      
    def hover_off (self, event):
        obj = event.target
        obj.obj.update_color ((0,0,0))

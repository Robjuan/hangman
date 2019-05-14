# scene.py
# Allows for the creation of Scenes and SceneObjects for use with SceneManager.
#
# (c) 2010 Alex Hixon <alex@alexhixon.com>

import pygame
from pygame.locals import *

import gui

"""
Contains information about the object to be rendered.
Used for SceneManager.
"""
class SceneObject():
    def __init__ (self, name, pos, visible, obj, layer=0, events = {}):
        self.name = name
        self.pos = pos
        self.visible = visible
        self.obj = obj
        self.layer = layer
        self.events = events

    @property
    def surface (self):
        if type(self.obj) != pygame.Surface:
            return self.obj.image
        else:
            return self.obj

    def touches (self, pos):
        mx, my = pos
        ox, oy = self.pos

        width, height = self.size
        return mx >= ox and mx <= (ox + width) and my >= oy and my <= (oy + height)

    @property
    def size (self):
        return self.surface.get_size()

    def __cmp__ (self, other):
        return cmp(self.layer, other.layer)

    def __str__(self):
        return str("SceneObject %s @ (%d,%d), layer %d" % (self.name, self.pos[0], self.pos[1], self.layer))

class Scene:
    def __init__ (self, game, setup=True, prev_scene=None):
        self.objects = {}
        self.keybinds = []
        self.game = game
        self.prev_scene = prev_scene
        
        if setup:
            self.load_scene()

    def load_scene (self):
        # This function should be overwritten by children.
        pass

    def add_object (self, name, objtype, pos, params, events=None):
        color = (0, 0, 0)
        #bg_color = (255, 255, 255)
        bg_color = None
        no_color = (123, 123, 123)
        visible = True
        obj = None
        onclick = None
        size = (0, 0)
        layer = 0
        padding = (5, 5, 5, 5)
        
        text = ""
        font_size = 16
        font_face = None
        font_file = None
        
        if events is None:
            events = {}
        if params.has_key("visible"):
            visible = params["visible"]

        if params.has_key ("color"):
            color = params["color"]
        
        # fgcolor is an alias of color
        if params.has_key ("fgcolor"):
            color = params["fgcolor"]

        if params.has_key ("layer"):
            layer = params["layer"]
        
        if params.has_key ("text"):
            text = params["text"]
        
        if params.has_key ("fontsize"):
            font_size = params["fontsize"]
        
        if params.has_key ("fontface"):
            font_face = params["fontface"]
            
        if params.has_key ("fontfile"):
            font_file = params["fontfile"]
        
        if params.has_key ("bgcolor"):
            bg_color = params["bgcolor"]
        
        if params.has_key ("nocolor"):
            no_color = params["nocolor"]
        
        if params.has_key ("padding"):
            padding = params["padding"]
        
        if objtype == "background":
            if params.has_key("path"):
                obj = pygame.image.load(params["path"]).convert()
            else:
                obj = pygame.Surface(self.game.screen.get_size())
                obj.fill(color)

        elif objtype == "image":
            obj = gui.Box((0,0), color, path=params["path"])
        
        elif objtype == "textbox":
            if font_file is not None:
                font_face = font_file
            elif font_face is not None:
                font_face = pygame.font.match_font(font_face)
                
            obj = gui.Textbox (pygame.font.Font(font_face, font_size), color, bg_color, no_color, padding=padding, text=text)
        
        elif objtype == "textarea":
            if font_file is not None:
                font_face = font_file
            elif font_face is not None:
                font_face = pygame.font.match_font(font_face)
            
            # XXX: NO BG COLOR
            obj = gui.Textarea (pygame.font.Font(font_face, font_size), color, no_color, padding=padding, text=text)
        
        elif objtype == "label":
            if font_file is not None:
                font_face = font_file
            elif font_face is not None:
                font_face = pygame.font.match_font(font_face)
            
            obj = gui.Label (pygame.font.Font(font_face, font_size), color, text)
        else:
            raise TypeError("no such scene object type %s" % repr(objtype))

        self.objects[name] = SceneObject (name, pos, visible, obj, layer, events)

    def add_escape_keybind (self):
        self.add_keybind (K_ESCAPE, lambda x: self.game.quit())
        
    def add_prevscene_keybind (self):
        self.add_keybind (K_ESCAPE, self.load_prev_scene)
    
    def load_prev_scene (self, *kargs):
        print "[scene.py] going to scene", self.prev_scene
        self.game.load_scene (self.prev_scene)
        
    def load_next_scene (self, newscene):
        newscene.prev_scene = self
        print "[scene.py] going to scene", newscene
        self.game.load_scene (newscene)

    def add_keybind (self, key, event):
        self.keybinds.append ((key, event))

    def add_background (self, path, layer=-1):
        """
        Helper function that adds a background object to the scene object stack.
        """
        self.add_object ("background", "background", (0, 0), { "path": path, "layer": layer })

    def add_image (self, name, pos, path, event=None):
        """
        Helper function for easily adding images with a click event.
        """
        self.add_object (name, "image", pos, {"path": path}, {"click": event})

    def set_focus (self,obj):
        #xxx: should not access scene_man from scene.
        self.game.scene_man.set_focus(obj, None)
        
    def add_label (self,name,pos,font,text,color,fontsize=48,event=None,visible=True):
        """
        Helper function for adding labels.
        """
        self.add_object(name,"label",pos,{
            "text":text,
            "color":color,
            "fontfile":font,
            "fontsize":fontsize,
            "visible":visible
            },{"click":event}) 
                
                   
    def __str__ (self):
        return "%s with %d objects" % (self.__class__.__name__, len(self.objects))

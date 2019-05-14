# scenemanager.py
# Provides a simple API to have pygame and GUI objects attached to a 'scene',
# which can easily be rendered.
#
# (c) 2010 Alex Hixon <alex@alexhixon.com>

import pygame
import gui

class Event():
    pass
    
class BlurEvent(Event):
    def __init__ (self, target):
        self.target = target

class MouseDownEvent(Event):
    def __init__ (self, target, x, y):
        self.target = target
        self.x = x
        self.y = y

class MouseHoverEvent(MouseDownEvent):
    pass

class KeyDownEvent(Event):
    def __init__ (self, target, key):
        self.target = target
        self.key = key

class TextSubmitEvent(Event):
    def __init__ (self, target, text):
        self.target = target
        self.text = text

class SceneManager():
    def __init__(self, screen, scene=None):
        self.screen = screen
        self.current_scene = scene
        self.current_focus = None
        self.last_focus = None
        self.current_hover = None

    def render(self):
        """
        Blits all objects in the scene to the screen, ordered by layer.
        """
        # order by layer, and loop
        for sobj in sorted(self.get_objects()):
            # blit only visible objects
            if sobj.visible:
                self.screen.blit (sobj.surface, sobj.pos)
                
                if sobj.events.has_key("render") and sobj.events["render"] is not None:
                    sobj.events["render"]()

                if (type(sobj.obj) == gui.Textbox or type(sobj.obj) == gui.Textarea) and self.current_focus is not None:
                    sobj.obj.blink_cursor()
                    
    def get_objects(self):
        """
        Returns all the objects in the scene as an array.
        """
        return self.current_scene.objects.values()
    
    def get_binds(self):
        return self.current_scene.keybinds

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.last_focus = self.current_focus
                self.current_focus = None
                
                # see if we've clicked into anything
                mpos = pygame.mouse.get_pos()
                mx, my = mpos
                for sobj in self.get_objects():
                    if sobj.touches (mpos):
                        # and fire the object's event
                        if sobj.events.has_key ("click") and sobj.events["click"] is not None and sobj.visible:
                            sobj.events["click"](MouseDownEvent(sobj, mx, my))
                            
                        # work out if we're in a textbox
                        if (type(sobj.obj) == gui.Textbox or type(sobj.obj) == gui.Textarea) and not sobj.obj.disabled:
                            self.set_focus (sobj, (mx, my))
            
            # See if we've lost focus from textbox, if so, change back color thing
            self._swap_last_focused()
            
            if event.type == pygame.MOUSEMOTION:
                # find out what lives at the current (x, y)
                mpos = pygame.mouse.get_pos()
                mx, my = mpos
                hover_set_already = False
                
                for sobj in self.get_objects():
                    if sobj.touches (mpos):
                        # see if we're touching our last hover object
                        if self.current_hover is not None and not self.current_hover.touches (mpos):
                            # tell the old object we are no longer hovering
                            if self.current_hover.events.has_key("hover_off") and self.current_hover.events["hover_off"] is not None and sobj.visible:
                                self.current_hover.events["hover_off"](MouseHoverEvent (self.current_hover, mx, my))
                                self.current_hover = None
                        
                        if hover_set_already:
                            continue
                        
                        if not sobj.name == "background":
                            self.current_hover = sobj
                            hover_set_already = True
                        
                        if sobj.events.has_key ("hover_on") and sobj.events["hover_on"] is not None and sobj.visible:
                            sobj.events["hover_on"](MouseHoverEvent (sobj, mx, my))
                
    
            textchanged = False
            if event.type == pygame.KEYDOWN:
                # see if we have any textboxes that need attenting to
                if self.current_focus is not None:
                    if event.key == pygame.K_BACKSPACE:
                        #self.current_focus.obj.text = self.current_focus.obj.text[:-1]
                        self.current_focus.obj.text_backspace()
                        textchanged = True
                    elif event.key == pygame.K_DELETE:
                        self.current_focus.obj.text_delete()
                        textchanged = True
                    elif event.key == pygame.K_RETURN:
                        # don't add newline character to textbox only
                        # instead, notify object of submit event, and lose focus
                        if type(self.current_focus.obj) == gui.Textarea:
                            self.current_focus.obj.text_add("\n")
                            textchanged = True
                        
                        if self.current_focus.events.has_key('submit') and self.current_focus.events["submit"] != None:
                            retval = self.current_focus.events["submit"](TextSubmitEvent(self.current_focus, self.current_focus.obj.text))
                            if retval is True:
                                self._lose_current_focus()
                    
                    elif event.key == pygame.K_ESCAPE:
                        # just lose focus on escape
                        self._lose_current_focus()
                    
                    elif event.key == pygame.K_UP and type(self.current_focus.obj) == gui.Textarea:
                        self.current_focus.obj.move_cursor_up()
                        textchanged = True
                    
                    elif event.key == pygame.K_DOWN and type(self.current_focus.obj) == gui.Textarea:
                        self.current_focus.obj.move_cursor_down()
                        textchanged = True
                        
                    elif event.key == pygame.K_HOME and type(self.current_focus.obj) == gui.Textarea:
                        self.current_focus.obj.move_cursor_home()
                        textchanged = True
                    
                    elif event.key == pygame.K_LEFT and type(self.current_focus.obj) == gui.Textarea:
                        self.current_focus.obj.move_cursor_left()
                        textchanged = True
                        
                    elif event.key == pygame.K_RIGHT and type(self.current_focus.obj) == gui.Textarea:
                        self.current_focus.obj.move_cursor_right()
                        textchanged = True
                    
                    elif event.key == pygame.K_END and type(self.current_focus.obj) == gui.Textarea:
                        self.current_focus.obj.move_cursor_end()
                        textchanged = True
                        
                    elif event.unicode != None and len(event.unicode) > 0:
                        self.current_focus.obj.text_add(event.unicode)
                        textchanged = True
                else:
                    # otherwise, see if the scene has any keybinds
                    for bind in self.get_binds():
                        if bind[0] == event.key:
                            bind[1](KeyDownEvent(None, event.key))
        
            if textchanged:
                self.current_focus.obj.update()
                if self.current_focus.events.has_key("keydown") and self.current_focus.events["keydown"] is not None:
                    self.current_focus.events["keydown"](KeyDownEvent(self.current_focus, event.key))
        
        return True
    
    def _swap_last_focused(self):
        if self.current_focus is None and self.last_focus is not None:
            if self.last_focus.events.has_key("blur") and self.last_focus.events["blur"] is not None:
                self.last_focus.events["blur"](BlurEvent(self.last_focus))

        if self.last_focus is not None:
            self.last_focus.obj.blinking = False
            self.last_focus.obj.swap_enabled()
            self.last_focus.obj.update()
            self.last_focus = None
    
    def _lose_current_focus(self):
        self.last_focus = self.current_focus
        self.current_focus = None
        self._swap_last_focused()

    def set_focus(self, obj, pos):
        #obj = self.current_scene.objects[name]
        self.current_focus = obj
        obj.obj.swap_enabled()
        if type(obj.obj) == gui.Textarea:
            mx, my = pos
            obj.obj.set_cursor_pos (mx, my)
        
        obj.obj.update()
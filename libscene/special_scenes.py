from pygame.locals import *
from scene import Scene

class MenuScene (Scene):
    # self, pixels from left for menu items, pixels from top for first menu item, pixels between labels, color dict
    def __init__ (self, game, label_x, label_y, label_distance, label_padding, colors, selectionpath, spacer=120):
        Scene.__init__ (self, game, setup=False)
        
        self.label_x = label_x
        self.label_y = label_y
        self.label_distance = label_distance
        self.label_padding = label_padding
        self.label_spacer = spacer
        
        self.label_y_spacing = 0
        
        self.colors = colors
        
        self.buttons = []
        self.current_selection = 0
        
        self.add_keybind (K_DOWN, self.update_selection_key)
        self.add_keybind (K_UP, self.update_selection_key)
        self.add_keybind (K_RETURN, self.activate_selection)
        self.add_keybind (K_RIGHT, self.activate_selection)
        
        self.add_object ("selection", "image", (0, self.label_y - self.label_padding), { "layer": -1, "path": selectionpath })
        
        # since we defined setup=False, our responsbility to load scene
        self.load_scene()
    
    def add_button (self, name, label, onclick=None, enabled=True, fontfile="resources/fonts/Harabara.ttf", fontsize=42):
        pos = len(self.buttons)
        
        if pos == 0 and enabled == True:
            color = "highlight"
        elif enabled == True:
            color = "normal"
        else:
            color = "disabled"
        
        if self.current_selection > 0 and self.buttons[self.current_selection - 1] == "-":
            print "increasing y becxause previous was a spacer"
            self.label_y_spacing += self.label_spacer
        
        self.add_object (name, "label", (self.label_x, self.label_y + (pos * self.label_distance) + self.label_y_spacing), {
                "text": label,
                "fontfile": fontfile,
                "fontsize": fontsize,
                "fgcolor": self.colors[color]
            }, {
                "click": onclick,
                "hover_on": self.hover_item
            })
        
        self.buttons.append (name)
    
    def selection_disabled (self, sel):
        if self.buttons[sel] == "-":
            return True
        
        return self.objects[self.buttons[sel]].obj.color == self.colors["disabled"]
    
    def update_selection_key(self, event):
        if len(self.buttons) == 0:
            return

        newsel = self.get_new_selection(event)
        
        # keep going until we pick one that isn't disabled (if the next one is)
        while self.selection_disabled(newsel) and self.buttons[self.current_selection] != "-":
            newsel = self.get_new_selection(event, newsel)

        # and update
        self.update_selection (newsel)
    
    def get_new_selection (self, event, newsel=None):
        key = event.key
        if newsel is None:
            newsel = self.current_selection
        
        if key == K_UP:
            newsel -= 1
            if newsel < 0:
                newsel = len(self.buttons) - 1
        else:
            newsel += 1
            if newsel > (len(self.buttons) - 1):
                newsel = 0
        
        return newsel
    
    def update_selection (self, new):
        # return old selection to normal color
        self.get_current_button().obj.update_color (self.colors["normal"])
        
        self.current_selection = new
        
        # change color of new text
        self.get_current_button().obj.update_color (self.colors["highlight"])
        
        # and move the background selection sprite
        self.move_selection()
    
    def move_selection(self):
        obj = self.objects["selection"]
        x, y = obj.pos
        
        y = self.label_y + (self.current_selection * self.label_distance)
        y -= 8
        
        if self.current_selection > 0 and self.buttons[self.current_selection - 1] == "-":
            y += self.label_y_spacing
        
        obj.pos = (x, y)
    
    def activate_selection(self, event):
        # pretend we clicked on the button if we hit enter/right
        btn = self.get_current_button()
        if btn.events.has_key("click") and btn.events["click"] != None:
            btn.events["click"](None)
    
    def get_current_button (self):
        return self.objects[self.buttons[self.current_selection]]
    
    def hover_item (self, event):
        obj = event.target
        if self.buttons.count(obj.name) > 0 and obj.obj.color != self.colors["disabled"]:
            # awesome, button is in our list, update current selection
            newsel = self.buttons.index(obj.name)
            self.update_selection (newsel)
    
    def add_spacer (self):
        self.buttons.append ("-")
        
    def pop_button (self):
        btn = self.buttons.pop()
        del self.objects[btn]
        print "popped", btn
        print self.buttons
    
    def pop_spacer (self):
        self.buttons.pop()
        self.label_y_spacing -= self.label_spacer
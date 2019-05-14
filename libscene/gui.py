import pygame
from pygame.locals import *


# padding[0] = top
#        [1] = left
#        [2] = bottom
#        [3] = right
#
# (just like CSS)

def real_size (size, padding):
    return (size[0] + padding[1] + padding[3], size[1] + padding[0] + padding[2])

class Box(pygame.sprite.Sprite):
    def __init__ (self, size, color=(0,0,0), path=None):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.color = color
        self.image = None
        self.path = path
        self.size = size
        self.update()
    
    def update(self):
        if self.path is not None:
            self.image = pygame.image.load (self.path)
        else:
            self.image = pygame.Surface(self.size, flags=SRCALPHA).convert_alpha()
            if self.color is not None:
                self.image.fill (self.color)
        self.size = self.image.get_size()        
        self.rect = self.image.get_rect()

class Label(pygame.sprite.Sprite):
    def __init__ (self, font, color, text):
        pygame.sprite.Sprite.__init__(self)
        self.text = text
        self.font = font
        self.color = color
        self.image = None
        self.size = None
        self.update()
    
    def update(self):
        self.image = self.font.render(self.text, True, self.color)
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
    
    def update_text(self, text):
        self.text = text
        self.update()
    
    def update_color(self, color):
        self.color = color
        self.update()

class Textbox(pygame.sprite.Group):
    def __init__(self, font, textcolor, bgcolor, disabledcolor, disabled=False, autosize=True, size=None, text="",padding=(0,0,0,0)):
        # first, create label
        pygame.sprite.Group.__init__ (self)
        
        self.font = font
        self.text = text
        self.fgcolor = textcolor
        self.bgcolor = bgcolor
        self.nocolor = disabledcolor
        
        self.disabled = disabled
        self.current_color = self.nocolor
        
        self.autosize = autosize
        self.padding = padding
        self.size = size       
        self.NUM_FRAMES_BLINK = 20
        self.frames_blink = self.NUM_FRAMES_BLINK
        self.blinking = False
        
        self.update()
    
    def swap_enabled(self):
        if self.disabled:
            return
        
        if self.current_color == self.nocolor:
            self.current_color = self.fgcolor
        else:
            self.current_color = self.nocolor
    
    def update_text(self, text):
        self.text = text
        self.update()
    
    def update_color(self, color):
        self.color = color
        self.update()
    
    def update(self):
        self.label = Label (self.font, self.current_color, self.text)
        
        if not self.blinking:
            self.label.text = self.text
            self.label.update()
        else:
            self.label.text = self.text + "|"
            self.label.update()
        
        self.empty()
        
        if self.autosize:
            self.size = self.label.image.get_size()
            
        # recreate background box
        if self.bgcolor != None:
            self.bg = Box (real_size(self.size, self.padding), self.bgcolor)
        
        self.label.rect.topleft = (self.padding[1], self.padding[0])
        
        # check to see if we should add it back because there is a bgcolor change
        if self.bgcolor != None:
            self.add (self.bg)
            
        self.add (self.label)
        
        self.create_image()
    
    def move_down (self, amount):
        for obj in self:
            x, y = obj.rect.topleft
            obj.rect.topleft = (x, y + amount)
            print "new topleft=", obj.rect.topleft
    
    def create_image(self):
        if len(self) > 1:
            self.image = pygame.Surface(self.bg.image.get_size())
            self.draw (self.image)
        else:
            self.image = self.label.image
        self.size = self.image.get_size()
    
    def blink_cursor(self):
        self.frames_blink -= 1
        if self.frames_blink == 0:
            self.blinking = not self.blinking
            self.frames_blink = self.NUM_FRAMES_BLINK
            self.update()
    
    def text_add (self, text):
        self.text += text
    
    def text_backspace (self):
        self.text = self.text[:-1]

class Textarea(pygame.sprite.Sprite):
    def __init__ (self, font, textcolor, disabledcolor, disabled=False, autosize=True, size=None, text="", padding=(0,0,0,0), linespacing=-5,editable=False):
        pygame.sprite.Sprite.__init__ (self)
        
        self.font = font
        self.fgcolor = textcolor
        self.bgcolor = None
        self.nocolor = disabledcolor
        
        if disabled:
            self.current_color = self.nocolor
        else:
            self.current_color = self.fgcolor
        
        self.disabled = disabled
        self.editable = editable
        self.autosize = autosize
        self.size = size
        self.text = text
        self.padding = padding
        self.linespacing = linespacing
        
        self.image = None
        self.size = size
        
        self.labels = []
        self.current_label = 0
        self.cursor_loc = 0
        
        self.NUM_FRAMES_BLINK = 20
        self.frames_blink = self.NUM_FRAMES_BLINK
        self.blinking = False
                
        self.update()
    
    def update_text (self, text):
        self.text = text
        self.update()
    
    def update (self):
        splittext = self.text.split('\n')
        print '[textarea, splittext]' , splittext
        
        if len(splittext) > len(self.labels):
            # move cursor down if new line added
            self.current_label += 1
        elif len(splittext) < len(self.labels):
            # move cursor up if line removed
            self.current_label -= 1
        
        self.labels = []
        
        if self.autosize:
            self.size = None
        
        if not self.size:
            self.surface = None
        else:
            self.surface = pygame.surface.Surface (self.size, flags=SRCALPHA)
            
        from_top = self.linespacing
        surf_y = 0
        surf_x = 0
        
        i = 0
        for text in splittext:
            if i == self.current_label:
                if self.blinking:
                    a = text[0:self.cursor_loc]
                    b = text[self.cursor_loc:]
                    text = ''.join ([a, '|', b])
            
            label = Label (self.font, self.current_color, text)
            self.labels.append (label)
            
            if label.size[0] > surf_x:
                surf_x = label.size[0]
            
            surf_y += label.size[1] + self.linespacing
            i += 1
        
        surf_y -= self.linespacing
        
        if self.surface is None:
            self.surface = pygame.surface.Surface ((surf_x, surf_y), flags=SRCALPHA)
    
        self.create_image()
        
    def create_image(self):
        # blit all text to one image
        y = 0
        for obj in self.labels:
            self.surface.blit (obj.image, (0, y))
            y += self.linespacing + obj.image.get_size()[1]
        
        # and blit to destination image
        self.image = self.surface
        self.size = self.image.get_size()
    
    def swap_enabled(self):
        if self.disabled:
            return
        
        if self.current_color == self.nocolor:
            self.current_color = self.fgcolor
        else:
            self.current_color = self.nocolor
            
        self.update()
    
    def blink_cursor(self):
        self.frames_blink -= 1
        if self.frames_blink == 0:
            self.blinking = not self.blinking
            self.frames_blink = self.NUM_FRAMES_BLINK
            self.update()
    
    def move_cursor_down(self):
        if self.current_label == len(self.labels) - 1:
            return
        
        # check to see if we're moving down to a line shorter
        if self.cursor_loc > len(self.get_current_label().text) - 1:
            self.move_cursor_end()
        
        self.current_label += 1
        self.update()
    
    def move_cursor_up(self):
        if self.current_label == 0:
            if self.cursor_loc == -1:
                self.cursor_loc = 0
            return
        
        self.current_label -= 1
        
        if self.cursor_loc == -1:
            # if moving from previous line by hitting left, goto end of line
            self.move_cursor_end()
        elif self.cursor_loc > len(self.get_current_label().text) - 1:
            # check to see if we're moving down to a line longer
            self.move_cursor_end()
        
        self.update()
    
    def move_cursor_right(self):
        self.cursor_loc += 1
        
        if self.cursor_loc > len(self.get_current_label().text) - 1:
            oldpos = self.current_label
            self.move_cursor_down()
            if oldpos != self.current_label:
                # cursor has moved, so moved down to line below
                self.move_cursor_home()
    
    def move_cursor_left(self):
        if self.cursor_loc == -1:
            return
        
        self.cursor_loc -= 1
        if self.cursor_loc < 0:
            self.move_cursor_up()
        elif self.cursor_loc > len(self.get_current_label().text) - 1:
            self.move_cursor_home()
            self.move_cursor_down()
    
    def move_cursor_end(self):
        self.cursor_loc = len(self.get_current_label().text)
    
    def move_cursor_home(self):
        self.cursor_loc = 0
    
    def set_cursor_pos (self, mx, my):
        # work out what line and location to put the cursor when clicked on
        y = 0
        
        labelidx = 0
        
        for obj in self.labels:
            if y > my:
                break
            y += self.linespacing + obj.image.get_size()[1]
            labelidx += 1
        
        self.current_label = labelidx - 1
        self.move_cursor_end()
    
    def get_current_label (self):
        return self.labels[self.current_label]
    
    def text_add (self, text):
        splittext = self.text.split('\n')
        newline = ""
        line = splittext[self.current_label]
        
        a = line[0:self.cursor_loc] + text
        b = line[self.cursor_loc:]
        newline = ''.join ([a, b])
        
        splittext[self.current_label] = newline
        self.text = '\n'.join(splittext)
        
        self.cursor_loc += 1
    
    def text_backspace (self):
        splittext = self.text.split('\n')
        newline = ""
        line = splittext[self.current_label]
        
        a = line[0:self.cursor_loc - 1]
        b = line[self.cursor_loc:]
        newline = ''.join ([a, b])
        
        if self.cursor_loc == 0:
            del splittext [self.current_label - 1]
        
        splittext[self.current_label] = newline
        self.text = '\n'.join(splittext)
        
        self.cursor_loc -= 1
    
    def text_delete (self):
        splittext = self.text.split('\n')
        newline = ""
        line = splittext[self.current_label]
        
        a = line[0:self.cursor_loc]
        b = line[self.cursor_loc + 1:]
        newline = ''.join ([a, b])
        
        if self.cursor_loc == len(line):
            del splittext [self.current_label + 1]
        
        splittext[self.current_label] = newline
        self.text = '\n'.join(splittext)

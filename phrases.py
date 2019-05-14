from pygame.locals import *
from libscene import Scene
import settings

class PhraseScene(Scene):
    def load_scene (self):
        #loading the word list
        self.linelist = []
        self.f = open("resources/config/phrases.txt","r")
        for line in self.f:
            w = line.replace('\r','').strip()
            self.linelist.append(w)
        self.f.close()

        self.adding = False
        self.deleting = False                    
        self.add_prevscene_keybind ()
        self.add_background ("resources/menu/generic_background.png")
        self.add_label("add",(50,150),"resources/fonts/Harabara.ttf","Add Phrases",(255,255,255),event=self.add_phrase)
        self.add_label("delete",(50,205),"resources/fonts/Harabara.ttf","Delete Phrases",(255,255,255),event=self.delete_phrase)        
        self.add_label("save",(50,100),"resources/fonts/Harabara.ttf","Save",(255,255,255),fontsize=30,visible=False,event=self.save_phrase)
        self.add_label("kill",(50,330),"resources/fonts/Harabara.ttf","Delete",(255,255,255),fontsize=48,visible=False,event=self.kill_phrase)
        self.add_object("phrasedisp","textbox",(50,50),{"visible":False,"text":"","fontsize":43,"bgcolor":(250,250,255,255)},{"keydown":self.update_search})
        self.add_object("multidisp","textarea",(50,150),{"visible":False,"text":"Search above","fontsize":43,"bgcolor":(250,250,255,200),"editable":False})
        self.add_label("back",(50,400),"resources/fonts/Harabara.ttf","< back",(255,255,255),event=self.load_prev_scene)

    def reset_scene(self,event):
        #this takes us back to the add/delete mini-scene
        self.deleting = False
        self.adding = False
        self.objects["phrasedisp"].visible = False
        self.objects["phrasedisp"].obj.text = ""
        self.objects["multidisp"].obj.update_text("Search below")
        self.objects["add"].visible = True
        self.objects["delete"].visible = True
        self.objects["kill"].visible = False
        self.objects["save"].visible = False
        self.objects["multidisp"].visible = False
        self.objects["back"].events["click"] = self.load_prev_scene

    def add_phrase(self,event):
        #this is a mini-scene, where we can add phrases to the dict
        self.adding = True
        self.objects["phrasedisp"].obj.text = "Click to edit"
        self.objects["back"].events["click"] = self.reset_scene
        self.objects["phrasedisp"].visible = True
        self.objects["add"].visible = False
        self.objects["delete"].visible = False
        self.objects["save"].visible = True

    def delete_phrase(self,event):
        #this is another mini-scene, for deleting phrases
        self.deleting = True
        self.displist = []
        #reload phrases, in case going add -> delete
        self.linelist = []
        self.f = open("resources/config/testphrases.txt","r")
        for line in self.f:
            w = line.replace('\r','').strip()
            self.linelist.append(w)
        self.f.close()
        
        self.objects["phrasedisp"].obj.text = "Click to search"
        self.objects["back"].events["click"] = self.reset_scene
        self.objects["add"].visible = False
        self.objects["delete"].visible = False
        self.objects["kill"].visible = True
        self.objects["phrasedisp"].visible = True
        self.objects["multidisp"].visible = True

    def update_search(self,event):
        # search for phrases
        if self.deleting:
            self.displist = []
            if not self.objects["phrasedisp"].obj.text:
                self.objects["multidisp"].obj.update_text("Search above")
            else:
                for line in self.linelist:
                    if line.startswith((self.objects["phrasedisp"].obj.text).lower()):
                        self.displist.append(line)
                self.objects["multidisp"].obj.update_text('\n'.join(self.displist))

    def kill_phrase(self,event):
        linenum = self.objects["multidisp"].obj.current_label
        self.linelist.remove(self.displist[linenum])
        print 'REMOVED FROM LINELIST'
        self.displist.pop(linenum)
        #save to file
        self.f = open("resources/config/testphrases.txt","w")
        for line in self.linelist:
            line = line + "\n"
            self.f.write(line)
        self.f.close()
        

    """
    def start_phrase(self,event):
        if self.adding:
            if self.objects["phrasedisp"].obj.text == "Click to edit":
                self.objects["phrasedisp"].obj.text = ""
        elif self.deleting:
            if self.objects["phrasedisp"].obj.text == "Click to search":
                self.objects["phrasedisp"].obj.text = ""
            
    def reset_phrasedisp(self,event):
        if self.adding:
            if not self.objects["phrasedisp"].obj.text:
                self.objects["phrasedisp"].obj.text = "Click to edit"
        elif self.deleting:
            if not self.objects["phrasedisp"].obj.text:
                self.objects["phrasedisp"].obj.text = "Click to search"
    """

    def save_phrase(self,event):
        #save the entered phrase to the config file
        w = self.objects["phrasedisp"].obj.text.strip().lower()
        self.linelist.append(w)
        self.f = open("resources/config/testphrases.txt","w")
        for line in self.linelist:
            line = line + "\n"
            self.f.write(line)
        self.f.close()
    



        

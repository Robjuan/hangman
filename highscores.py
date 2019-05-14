import libscene
import operator

class ScoreScene(libscene.Scene):
    def test(self):
        print 'keybind working apparently'
        
    def load_scene (self):
        self.add_prevscene_keybind()
        self.add_background ("resources/menu/generic_background.png")

        #############################
        #TESTING SHIT FOR MAJOR WORK
        
        self.add_keybind(K_w,self.test())


        #############################
        self.select_color = (255, 255, 255)
        self.normal_color = (160, 160, 160)
        
        self.sort_labels = [ "name", "win", "lose", "time", "besttime", "played" ]
        
        self.add_label ("name", (20,50),"resources/fonts/Harabara.ttf", "Name", self.normal_color, 25, self.sort_name)
        self.add_label ("win", (120,50),"resources/fonts/Harabara.ttf", "Wins", self.normal_color, 25, self.sort_win)
        self.add_label ("lose", (200,50),"resources/fonts/Harabara.ttf", "Losses", self.normal_color, 25, self.sort_lose)
        self.add_label ("time", (300,50),"resources/fonts/Harabara.ttf", "Avg Time", self.normal_color, 25, self.sort_time)
        self.add_label ("besttime", (440,50),"resources/fonts/Harabara.ttf", "Best", self.normal_color, 25, self.sort_best)
        self.add_label ("played", (540,50),"resources/fonts/Harabara.ttf", "Games +", self.normal_color, 25, self.sort_played)

        self.current_sort = -1
        self.reverse = False
        
        self.sort_win (None)
        self.layout_scores()

    def layout_scores (self):
        i = 0
        pixel_move = 20
        pixel_initial = 80
        for score in self.game.hscore_man.scores:
            #self.add_label ("name-%d" % i, (50, pixel_initial + (i * pixel_move)), "resources/fonts/Harabara.ttf", score[0], self.get_col_color (0), 20)
            
            self.add_label ("name-%d" % i, (20, pixel_initial + (i * pixel_move)), "resources/fonts/Harabara.ttf", score[0], self.select_color, 20)
            self.add_label ("win-%d" % i, (120, pixel_initial + (i * pixel_move)), "resources/fonts/Harabara.ttf", str(score[1]), self.get_col_color (1), 20)
            self.add_label ("lose-%d" % i, (200, pixel_initial + (i * pixel_move)), "resources/fonts/Harabara.ttf", str(score[2]), self.get_col_color (2), 20)
            self.add_label ("time-%d" % i, (300, pixel_initial + (i * pixel_move)), "resources/fonts/Harabara.ttf", self.time_format(score[3]), self.get_col_color (3), 20)
            self.add_label ("best-%d" % i, (440, pixel_initial + (i * pixel_move)), "resources/fonts/Harabara.ttf", self.time_format(score[4]), self.get_col_color (4), 20)
            self.add_label ("played-%d" % i, (540, pixel_initial + (i * pixel_move)), "resources/fonts/Harabara.ttf", str(score[5]), self.get_col_color (5), 20)
            i+= 1
    
    def clear_scores (self):
        try:
            for i in xrange (0, len(self.scores)):
                del self.objects["name-%d" % i]
                del self.objects["win-%d" % i]
                del self.objects["lose-%d" % i]
                del self.objects["time-%d" % i]
                del self.objects["best-%d" % i]
        except:
            # so we don't asplode for trying to remove non-existent objects on scene
            pass

    def get_current_heading_obj(self):
        return self.objects[self.sort_labels[self.current_sort]].obj
    
    def update_text (self, obj, regular_reverse=False):
        dir_char = "+"
        if self.reverse != regular_reverse:
            dir_char = "-"
            
        obj.update_text (obj.text[:-1] + dir_char)

    def sort_time (self, evt):
        self.gui_sort (3)
        
    def sort_name (self, evt):
        self.gui_sort (0)

    def sort_win (self, evt):
        self.gui_sort (1, True)
    
    def sort_lose (self, evt):
        self.gui_sort (2, True)

    def sort_best (self, evt):
        self.gui_sort (4)
    
    def sort_played (self, evt):
        self.gui_sort (5)
    
    def gui_sort (self, col, default_reverse=False):
        obj = self.get_current_heading_obj()
        if self.current_sort == col:
            self.reverse = not self.reverse
        else:
            obj.update_color (self.normal_color)
            obj.update_text (obj.text [:-2])
            
            self.current_sort = col
            obj = self.get_current_heading_obj()
            obj.update_color (self.select_color)
            if not default_reverse:
                obj.update_text (obj.text + " +")
            else:
                obj.update_text (obj.text + " -")
            self.reverse = default_reverse
        
        self.update_text (obj)
        self.sort (col, self.reverse)
    
    def sort (self, col, reverse=False):
        self.game.hscore_man.scores = sorted (self.game.hscore_man.scores, key=operator.itemgetter(col), reverse=reverse)
        
        self.clear_scores ()
        self.layout_scores ()
    
    def get_col_color (self, col):
        if self.current_sort == col:
            return self.select_color
        else:
            return self.normal_color
    
    def time_format (self, sec):
        min = 0
        hour = 0
        if sec > 60:
            min  = sec / 60
            sec = sec % 60
        
        if min > 60:
            hour = min / 60
            min = min % 60
        
        if hour > 0:
            return "%d hr, %d min, %d sec" % (hour, min, sec)
        elif min > 0:
            return "%d min, %d sec" % (min, sec)
        else:
            return "%d sec" % (sec)

class HighScoreManager:
    def __init__ (self, filename="resources/config/highscores.txt"):
        self.filename = filename
        self.scores = []
        self.load_scores()
        
    def load_scores (self):
        f = open(self.filename)
        for line in f:
            if not line.startswith("#") and len(line) > 5:
                name_s, win_s, lose_s, time_s, best_s, played_s = line.strip().split(',')
                name_s = name_s.strip()
                win_s = win_s.strip()
                lose_s = lose_s.strip()
                time_s = time_s.strip()
                best_s = best_s.strip()
                played_s = played_s.strip()
                self.scores.append ([name_s, int(win_s), int(lose_s), int(time_s), int(best_s), int(played_s)])

        f.close()
    
    def update_score (self, name, time, win=True):
        data = None
        idx = 0
        for score in self.scores:
            if score[0] == name:
                data = score
                break
            
            idx += 1
        
        # if never played before, setup defaults
        if data is None:
            data = [name, 0, 0, 0, time, 0]
            self.scores.append (data)
            idx = len(self.scores) - 1
        
        # increase/decrease score as appropriate
        if win:
            data[1] += 1
            
            # avg time and best time
            print "current avg", data[3]
            data[3] += ((data[3] * data[5]) + time) / (data[5] + 1)
            print "new avg", data[3]
            if time < data[4]:
                data[4] = time
        else:
            data[2] += 1
        
        # num games
        data[5] += 1
        
        self.scores[idx] = data
        self.write_scores()
    
    def beat_prev_time (self, name, time):
        data = None
        idx = 0
        for score in self.scores:
            if score[0] == name:
                data = score
                break
            
            idx += 1
        
        # if never played before, always beats
        if data is None:
            return True
    
        return time < data[4]
    
    def write_scores (self):
        f = open(self.filename, 'w')
        for score in self.scores:
            print score
            f.write ('%s, %d, %d, %d, %d, %d\r\n' % (score[0], score[1], score[2], score[3], score[4], score[5]))
        
        f.close()

import time
from tkinter import *
from tkinter import filedialog, ttk

import numpy as np
from PIL import ImageTk, ImageDraw, ImageFont
import PIL.Image
import ai
import pieces
import sounds as sn
from constants import *

import os
import psutil

from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


def process_memory():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss


# decorator function
def profile(func):
    def wrapper(*args, **kwargs):
        mem_before = process_memory()
        result = func(*args, **kwargs)
        mem_after = process_memory()
        print(func)
        print(mem_before)
        print(mem_after)
        print(mem_after - mem_before)

        return result

    return wrapper


class Interface(Frame):
    def __init__(self, fenetre, **kwargs):
        Frame.__init__(self, fenetre, width=1000, height=1200, **kwargs)
        self.winfo_toplevel().title("Keivchess")
        self.comp = None
        self.pack(fill=BOTH)
        self.a = None
        self.last = None
        self.still = [1, 1, 1, 1]
        self.gameover = 0
        self.color_win = 0
        self.hist = []
        self.data_hist = []
        self.hist_time = 0
        self.taken = []
        self.cb = pieces.Chessboard()
        self.startGame = False
        self.ranking = True
        self.scale = 1
        self.wait_prom = False
        self.training = False
        self.models = ['', '']
        self.play_sound = True
        self.bkg = PIL.Image.open(chessboard_path[os_name])
        self.all_stats = []
        self.canvas = None
        self.plot1 = None

        self.img = Label(self)

        self.bouton_quitter = Button(self, text="Quit", command=self.quit_and_sound)
        self.bouton_train = Button(self, text="RL Training", command=lambda: self.start_game('Training'))
        self.bouton_load_white = Button(self, text="Load White", command=lambda: self.load_model_white())
        self.bouton_load_black = Button(self, text="Load Black", command=lambda: self.load_model_black())

        self.bouton_tp = Button(self, text="Two players", fg="blue", command=lambda: self.start_game('Two players'))
        self.bouton_tc = Button(self, text="Two computers", fg="blue",
                                command=lambda: self.start_game('Two computers'))
        self.bouton_w = Button(self, text="Play white", fg="black",
                               command=lambda: self.start_game('Play white'))
        self.bouton_b = Button(self, text="Play black", fg="black",
                               command=lambda: self.start_game('Play black'))
        self.bouton_bw = Button(self, text="Blindfold white", fg="black",
                                command=lambda: self.start_game('Blindfold white'))
        self.bouton_bb = Button(self, text="Blindfold black", fg="black",
                                command=lambda: self.start_game('Blindfold black'))
        self.bouton_flip = Button(self, text="Flip board", fg="blue", command=lambda: self.flip())
        values = ['First move', 'Random', '1', '2', '3', '4', 'RL (CNN)', 'RL (Dense)']
        self.label_black = Label(self, text="Select AI for black")
        self.combo_black = ttk.Combobox(self, values=values, name='black')
        self.combo_black.current(6)
        self.label_white = Label(self, text="Select AI for white")
        self.combo_white = ttk.Combobox(self, values=values, name='white')
        self.combo_white.current(6)

        self.img = Label(self, image='')
        self.place_buttons()
        sn.start()

    def place_buttons(self):
        self.bouton_train.place(relx=.65, rely=0)
        self.bouton_quitter.place(relx=.65, rely=0.8)
        self.bouton_tp.place(relx=.65, rely=.1)
        self.bouton_tc.place(relx=.65, rely=.2)
        self.bouton_w.place(relx=.65, rely=.3)
        self.bouton_b.place(relx=.65, rely=.4)
        self.bouton_bw.place(relx=.65, rely=.5)
        self.bouton_bb.place(relx=.65, rely=.6)
        self.bouton_flip.place(relx=.65, rely=.7)
        self.label_white.place(relx=.8, rely=.05)
        self.label_black.place(relx=.8, rely=.15)
        self.combo_white.place(relx=.8, rely=.1)
        self.combo_black.place(relx=.8, rely=.2)
        self.bouton_load_black.place(relx=.9, rely=0)
        self.bouton_load_white.place(relx=.8, rely=0)
        self.img.place(relx=0, rely=0)

    def load_model_white(self):
        self.models[0] = filedialog.askdirectory(initialdir='RL models')
        values = ['First move', 'Random', '1', '2', '3', '4', 'RL (scratch)', f'RL ({self.models[0].split("/")[-1]})']
        self.combo_white['values'] = values
        print(self.models)

    def load_model_black(self):
        self.models[1] = filedialog.askdirectory(initialdir='RL models')
        values = ['First move', 'Random', '1', '2', '3', '4', 'RL (scratch)', f'RL ({self.models[1].split("/")[-1]})']
        self.combo_black['values'] = values
        print(self.models)

    def quit_and_sound(self):
        self.gameover = 1
        sn.end(thread=False)
        self.quit()

    def memory_initialisation(self):
        self.hist = []
        self.data_hist = []
        self.hist_time = 0
        self.gameover = 0
        self.color_win = 0
        self.a = None
        self.last = None
        self.still = [1, 1, 1, 1]
        self.taken = []
        self.cb = pieces.Chessboard()
        self.cb.white_init()
        self.cb.black_init()

    def gui_initialisation(self, option):
        self.memory_initialisation()
        self.all_stats = []
        self.option = option
        self.training = option == 'Training'
        self.play_sound = option != 'Training'
        self.model = ''
        self.c1 = [self.combo_white.get(), self.combo_white.get()]
        self.c2 = [self.combo_black.get(), self.combo_black.get()]
        if option != 'Two players':
            if 'black' in option:
                self.comp = ai.Keivchess(self.c1[0], self.c1[1], self.models[0])
            else:
                self.comp = ai.Keivchess(self.c2[0], self.c2[1], self.models[1])
            if option in ['Two computers', 'Training']:
                self.comp = [ai.Keivchess(self.c1[0], self.c1[1], self.models[0]),
                             ai.Keivchess(self.c2[0], self.c2[1], self.models[1])]
                if option == 'Training':
                    fig = Figure(figsize=(3, 3), dpi=110)
                    self.canvas = FigureCanvasTkAgg(fig, master=self, )
                    self.canvas.get_tk_widget().pack()
                    toolbar = NavigationToolbar2Tk(self.canvas, self)
                    toolbar.update()
                    self.canvas.get_tk_widget().pack()
                    self.plot1 = fig.add_subplot(111)
                    self.plot1.plot([], [])

        if option == 'Play black' or option == 'Blindfold black':
            self.chess_up = -1
        else:
            self.chess_up = 1
        self.display_pieces(self.cb.table, to=self.chess_up)
        self.show_bkg(self.bkg)
        self.update()

    def plot_stats(self, stats):
        N = min(30,len(stats))
        y0 = np.convolve(100 * np.array(stats)[:,0], np.ones(N)/N, mode='same')
        y1 = np.convolve(100 * np.array(stats)[:,1], np.ones(N)/N, mode='same')
        y2 = np.convolve(100 * np.array(stats)[:,2], np.ones(N)/N, mode='same')
        y = np.stack((y0,y1,y2),-1)
        x = np.arange(len(stats))
        self.plot1.clear()
        self.plot1.plot(x, y)
        self.plot1.set_xlim(0, len(x))
        self.plot1.set_ylim(-5, 105)
        sums = np.sum(np.array(stats)[-N:],0)
        self.plot1.set_title(f'{100-sums[1]/sum(sums):.1f}% of checkmates')
        self.plot1.legend(['B-win', 'Draw', 'W-win'])
        self.canvas.draw()

    def show_bkg(self, bkg):
        new_size = min(int(self.winfo_width() * REL_CHESSBOARD_SIZE), self.winfo_height())
        self.scale = new_size / CHESSBOARD_SIZE
        bkg = bkg.resize((new_size, new_size))
        render = ImageTk.PhotoImage(bkg)
        self.img.configure(image=render)
        self.img.image = render

    def display_pieces(self, table, to=1, save=True):
        self.bkg = PIL.Image.open(chessboard_path[os_name])
        for i in range(8):
            for j in range(8):
                if table[j, i] != 0:
                    load = PIL.Image.open(pieces.images[6 + table[j, i]])
                    load = load.rotate(90 * (to + 1))
                    load = load.resize((PIECE_SIZE, PIECE_SIZE))
                    self.bkg.paste(load, (PIECES_SPACING * (7 - j) + CB_BORDER, PIECES_SPACING * i + CB_BORDER), load)
        self.bkg = self.bkg.rotate(90 * (to + 1))
        w = 0
        b = 0
        piece = -5
        for i in range(len(self.taken)):
            if self.taken[i] < 0:
                if piece == self.taken[i]:
                    b += SAME_TAKEN_SPACING
                else:
                    b += DIFF_TAKEN_SPACING
                mouse = self.tabletomouse(-1 + b, 3.5 - 4.4 * to, 1)
            else:
                if piece == self.taken[i]:
                    w += SAME_TAKEN_SPACING
                else:
                    w += DIFF_TAKEN_SPACING
                mouse = self.tabletomouse(-1 + w, 3.5 + 4.4 * to, 1)
            piece = self.taken[i]
            load = PIL.Image.open(pieces.images[6 + piece])
            load = load.resize((TAKEN_PIECE_SIZE, TAKEN_PIECE_SIZE))
            self.bkg.paste(load, (mouse[0], mouse[1]), load)
        s = ai.sum_value(self.cb.table)
        if s != 0:
            if s > 0:
                b += SCORE_SPACING
                mouse = self.tabletomouse(-1 + b, 3.4 - 4.5 * to, 1)
            else:
                w += SCORE_SPACING
                mouse = self.tabletomouse(-1 + w, 3.4 + 4.5 * to, 1)
            draw = ImageDraw.Draw(self.bkg)
            font = ImageFont.truetype("/usr/share/fonts/truetype/open-sans/OpenSans-Bold.ttf", size=SCORE_FONT_SIZE)
            draw.text((mouse[0], mouse[1]), f'+{np.abs(s)}', fill=(0, 0, 0), font=font)
        if pieces.exposed_king(self.cb.table, self.last, self.still, no_move=True):
            [x, y] = np.where(self.cb.table == 6 * pieces.current_color(self.cb.table, self.last))
            mouse = self.tabletomouse(int(x), int(y), self.chess_up)
            load = PIL.Image.open(reds_path[os_name])
            load = load.resize((SQUARE_SIZE, SQUARE_SIZE))
            load.putalpha(128)
            self.bkg.paste(load, (mouse[0], mouse[1]), load)
        if save:
            if self.last is not None:
                self.hist.append(self.bkg)
                self.hist_time = len(self.hist) - 1
        self.show_last()

    def allowed_moves(self, allrules, movexy):
        for r in allrules:
            if r.split()[0] == movexy:
                xy2 = pieces.xy(r.split()[1])
                mouse2 = self.tabletomouse(xy2[0], xy2[1], self.chess_up)
                load = PIL.Image.open(yellows_path[os_name])
                load = load.resize((SQUARE_SIZE, SQUARE_SIZE))
                load.putalpha(128)
                self.bkg.paste(load, (mouse2[0], mouse2[1]), load)

    def show_last(self):
        if self.last is None:
            return
        xy1 = pieces.xy(self.last[0])
        xy2 = pieces.xy(self.last[1])
        mouse1 = self.tabletomouse(xy1[0], xy1[1], self.chess_up)
        mouse2 = self.tabletomouse(xy2[0], xy2[1], self.chess_up)
        p1 = -5
        p2 = 33
        load = PIL.Image.open(reds_path[os_name])
        load = load.resize((SURROUND_SIZE, 5))
        self.bkg.paste(load, (mouse1[0] + p1, mouse1[1] + p2), load)
        self.bkg.paste(load, (mouse2[0] + p1, mouse2[1] + p2), load)
        load = load.resize((SURROUND_SIZE, 5))
        self.bkg.paste(load, (mouse1[0] + p1, mouse1[1] + p1), load)
        self.bkg.paste(load, (mouse2[0] + p1, mouse2[1] + p1), load)
        load = load.resize((5, SURROUND_SIZE))
        self.bkg.paste(load, (mouse1[0] + p2, mouse1[1] + p1), load)
        self.bkg.paste(load, (mouse2[0] + p2, mouse2[1] + p1), load)
        load = load.resize((5, SURROUND_SIZE))
        self.bkg.paste(load, (mouse1[0] + p1, mouse1[1] + p1), load)
        self.bkg.paste(load, (mouse2[0] + p1, mouse2[1] + p1), load)

    def add_taken(self, piece):
        self.taken.append(piece)
        self.taken.sort()
        self.taken = sorted(self.taken, key=abs)

    def move_process(self, a, b):
        coor = pieces.xy(b)
        if self.cb.table[coor[0], coor[1]] != 0:
            self.add_taken(self.cb.table[coor[0], coor[1]])
            if self.play_sound:
                sn.capture()
        else:
            if self.play_sound:
                sn.move()
        # update chessboard (move piece)
        self.cb.table = pieces.move(self.cb.table, a, b, self.still)
        # update taken pieces by subtracting old/new chessboard sum
        # update last move
        self.last = [a, b]
        X2 = np.concatenate([pieces.xy(self.last[0]), pieces.xy(self.last[1]), self.still])
        self.data_hist.append((self.cb.table, X2))

    def to_promotion(self, yclick):
        prev_xy = pieces.xy(self.a)
        was_sectolast_raw = prev_xy[1] == 3.5 + 2.5 * pieces.current_color(self.cb.table, self.last)
        was_pawn = np.abs(self.cb.table[prev_xy[0]][prev_xy[1]]) == 1
        last_row = yclick == 3.5 + 3.5 * pieces.current_color(self.cb.table, self.last)
        return was_sectolast_raw and was_pawn and last_row

    def user_move(self, event):
        [x, y] = (self.mousetotable(event.x, event.y, self.chess_up))
        # click outside of chessboard
        if not pieces.oncb(x, y):
            self.a = self.b = None
            return False
        movexy = pieces.mv(x, y)
        allrules = pieces.allrules_ek(self.cb.table, self.last, self.still)
        # if original square (a) not selected yet, set a, and display yellow allowed moves
        if self.a is None:
            self.a = movexy
            self.allowed_moves(allrules, movexy)
            self.show_bkg(self.bkg)
            self.update()
            return False
        # else, see where this second click lands and act accordingly
        else:
            # if the origin piece (a) is a pawn and the landing (b) coordinate is the edge (0 or 7), set promoted b
            # else, set b
            if self.to_promotion(y):
                if not self.wait_prom:
                    self.wait_prom = True
                    # prom = input('Promotion:N,B,R,Q?')
                    for k in (range(2, 6)):
                        load = PIL.Image.open(pieces.images[6 + pieces.current_color(self.cb.table, self.last) * k])
                        load = load.resize((PIECE_SIZE // 2, PIECE_SIZE // 2))
                        self.bkg.paste(
                            load,
                            (
                                (PIECE_SIZE + 6) * int(
                                    3.5 * (1 - self.chess_up) + self.chess_up * x) + CB_BORDER + PIECE_SIZE // 2 * (
                                            k & 1),
                                (PIECE_SIZE + 6) * int(
                                    3.5 * (1 + self.chess_up) - self.chess_up * y) + CB_BORDER + PIECE_SIZE // 4 * (
                                            k & 2)
                            ),
                            load
                        )
                    self.b = movexy
                    self.show_bkg(self.bkg)
                    self.update()
                    return False
                else:
                    self.wait_prom = False
                    if movexy == self.b:
                        [x2, y2] = (self.mousetotable(event.x, event.y, self.chess_up, granularity=16))
                        self.b += ['R', 'B', 'N', 'Q'][::self.chess_up][2 * (x2 % 2) + (y2 % 2)]
                    else:
                        self.a = movexy
                        self.b = None
                        self.display_pieces(self.cb.table, to=self.chess_up, save=False)
                        self.allowed_moves(allrules, movexy)
                        self.show_bkg(self.bkg)
                        self.update()
                        return False
            else:
                self.wait_prom = False
                self.b = movexy
            # if (a b) is not an allowed move, unset b and set a as the newly clicked square
            # and reset chessboard (to clear yellow squares) and redraw allowed moved squares
            if self.a + ' ' + self.b not in allrules:
                self.a = movexy
                self.b = None
                self.display_pieces(self.cb.table, to=self.chess_up, save=False)
                self.allowed_moves(allrules, movexy)
                self.show_bkg(self.bkg)
                self.update()
                return False
            else:
                self.move_process(self.a, self.b)
                self.gameover_actions()
                # display new chessboard
                self.display_pieces(self.cb.table, to=self.chess_up)
                self.show_bkg(self.bkg)
                self.update()
                return True

    def gameover_actions(self):
        self.gameover, self.color_win = ai.check_gameover(self.cb.table, self.last, self.still, self.data_hist)
        if self.gameover:
            if self.color_win == 0:
                if self.play_sound:
                    sn.draw()
                end = 'Draw!'
            elif self.color_win * self.chess_up == 1:
                if self.play_sound:
                    sn.victory()
                end = 'You won!'
            else:
                if self.play_sound:
                    sn.game_over()
                end = 'You lost!'
            self.winfo_toplevel().title(end)

    def ai_move(self, comp, show=True):
        cmove = comp.move(self.cb.table, self.last, self.still, self.data_hist).split()
        self.move_process(cmove[0], cmove[1])
        self.gameover_actions()
        if show:
            # display new chessboard
            self.display_pieces(self.cb.table, to=self.chess_up, save=not self.training)
            self.show_bkg(self.bkg)
            self.update()
        return cmove

    def blindfold_game(self):
        turn = 0
        while not self.gameover:
            if talking:
                bmove = self.get_voice_move()
                blind.engine.say("You chose " + bmove[0] + ' to ' + bmove[1])
                blind.engine.runAndWait()
            else:
                bmove = input("Move: ").split()
            self.move_process(bmove[0], bmove[1])
            # display new chessboard
            self.display_pieces(self.cb.table, to=self.chess_up)
            self.update()

            cmove = self.comp.move(self.cb.table, self.last, self.still, self.data_hist).split()
            if talking:
                blind.engine.say(cmove[0] + ' to ' + cmove[1])
                blind.engine.runAndWait()
            print(cmove[0] + ' ' + cmove[1])
            self.move_process(cmove[0], cmove[1])
            # display new chessboard
            self.display_pieces(self.cb.table, to=self.chess_up)
            if talking:
                blind.engine.say(cmove[0] + ' to ' + cmove[1])
                blind.engine.runAndWait()
            print(cmove[0] + ' ' + cmove[1])
            self.gameover_actions()
            self.show_bkg(self.bkg)
            self.update()
            turn = 1 - turn

    def key(self, event):
        print("pressed", repr(event.char))

    def leftKey(self, event):
        self.hist_time -= 1
        self.hist_time = max(0, self.hist_time)
        self.show_bkg(self.hist[self.hist_time])
        self.update()

    def rightKey(self, event):
        self.hist_time += 1
        self.hist_time = min(len(self.hist) - 1, self.hist_time)
        self.show_bkg(self.hist[self.hist_time])
        self.update()

    def flip(self):
        if self.startGame:
            self.chess_up = -self.chess_up
            self.display_pieces(self.cb.table, to=self.chess_up, save=False)
            self.show_bkg(self.bkg)
            self.update()

    def mousetotable(self, x, y, to, granularity=8):
        x /= self.scale
        y /= self.scale
        c0 = float(CB_BORDER)
        c1 = float(CHESSBOARD_SIZE - CB_BORDER)
        if to == -1:
            xnew = granularity - 1 - int((x - c0) / (c1 - c0) * granularity)
            ynew = int((y - c0) / (c1 - c0) * granularity)
        else:
            xnew = int((x - c0) / (c1 - c0) * granularity)
            ynew = granularity - 1 - int((y - c0) / (c1 - c0) * granularity)
        return [xnew, ynew]

    def tabletomouse(self, x, y, to):
        c0 = CB_BORDER
        c1 = CHESSBOARD_SIZE - CB_BORDER
        mx1 = 8
        my1 = 4
        mx2 = 3
        my2 = 8
        if to == -1:
            xnew = int((c1 - c0) / 8 * (7 - x) + c0 + mx2)
            ynew = int((c1 - c0) / 8 * y + c0 + my2)
        else:
            xnew = int((c1 - c0) / 8 * x + c0 + mx1)
            ynew = int((c1 - c0) / 8 * (7 - y) + c0 + my1)
        return [int(xnew), int(ynew)]

    def get_voice_move(self):
        bmove = [0]
        attempt = 0
        allrules = pieces.allrules_ek(self.cb.table, self.last, self.still)
        while attempt < 4 and (len(bmove) != 2 or bmove[0] + ' ' + bmove[1] not in allrules):
            blind.engine.say("Say a valid move")
            blind.engine.runAndWait()
            with blind.mic as source:
                audio = blind.r.listen(source)
            try:
                bmove = blind.r.recognize_google(audio).lower().split(' to ')
                if len(bmove) == 1:
                    bmove = bmove.split()
            except:
                bmove = [0]
                attempt -= 1
            print(bmove)
            attempt += 1
        if attempt == 4:
            blind.engine.say("I can't understand your accent, write down your move, you prick!")
            blind.engine.runAndWait()
            while len(bmove) != 2 or bmove[0] + ' ' + bmove[1] not in allrules:
                bmove = input("Move: ").split()
        return bmove

    def callback(self, event):
        if self.startGame and self.option != 'Two computers' and not self.gameover:
            moved = self.user_move(event)
            if moved:
                # if two player mode, flip chessboard
                if self.option == 'Two players':
                    time.sleep(.1)
                    self.chess_up = -self.chess_up
                    self.display_pieces(self.cb.table, to=self.chess_up)
                    self.show_bkg(self.bkg)
                    self.update()
                # else, AI plays
                elif not self.gameover:
                    self.ai_move(self.comp)

    def on_window_resize(self, event):
        if np.random.random() < ON_WINDOW_RESIZE__RANDOM_TRIGGER:
            width = event.width
            height = event.height
            try:
                self.show_bkg(self.bkg)
            except:
                pass

    def start_game(self, option):
        self.gui_initialisation(option)
        talking = 0
        if 'black' in option:
            cmove = self.ai_move(self.comp)
            if talking:
                blind.engine.say(cmove[0] + ' to ' + cmove[1])
                blind.engine.runAndWait()
            print(cmove[0] + ' ' + cmove[1])
        if 'Blindfold' in option:
            self.blindfold_game()

        if self.option == 'Training':
            timestr = time.strftime("%Y%m%d%H%M%S")
            for game in range(N_GAMES):
                stats = [0, 0, 0]
                turn = 0
                self.memory_initialisation()
                while not self.gameover:
                    try:
                        self.ai_move(self.comp[turn], show=game % SHOW_TRAINING_GAMES_PER == 0)
                        turn = 1 - turn
                    except KeyboardInterrupt:
                        break
                stats[self.color_win + 1] = 1
                for i in range(2):
                    if 'RL' in self.comp[i].mode:
                        self.comp[i].update_db(self.data_hist, self.color_win)
                        if game % TRAIN_PER == 0:
                            self.comp[i].train_on_last_games()
                            self.comp[i].model.save(f'RL models/model_{i}_{timestr}')
                self.winfo_toplevel().title(f'Training. Game {game}. Stats: B{stats[0]}/D{stats[1]}/W{stats[2]}')
                self.all_stats.append(stats.copy())
                self.plot_stats(self.all_stats)
                self.update()
        if self.option == 'Two computers':
            turn = 0
            while not self.gameover:
                try:
                    self.ai_move(self.comp[turn])
                    turn = 1 - turn
                except KeyboardInterrupt:
                    break

        self.startGame = True


window = Tk()
# 33,394


window.geometry("1000x800")
interface = Interface(window)
window.bind("<Configure>", interface.on_window_resize)
window.bind("<Button-1>", interface.callback)
window.bind("<Key>", interface.key)
window.bind('<Left>', interface.leftKey)
window.bind('<Right>', interface.rightKey)
window.mainloop()
interface.destroy()

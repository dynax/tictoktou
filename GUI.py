import wx
import board
import search
import os
import time
import datetime
import random
from threading import *

random.seed(time.time())

# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data=None):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class ai_move_thread(Thread):
    """AI move threading, in order to reveal instant frame changes"""
    def __init__(self, main_frame):
        Thread.__init__(self)
        self.main_frame = main_frame
        self.start()

    def run(self):
        main = self.main_frame
        current_player = main.get_current_player()
        dest = current_player.get_strategy(main.board)
        main.board.move(dest)
        main.play_panel.refresh_text()
        main.play_panel.board_panel.update_piece(dest, main.board.o[dest], main.board.x[dest])
        main.board.is_end()
        if main.board.status == 0:
            wx.PostEvent(main, ResultEvent())
        else:
            main.ending(main.board.status)


class MainFrame(wx.Frame):
    """Main control frame"""
    def __init__(self, parent, ID, title, pos=wx.DefaultPosition, style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, ID, title, pos, (320, 460), style)
        self.welcome_panel = WelcomePanel(self)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.welcome_panel, 1, wx.EXPAND)
        self.SetSizer(self.main_sizer)

        self.Bind(wx.EVT_BUTTON, self.OnStart, self.welcome_panel.start_button)
        self.Connect(-1,-1, EVT_RESULT_ID, self.ai_move)

    def OnStart(self, event):
        # intial inner board infomation
        self.board = board.board()
        self.o_player = self._init_player(True, self.welcome_panel.o_player_setting.GetItemLabel(self.welcome_panel.o_player_setting.GetSelection()), self.welcome_panel.o_ai_setting.GetSelection())
        self.x_player = self._init_player(False, self.welcome_panel.x_player_setting.GetItemLabel(self.welcome_panel.x_player_setting.GetSelection()), self.welcome_panel.x_ai_setting.GetSelection())
        # display 
        if True == hasattr(self, "play_panel"):
            self.play_panel.Destroy()
        self.play_panel = PlayPanel(self)
        self.main_sizer.Add(self.play_panel, 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.OnQuit, self.play_panel.quit_button)
        self.Bind(wx.EVT_BUTTON, self.OnRevert, self.play_panel.revert_button)
        self.play_panel.board_panel.board_bmp.Bind(wx.EVT_LEFT_DOWN, self.OnClick)

        self.welcome_panel.Hide()
        self.play_panel.Show()
        self.Layout()
        # start the move
        wx.PostEvent(self, ResultEvent())

    def ending(self, status):
        if status == 1:
            res = "O won. "
        elif status == 2:
            res = "X won. "
        else:
            res = "Draw game. "
        self.play_panel.game_status_text.SetLabel(res)

    def ai_move(self, event):
        if self.board.status != 0 or self.get_current_player().type == "human":
            self.get_current_player().timer_tic()
            return
        self.ai_worker = ai_move_thread(self)

    def OnQuit(self, event):
        self.play_panel.Hide()
        self.welcome_panel.Show()
        self.Layout()

    def OnRevert(self, event):
        current_player = self.get_current_player()
        if current_player.type != "human":
            return

        self.play_panel.game_status_text.SetLabel("Game is running...")
        if self.board.current_round > 0:
            dest = self.board.get_last_move()
            self.board.revert_move()
            current_player.time_update()
            self.play_panel.refresh_text()
            self.play_panel.board_panel.update_piece(dest, 0, 0)
            self.play_panel.board_panel.piece_bmp[dest[0]][dest[1]].Hide()
        if self.board.current_round > 0: # do it twice
            dest = self.board.get_last_move()
            self.board.revert_move()
            current_player.time_update()
            self.play_panel.refresh_text()
            self.play_panel.board_panel.update_piece(dest, 0, 0)
            self.play_panel.board_panel.piece_bmp[dest[0]][dest[1]].Hide()

        self.board.status = 0
        wx.PostEvent(self, ResultEvent())

    def OnClick(self, event):
        if self.board.status != 0:
            return
        current_player = self.get_current_player()
        if current_player.type != "human":
            return

        pos_x, pos_y = event.GetPosition()
        dest = self._pos_to_ind(pos_x, pos_y)
        move_stat = self.board.move(dest)
        if move_stat == 0:
            current_player.time_update()
            self.play_panel.refresh_text()
            self.play_panel.board_panel.update_piece(dest, self.board.o[dest], self.board.x[dest])
            self.board.is_end()

            if self.board.status > 0:
                self.ending(self.board.status) # ending
            else:
                wx.PostEvent(self, ResultEvent())

    def _init_player(self, is_o, player_type, ai_level):
        assert player_type in ["human", "ai"]
        if player_type == "human":
            return human_player(is_o, player_type)
        else:
            strength = 0.2*(ai_level+1.)/4 + 0.8
            return ai_player(is_o, player_type, strength)

    def _pos_to_ind(self, pos_x, pos_y):
        for i in range(3):
            if pos_x <= (i+1) * 90:
                break
        for j in range(3):
            if pos_y <= (j+1) * 90:
                break
        return (i, j)

    def get_current_player(self):
        if True == self.board.is_o:
            return  self.o_player
        else:
            return self.x_player


class WelcomePanel(wx.Panel):
    """Starting panel"""
    def __init__(self, parent):
        self.parent = parent
        wx.Panel.__init__(self, parent)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        game_name = wx.StaticText(self, -1, "\nTicTokTou", style=wx.ALIGN_CENTER)
        font_game_name = wx.Font(28, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        game_name.SetFont(font_game_name)
        self.main_sizer.Add(game_name, 1, wx.ALIGN_CENTER_HORIZONTAL)

        auther = wx.StaticText(self, -1, "By: Lex", style=wx.ALIGN_CENTER)
        self.main_sizer.Add(auther, 1, wx.ALIGN_CENTER_HORIZONTAL)

        self.PLAYTER_TYPE = ["human", "ai"]
        self.AI_LEVEL = ["random", "newbie", "good", "crazy"]

        self.o_player_setting = wx.RadioBox(self, -1, "O Player: ", wx.DefaultPosition, wx.DefaultSize, self.PLAYTER_TYPE, 1, wx.RA_SPECIFY_ROWS)
        self.main_sizer.Add(self.o_player_setting, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.x_player_setting = wx.RadioBox(self, -1, "X Player: ", wx.DefaultPosition, wx.DefaultSize, self.PLAYTER_TYPE, 1, wx.RA_SPECIFY_ROWS)
        self.x_player_setting.SetSelection(1)
        self.main_sizer.Add(self.x_player_setting, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.o_ai_setting = wx.RadioBox(self, -1, "O ai level: ", wx.DefaultPosition, wx.DefaultSize, self.AI_LEVEL, 1, wx.RA_SPECIFY_ROWS)
        self.o_ai_setting.SetSelection(2)
        self.main_sizer.Add(self.o_ai_setting, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.x_ai_setting = wx.RadioBox(self, -1, "X ai level: ", wx.DefaultPosition, wx.DefaultSize, self.AI_LEVEL, 1, wx.RA_SPECIFY_ROWS)
        self.x_ai_setting.SetSelection(2)
        self.main_sizer.Add(self.x_ai_setting, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.start_button = wx.Button(self, -1, "Start")
        self.main_sizer.Add(self.start_button, 1, wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizerAndFit(self.main_sizer)

class PlayPanel(wx.Panel):
    """Play panel"""
    def __init__(self, parent):
        self.parent = parent
        wx.Panel.__init__(self, parent)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        word_line1 = wx.StaticText(self, -1, "Current player: ")
        self.main_sizer.Add(word_line1, 0, wx.ALIGN_LEFT)

        self.current_player_text = wx.StaticText(self, -1, "O")
        self.main_sizer.Add(self.current_player_text, 0, wx.ALIGN_LEFT)

        self.o_player_status = wx.StaticText(self, -1, "O player: "+self.parent.o_player.name+"\t"+self.parent.o_player.get_elapsed_time())
        self.main_sizer.Add(self.o_player_status, 0, wx.ALIGN_LEFT)

        self.x_player_status = wx.StaticText(self, -1, "X player: "+self.parent.x_player.name+"\t"+self.parent.x_player.get_elapsed_time())
        self.main_sizer.Add(self.x_player_status, 0, wx.ALIGN_LEFT)

        self.board_panel = BoardPanel(self)
        self.main_sizer.Add(self.board_panel, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.game_status_text = wx.StaticText(self, -1, "Game is running...")
        self.main_sizer.Add(self.game_status_text, 0, wx.ALIGN_LEFT)

        self.revert_button = wx.Button(self, -1, "Revert")
        self.quit_button = wx.Button(self, -1, "ToMain")
        button_bar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_bar_sizer.Add(self.revert_button, 1, wx.ALIGN_LEFT)
        button_bar_sizer.Add(self.quit_button, 1, wx.ALIGN_LEFT)
        self.main_sizer.Add(button_bar_sizer, 1, wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizerAndFit(self.main_sizer)

    def refresh_text(self):
        if True == self.parent.board.is_o:
            current_player_name = "O"
        else:
            current_player_name = "X"
        self.current_player_text.SetLabel(current_player_name)
        self.o_player_status.SetLabel("O player: "+self.parent.o_player.name+"\t"+self.parent.o_player.get_elapsed_time())
        self.x_player_status.SetLabel("X player: "+self.parent.x_player.name+"\t"+self.parent.x_player.get_elapsed_time())

class BoardPanel(wx.Panel):
    """Bitmap board panel"""
    def __init__(self, parent):
        self.root = parent.parent
        wx.Panel.__init__(self, parent)
        self._load_images()

        self.board_bmp = wx.StaticBitmap(self, -1, self.BOARD_BMP, (0,0))
        self.init_piece()

    def update_piece(self, pos, is_o, is_x):
        if is_o > 0:
            BMP = self.O_BMP
        elif is_x > 0:
            BMP = self.X_BMP
        else:
            BMP = self.BLANK_BMP
        self.piece_bmp[pos[0]][pos[1]].SetBitmap(BMP)
        self.piece_bmp[pos[0]][pos[1]].Show()

    def init_piece(self):
        self.piece_bmp = [[None] * 3 for i in range(3)]
        for i in range(3):
            for j in range(3):
                self.piece_bmp[i][j] = wx.StaticBitmap(self, -1, self.BLANK_BMP, (90*i, 90*j))
                self.piece_bmp[i][j].Hide()

    def restart_piece(self):
        for i in range(3):
            for j in range(3):
                self.update_piece((i, j), 0, 0)

    def _load_images(self, dir_path="dat"):
        self.BOARD_BMP = wx.Bitmap(os.path.join(dir_path, "board.bmp"))
        self.O_BMP = wx.Bitmap(os.path.join(dir_path, "O.bmp"))
        self.X_BMP = wx.Bitmap(os.path.join(dir_path, "X.bmp"))
        self.BLANK_BMP = wx.Bitmap(os.path.join(dir_path, "blank.bmp"))


#===========player logic============
class player:
    def __init__(self, is_o, player_type):
        assert player_type in ["human", "ai"]
        self.type = player_type
        self.is_o = is_o
        self.elaspled_time = 0.

    def get_strategy(self, board):
        raise AttributeError("get_strategy method has not implemented in this player object. ")

    def get_elapsed_time(self):
        return str(datetime.timedelta(seconds=int(self.elaspled_time)))

class human_player(player):
    def __init__(self, is_o, player_type):
        super().__init__(is_o, player_type)
        self.name = "human"
        self.start_time = 0.

    def get_strategy(self, board):
        pass

    def timer_tic(self):
        self.start_time = time.time()

    def time_update(self):
        self.elaspled_time += time.time() - self.start_time

class ai_player(player):
    def __init__(self, is_o, player_type, strength = 1.):
        super().__init__(is_o, player_type)
        self.name = "ai   "
        self.strength = strength
        self.engine = search.absearch()
        self.MID_POS = [(1,1)]
        self.CORNER_POS = [(0,0), (0,2), (2,0), (2,2)]
        self.EDGE_POS = [(0,1), (1,0), (1,2), (2,1)]

    def get_strategy(self, board):
        time_start = time.time()
        time.sleep(0.5)
        if random.random() <= self.strength:
            if board.current_round == 0:
                dest = self._start_strategy()
            else:
                dest = self.engine.get_strategy(board)
        else:
            dest = self._get_random_strategy(board)
        self.elaspled_time += time.time() - time_start
        return dest

    def _start_strategy(self, mid=0.5, corner=0.4, edge=0.1):
        rd = random.random()
        if rd <= mid:
            dest = random.choice(self.MID_POS)
        elif rd <= mid+corner:
            dest = random.choice(self.CORNER_POS)
        else:
            dest = random.choice(self.EDGE_POS)
        return dest

    def _get_random_strategy(self, board):
        possible_moves = board.find_all_moves()
        dest = random.choice(possible_moves)
        return dest


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame(None, wx.ID_ANY, "TicTokTou")
    frame.Show()
    app.MainLoop()
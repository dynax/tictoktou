import board
import search
import readchar
import os
import time
import datetime
import random
random.seed(time.time())

class shell:
    def __init__(self, ini_board=None):
        if None == ini_board:
            self.board = board.board()
        else:
            self.board = ini_board
        self._welcome()

    def display_board(self):
        NUM_SPACE = 5
        COLNAMES = "123"
        ROWNAMES = ["A", "B", "C"]
        os.system("clear")
        display  = "\nO player: " + self.o_player.name + "   " + self.o_player.get_elapsed_time()
        display += "\nX player: " + self.x_player.name + "   " + self.x_player.get_elapsed_time()
        if True == self.board.is_o:
            display += "\n===OOO=== "
        else:
            display += "\n===XXX=== "
        display += " turn.\n\n"
        display += " " * NUM_SPACE + "  "+COLNAMES+"\n"
        for i in range(3):
            display += " " * NUM_SPACE + ROWNAMES[i]+"|"
            for j in range(3):
                if self.board.o[i][j] == 1:
                    display += "O"
                elif self.board.x[i][j] == 1:
                    display += "X"
                else:
                    display += " "
            display += "\n"
        display += "\n"
        print(display)


    def main(self):
        game_status = 2
        while self.board.current_round < 9:
            self.display_board()
            self._display_control()
            if True == self.board.is_o:
                dest = self.o_player.get_strategy(self.board)
            else:
                dest = self.x_player.get_strategy(self.board)
            if dest == 0:
                self.board.revert_move()
                if self.board.current_round>0:
                    self.board.revert_move()
            elif dest == 1:
                game_status = 3
                break
            else: 
                self.board.move(dest)
                if True == self.board.is_win():
                    if False == self.board.is_o:
                        game_status = 0
                    else:
                        game_status = 1
                    break          
        self._ending(game_status)

    def _welcome(self):
        os.system("clear")
        display  = "\n\n\n"
        display += "**************************************************\n" 
        display += "               Welcome to TicTokTou!              \n"
        display += "**************************************************\n\n"
        display += "1: human play O and ai play X\n"
        display += "2: ai play O and human play X\n"
        display += "3: human play both O and X\n"
        display += "4: ai play both O and X\n"
        print(display)
        # set players
        while True:
            key = readchar.readkey().lower()
            if key == "1":
                self.o_player = human_player(True)
                self.x_player = ai_player(False)
                break
            elif key == "2":
                self.o_player = ai_player(True)
                self.x_player = human_player(False)
                break
            elif key == "3":
                self.o_player = human_player(True)
                self.x_player = human_player(False)
                break
            elif key == "4":
                self.o_player = ai_player(True, 0.5)
                self.x_player = ai_player(False)
                break

    def _display_control(self):
        display  = "Use one of the following keys to put a piece on: \n"
        display += "   UIO\n"
        display += "   JKL\n"
        display += "   M,.\n"
        display += "Revert with R.\n"
        display += "Quit with Q.\n"
        print(display) 

    def _ending(self, game_status):
        self.display_board()
        if 2 == game_status:
            print("Draw game. ")
        elif 1 == game_status:
            print("X wins. ")
        elif 3 == game_status:
            print("User shut down. ")
        else:
            print("O wins. ")


class player:
    def __init__(self, is_o):
        self.is_o = is_o
        self.elaspled_time = 0.

    def get_strategy(self, board):
        raise AttributeError("get_strategy method has not implemented in this player object. ")

    def get_elapsed_time(self):
        return str(datetime.timedelta(seconds=int(self.elaspled_time)))

class human_player(player):
    def __init__(self, is_o):
        super().__init__(is_o)
        self.name = "human"
        self.key_map = dict()
        self.key_map["u"] = (0,0)
        self.key_map["i"] = (0,1)
        self.key_map["o"] = (0,2)
        self.key_map["j"] = (1,0)
        self.key_map["k"] = (1,1)
        self.key_map["l"] = (1,2)
        self.key_map["m"] = (2,0)
        self.key_map[","] = (2,1)
        self.key_map["<"] = (2,1)
        self.key_map["."] = (2,2)
        self.key_map[">"] = (2,2)
        self.valid_keys = self.key_map.keys()

    def get_strategy(self, board):
        time_start = time.time()
        valid_moves = board.find_all_moves()
        while True:
            key = readchar.readkey().lower()
            if key in self.valid_keys and self.key_map[key] in valid_moves:
                self.elaspled_time += time.time() - time_start
                return self.key_map[key]
            if key == 'r' and board.current_round > 0: 
                self.elaspled_time += time.time() - time_start
                return 0
            if key == 'q':
                self.elaspled_time += time.time() - time_start
                return 1

class ai_player(player):
    def __init__(self, is_o, strength = 1.):
        super().__init__(is_o)
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
    game = shell()
    game.main()

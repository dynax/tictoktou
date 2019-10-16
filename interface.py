import board
import readchar
import os

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
        if True == self.board.is_o:
            display = "\nOOO "
        else:
            display = "\nXXX "
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
            if None != dest:
                self.board.move(dest)
                if True == self.board.is_win():
                    if False == self.board.is_o:
                        game_status = 0
                    else:
                        game_status = 1
                    break
            else:
                self.board.revert_move()
        # endwhile            
        self._ending(game_status)

    def _welcome(self):
        os.system("clear")
        display  = "\n\n\n"
        display += "**************************************************\n" 
        display += "               Welcome to TicTokTou!              \n"
        display += "**************************************************\n"
        print(display)
        # set players
        self.o_player = human_player(True)
        self.x_player = human_player(False)
        readchar.readkey()

    def _display_control(self):
        display  = "Use one of the following keys to put a piece on: \n"
        display += "   UIO\n"
        display += "   JKL\n"
        display += "   M,.\n"
        display += "Revert with R.\n"
        print(display) 

    def _ending(self, game_status):
        self.display_board()
        if 2 == game_status:
            print("Draw game. ")
        elif 1 == game_status:
            print("X wins. ")
        else:
            print("O wins. ")



class player:
    def __init__(self, is_o):
        self.is_o = is_o

    def get_strategy(self, board):
        raise AttributeError("get_strategy method has not implemented in this player object. ")

class human_player(player):
    def __init__(self, is_o):
        super().__init__(is_o)
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
        valid_moves = board.find_all_moves()
        while True:
            key = readchar.readkey().lower()
            if key in self.valid_keys and self.key_map[key] in valid_moves:
                return self.key_map[key]
            if key == 'r' and board.current_round > 0: 
                return None

class ai_player(player):
    def __init__(self, is_o, strength = 1):
        super().__init__(is_o)
        self.random_prob = 1 - strength

    def get_strategy(self, board):
        pass

  

if __name__ == "__main__":
    game = shell()
    game.main()

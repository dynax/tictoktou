import random
import time
random.seed(time.time())

class absearch:
    def __init__(self):
        pass

    def get_strategy(self, board):
        possible_moves = board.find_all_moves()
        random.shuffle(possible_moves)
        dest = possible_moves[0]
        best_val = -10
        for each_move in possible_moves:
            board.move(each_move)
            each_val = self._search(board, best_val)
            board.revert_move()
            if each_val > best_val:
                best_val = each_val
                dest = each_move
            # print(board.current_round, each_move, each_val, best_val)
        return dest

    def _search(self, board, current_max):
        if True == board.is_win():
            return 1
        if board.current_round >= 9:
            return 0
        possible_moves = board.find_all_moves()
        random.shuffle(possible_moves)
        best_val = -10
        for each_move in possible_moves:
            board.move(each_move)
            each_val = self._search(board, best_val)
            board.revert_move()
            # print(board.current_round, each_move, each_val, best_val)
            if - each_val <= current_max:
                return -each_val
            elif each_val >best_val:
                best_val = each_val

        return -best_val


import numpy as np

class board:
    def __init__(self, moves=None):
        self.reset_board()
        self._set_aug_functions()
        if None == moves:
            self.moves = [None] * 9
        else:
            self.moves = moves

    def reset_board(self):
        self.o = np.zeros([3,3])
        self.x = np.zeros([3,3])
        self.current_round = 0
        self.is_o = True

    def move(self, dest):
        try: 
            assert isinstance(dest, tuple)
        except:
            dest = tuple(dest)
        if True == self.is_o:
            self.o[dest] = 1
        else:
            self.x[dest] = 1
        self.moves[self.current_round] = dest
        self.current_round += 1
        self.is_o = not self.is_o

    def revert_move(self):
        try:
            dest = self.moves[self.current_round-1]
        except:
            raise ValueError("You cannot revert in the first round. ")
        if False == self.is_o:
            self.o[dest] = 0
        else:
            self.x[dest] = 0
        self.current_round -= 1
        self.is_o = not self.is_o

    def find_all_moves(self):
        occupied = self.o + self.x
        valid = np.where(occupied == 0)
        return list(zip(valid[0], valid[1]))

    def is_win(self):
        last_move = self.moves[self.current_round-1]
        if False == self.is_o:
            current_board = self.o
        else:
            current_board = self.x
        res = 0
        for m, n in self.check[last_move]:
            res += current_board[m] * current_board[n]
        return res

    # to speed up the is_win, manually write all the possible cases
    def _set_aug_functions(self):
        self.check = dict()
        self.check[(0,0)] = [[(1,0),(2,0)], [(1,1),(2,2)], [(0,1),(0,2)]]
        self.check[(0,1)] = [[(0,0),(0,2)], [(1,1),(2,1)]]
        self.check[(0,2)] = [[(0,0),(0,1)], [(1,1),(2,0)], [(1,2),(2,2)]]
        self.check[(1,0)] = [[(0,0),(2,0)], [(1,1),(1,2)]]
        self.check[(1,1)] = [[(1,0),(1,2)], [(0,1),(2,1)], [(0,0),(2,2)], [(0,2),(2,0)]]
        self.check[(1,2)] = [[(1,0),(1,1)], [(0,2),(2,2)]]
        self.check[(2,0)] = [[(0,0),(1,0)], [(1,1),(0,2)], [(2,1),(2,2)]]
        self.check[(2,1)] = [[(0,1),(1,1)], [(2,0),(2,2)]]
        self.check[(2,2)] = [[(2,0),(2,1)], [(1,1),(0,0)], [(0,2),(1,2)]]

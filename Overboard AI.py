import copy
import sys
import random

import numpy as np

inf = float('inf')
directions = ('left', 'right', 'down', 'up')
p1_init_peices = 18
p2_init_peices = 18
difficulty = 4

# 1 is B, 2 is R, 0 is empty
init_board = np.array([[1, 1, 2, 1, 1, 2],
                       [2, 2, 1, 1, 1, 2],
                       [2, 2, 1, 2, 2, 1],
                       [1, 2, 2, 1, 2, 2],
                       [2, 1, 1, 1, 2, 2],
                       [2, 1, 1, 2, 1, 1]])


class OverboardState:
    
    def __init__(self, board, parent=None):
        self.board = board
        self.size = 6
        if parent is None:
            self.p1_peices = p1_init_peices
            self.p2_peices = p2_init_peices
            self.parent = None
        else:
            self.p1_peices = parent.p1_peices
            self.p2_peices = parent.p2_peices
            self.parent = parent
        self.children = []

    def shift_tiles(self, v, pos, tiles):
        if tiles < 0:
            return self.shift_tiles(v[::-1], len(v) - pos - 1, -tiles)[::-1]
        elif tiles < len(v) - pos:
            idx = np.where(np.cumsum(v[pos + 1:] == 0) == tiles)[0]
            last_zero_idx = idx[0] if len(idx) > 0 else len(v) - pos - 1
            # Get non-empty values
            v_slice = v[pos + 1:pos + last_zero_idx + 1]
            values = v_slice[np.where(v_slice != 0)[0]]
            # Copy to vector
            v[pos + tiles] = v[pos]
            r = range(pos + tiles + 1, min(pos + 2 + last_zero_idx, len(v)))
            v[r] = values[:len(r)]
        v[pos:pos + tiles] = 0
        return v

    def move_tile(self, y, x, direction, tiles):
        if direction == 'down':
            self.board[:, x] = self.shift_tiles(self.board[:, x], y, tiles)
        elif direction == 'up':
            self.board[:, x] = self.shift_tiles(self.board[:, x], y, -tiles)
        elif direction == 'right':
            self.board[y, :] = self.shift_tiles(self.board[y, :], x, tiles)
        elif direction == 'left':
            self.board[y, :] = self.shift_tiles(self.board[y, :], x, -tiles)

    def count_elems(self, v, tiles, pId):
        pTiles, oTiles, emptyTiles = 0, 0, 0
        myLast = -1
        for i in range(0, v.shape[0]):
            if v[i] == pId:
                myLast = i
                pTiles += 1
            elif v[i] == 0:
                emptyTiles += 1
            else:
                oTiles += 1
        return (pTiles, oTiles, emptyTiles, myLast)

    def is_move_valid(self, y, x, tiles, direction, pId):
        elems, elemsAfter = None, None
        if self.board[y, x] != pId:
            return False
        if direction == 'up' or direction == 'down':
            #if y - tiles >= 0 and y + tiles < self.size:
            if tiles > 0 and tiles < self.size:
                elems = self.count_elems(self.board[:, x], tiles, pId)
                test = OverboardState(self.board.copy(), self)
                test.move_tile(y, x, direction, tiles)
                elemsAfter = self.count_elems(test.board[:, x], tiles, pId)
            else:
                return False
        elif direction == 'left' or direction == 'right':
            #if x - tiles >= 0 and x + tiles < self.size:
            if tiles > 0 and tiles < self.size:
                elems = self.count_elems(self.board[y, :], tiles, pId)
                test = OverboardState(self.board.copy(), self)
                test.move_tile(y, x, direction, tiles)
                elemsAfter = self.count_elems(test.board[y, :], tiles, pId)
            else:
                return False
        else:
            return False
        return elems[0] >= elemsAfter[0]

    def __str__(self):
        board = self.board.flatten()
        X = self.size
        out = ''
        for i in range(0, len(board)):
            s = ''
            if i % X == 0 and i != 0:
                out += '\n'
            if board[i] == 1:
                s += 'B'
            elif board[i] == 2:
                s += 'R'
            elif board[i] == 0:
                s += '-'
            out += s
        return out


class OverboardPlayer:
    def __init__(self, ptype, pId):
        self.ptype = ptype.lower()
        self.pId = pId
        self.nodeNum = 0
        if self.pId == 1:
            self.oId = 2
        elif self.pId == 2:
            self.oId = 1
        else:
            raise ValueError('OverboardPlayer: Invalid pID')

    def proc_turn(self, state):
        raise NotImplementedError('proc_turn')

    def count_peices(self, state, pId):
        pTiles, oTiles, emptyTiles = 0, 0, 0
        for i in range(0, state.size):
            for j in range(0, state.size):
                if state.board[i, j] == pId:
                    pTiles += 1
                elif state.board[i, j] == 0:
                    emptyTiles += 1
                else:
                    oTiles += 1
        return (pTiles, oTiles, emptyTiles)


class OverboardHummanPlayer(OverboardPlayer):
    def proc_turn(self, board):
        raise NotImplementedError('Human Player')


class OverboardRandomPlayer(OverboardPlayer):
    def proc_turn(self, state):
        move = None
        while not move:
            if not self.can_make_move(state):
                return None 
            x = random.randint(0, state.size-1)
            y = random.randint(0, state.size-1)
            tiles = random.randint(1, state.size-1)
            direction = directions[random.randint(0, 3)]
            if state.is_move_valid(y, x, tiles, direction, self.pId):
                move = OverboardState(state.board.copy(), state)
                move.move_tile(y, x, direction, tiles)
        return move

    def can_make_move(self, state):
        for tiles in range(1, state.size):
            for i in range (0, state.size):
                for j in range(0, state.size):
                    for direction in directions:
                        if state.is_move_valid(i, j, tiles, direction, self.pId):
                            return True
        return False
                        



class OverboardMMPlayer(OverboardPlayer):
    def heuristic(self, state, pId):
        raise NotImplementedError('heuristic')

    # Proc turn with minimax and alpha-beta pruning
    def proc_turn(self, state, depth=-1):
        return self.findmove(state, depth=difficulty)

    def findmove(self, state, depth=-1):
        alpha = -inf 
        beta = inf
        move = None
        for child in self.get_successors(state, self.pId):
            val = self.min_val(state, alpha, beta, depth - 1)
            if val > alpha:
                alpha = val
                move = child
        return move

    def max_val(self, state, alpha, beta, depth):
        if self.is_terminal(state) or depth == 0:
            return self.heuristic(state, self.pId)
        val = -inf
        for child in self.get_successors(state, self.pId):
            val = max(val, self.min_val(child, alpha, beta, depth - 1))
            if val >= beta: return val
            alpha = max(alpha, val)
        return val

    def min_val(self, state, alpha, beta, depth):
        if self.is_terminal(state) or depth == 0:
            return self.heuristic(state, self.oId)
        val = inf
        for child in self.get_successors(state, self.pId):
            val = min(val, self.max_val(child, alpha, beta, depth - 1))
            if val <= alpha: return val
            beta = min(beta, val)
        return val

    def get_successors(self, state, pId):
        children, moves = [], []
        for tiles in range(1, state.size):
            for i in range(0, state.size):
                for j in range(0, state.size):
                    for direction in directions:
                            moves.append(self.move(state, i, j, tiles, direction, pId))
                            self.nodeNum += 1
        for move in moves:
            if move:
                children.append(move)
        state.children = children
        return children

    def move(self, state, y, x, tiles, direction, pId):
        move = None
        if direction in directions:
            if state.is_move_valid(y, x, tiles, direction, pId):
                move = OverboardState(state.board.copy(), state)
                move.move_tile(y, x, direction, tiles)
        return move

    def is_terminal(self, state):
        return not state.children


class OverboardMM1Player(OverboardMMPlayer):
    def heuristic(self, board, pId):
        peices = self.count_peices(board, pId)
        if pId == self.pId:
            return abs(peices[0] - peices[1])
        else:
            return -abs(peices[0] - peices[1])


class OverboardMM2Player(OverboardMMPlayer):
    def heuristic(self, board, pId):
        peices = self.count_peices(board, pId)
        if pId == self.pId:
            return peices[0]
        else:
            return -peices[0]


class OverboardView:
    def __init__(self, game):
        self.game = game

    def get_game_type(self):
        while True:
            print('What type of game would you like to play (h for options)?')
            selection = input('> ')
            selection = selection.lower()
            if selection == 'h':
                print('Options: [mm vs ran] or [mm vs mm]')
            elif selection == 'mm vs ran':
                return 'game1'
            elif selection == 'mm vs mm':
                return 'game2'
            else:
                print('Try again')

    def print_game_header(self):
        current = self.game.get_current_player()
        print('Player {}\'s turn ({})'.format(current.pId, current.ptype))

    def print_game_footer(self):
        print('node num: {} \n'.format(self.game.previous_player.nodeNum))

    def print_board_state(self):
        print(self.game.state)

    def print_game(self):
        self.print_game_header()
        self.print_board_state()
        self.print_game_footer()

    def print_game_over(self, winner, scores):
        p1 = self.game.player1
        p2 = self.game.player2
        print('=====GAME OVER=====')
        print('Player {} ({}) Wins!'.format(winner.pId, winner.ptype))
        if p1 is winner:
            print('Final score: {}'.format(scores[0]))
        elif p2 is winner:
            print('Final score: {}'.format(scores[1]))


class OverboardGame:
    def __init__(self, board):
        self.state = OverboardState(board, None)
        self.view = OverboardView(self)
        self.current_player = None
        self.previous_player = None
        self.winner = None
        self.turnNum = 0

    def setup(self):
        selection = self.view.get_game_type()
        if selection == 'game1':
            self.player1 = OverboardMM1Player('heuristic1', 1)
            self.player2 = OverboardRandomPlayer('ran', 2)
        elif selection == 'game2':
            self.player1 = OverboardMM1Player('heuristic1', 1)
            self.player2 = OverboardMM2Player('heuristic2', 2)

    def run(self):
        while not self.is_game_over():
            self.current_player = self.get_next_player()
            self.turn(self.current_player)
            self.view.print_game()
        finalScores = self.count_peices()
        if finalScores[0] == 0:
            self.winner = self.player2
        elif finalScores[1] == 0:
            self.winner = self.player1
        self.view.print_game_over(self.winner, finalScores)

    def turn(self, player):
        self.turnNum += 1
        move = player.proc_turn(self.state)
        if move is None:
            raise ValueError('AI Cannot Generate a Move. Check Production System')
        self.state = OverboardState(move.board.copy(), None)

    def get_next_player(self):
        if self.current_player is self.player1:
            self.previous_player = self.player1
            return self.player2
        else:
            self.previous_player = self.player2
            return self.player1

    def get_current_player(self):
        return self.current_player

    def is_game_over(self):
        scores = self.count_peices()
        return scores[0] == 0 or scores[1] == 0

    def count_peices(self):
        board = self.state.board
        p1Score, p2Score, empty = 0, 0, 0
        for i in range(0, board.shape[0]):
            for j in range(0, board.shape[1]):
                if board[i, j] == self.player1.pId:
                    p1Score += 1
                elif board[i, j] == self.player2.pId:
                    p2Score += 1
                else:
                    empty += 1
        return (p1Score, p2Score, empty)


def main():
    game = OverboardGame(init_board)
    game.setup()
    game.run()


if __name__ == '__main__': main()

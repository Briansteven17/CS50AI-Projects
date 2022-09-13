"""
Tic Tac Toe Player
"""

from audioop import add
from copy import deepcopy
from decimal import ROUND_DOWN
import math
from zoneinfo import available_timezones

X = "X"
O = "O"
EMPTY = None

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    numberO = 0
    numberX = 0

    for row in board:
        for cell in row:
            if cell == X:
                numberX += 1
            elif cell == O:
                numberO += 1

    if numberO == numberX:
        return X
    else:
        return O
    
    # raise NotImplementedError


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set ()

    row_number = -1
    for row in board:
        row_number += 1
        cell_number = 0
        for cell in row:
            if cell != X and cell != O:
                actions.add((row_number, cell_number))
            cell_number += 1

    return actions 

    # raise NotImplementedError


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    available = actions(board)

    if not action in available:
        raise NameError('This cell is not available')

    current_player = player(board)
    new_board = deepcopy(board)

    row = action[0]
    cell = action[1]

    new_board[row][cell] = current_player

    return new_board

    # raise NotImplementedError


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    rowN = -1
    for row in board:
        rowN += 1
        cellN = 0
        
        rowX, rowO, colX, colO = 0, 0, 0, 0
        cruz1X, cruz1O, cruz2X, cruz2O = 0, 0, 0, 0
        for cell in row:
            if board[rowN][cellN] == X:
                rowX += 1
            elif board[rowN][cellN] == O:
                rowO += 1
            if board[cellN][rowN] == X:
                colX += 1
            elif board[cellN][rowN] == O:
                colO += 1

            if rowN == 0:
                if board[cellN][cellN] == X:
                    cruz1X += 1
                elif board[cellN][cellN] == O:
                    cruz1O += 1
                if board[2 - cellN][cellN] == X:
                    cruz2X += 1
                elif board[2 - cellN][cellN] == O:
                    cruz2O += 1
            cellN += 1
        if 3 in (rowX, colX, cruz1X, cruz2X):
            return X
        elif 3 in (rowO, colO, cruz1O, cruz2O):
            return O

    return None

    # raise NotImplementedError


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    count = 0
    for row in board:
        if EMPTY in row:
            count += 1

    if winner(board) != None:
        return True
    elif count == 0:
        return True   

    return False

    # raise NotImplementedError


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    state = winner(board)
    if state == X:
        return 1
    elif state == O:
        return -1
    else:
        return 0

    # raise NotImplementedError


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    if terminal(board) == True:
        return None

    if player(board) == X:
        v = -math.inf
        max_action = set ()
        for action in actions(board):
            max = evaluate(result(board, action))
            max_action.add((max, action))
            if max == 1:
                break

        for i in range(0, 3, 1):
            for max, action in max_action:
                if max == 1 and i == 1:
                    return action
                elif max == 0 and i == 2:
                    return action
                elif max == -1 and i == 3:
                    return action
            


    elif player(board) == O:
        v = math.inf
        mini_action = set()
        for action in actions(board):
            mini = evaluate(result(board, action))
            mini_action.add((mini, action))
            if mini == -1:
                break

        for i in range(0, 3, 1):
            for mini, action in mini_action:
                if mini == -1 and i == 1:
                    return action
                elif mini == 0 and i == 2:
                    return action
                elif mini == 1 and i == 3:
                    return action

def evaluate(board):

    if terminal(board) == True:
        return utility(board)

    if player(board) == X:
        v = -math.inf
        for action in actions(board):
            v = max(v, evaluate(result(board, action)))
            if v == 1:
                break
        return v

    elif player(board) == O:
        v = math.inf
        for action in actions(board):
            v = min(v, evaluate(result(board, action)))
            if v == -1:
                break
        return v




    # raise NotImplementedError

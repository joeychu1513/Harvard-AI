"""
Tic Tac Toe Player
"""

import math
import copy
from telnetlib import X3PAD
from tkinter.tix import X_REGION

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
    # return [[EMPTY, X, EMPTY],
    #         [EMPTY, EMPTY, O],
    #         [EMPTY, X, O]]
    # return [[X, X, EMPTY],
    #         [EMPTY, EMPTY, O],
    #         [EMPTY, X, O]]

def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # raise NotImplementedError

    # count number of X and O            
    count_of_X = 0
    count_of_O = 0

    for row in board:
        for column in row:
            if column == X:
                count_of_X += 1
            elif column == O:
                count_of_O += 1
    
    # X makes the first move

    if count_of_X > count_of_O:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # raise NotImplementedError

    actions = set()

    for i, row in enumerate(board):
        for j, column in enumerate(row):
            if column == EMPTY:
                actions.add((i, j))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # raise NotImplementedError

    action_row = action[0]
    action_column = action[1]

    if board[action_row][action_column] != EMPTY:
        raise Exception("invalud action")
    
    player_now = player(board)
    new_board = copy.deepcopy(board)
    new_board[action_row][action_column] = player_now

    return new_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # raise NotImplementedError

    # check if any row win
    for row in board:
        if row[0] == row[1] and row[1] == row[2]:
            return row[0]

    # check if any column win
    for j in range(3):
        if board[0][j] == board[1][j] and board[1][j] == board[2][j]:
            return board[0][j]

    # check if any diagonal win
    if board[0][0] == board[1][1] and board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] == board[1][1] and board[1][1] == board[2][0]:
        return board[0][2]

    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # raise NotImplementedError

    if winner(board) is not None:
        print(winner(board))
        return True
    for row in board:
        for column in row:
            if column == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # raise NotImplementedError

    winner_now = winner(board)
    if winner_now is X:
        return 1
    elif winner_now is O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # raise NotImplementedError

    if terminal(board) is True:
        return None

    # initial setting
    player_now = player(board)
    actions_now = actions(board)

    # max-min
    if player_now == X:

        optimal_action = None
        optimal_utility = float('-inf')


        for action in actions_now:
            new_board = result(board, action)
        
            if terminal(new_board) is True:
                if utility(new_board) > optimal_utility:
                    optimal_utility = utility(new_board)
                    optimal_action = action

            else:
                while terminal(new_board) is False:
                    new_board = result(new_board, minimax(new_board))
                    if terminal(new_board) is True and utility(new_board) > optimal_utility:
                        optimal_utility = utility(new_board)
                        optimal_action = action


    # min-max
    if player_now == O:

        optimal_action = None
        optimal_utility = float('inf')

        for action in actions_now:
            new_board = result(board, action)
            if terminal(new_board) is True:
                if utility(new_board) < optimal_utility:
                    optimal_utility = utility(new_board)
                    optimal_action = action

            else:
                while terminal(new_board) is False:
                    new_board = result(new_board, minimax(new_board))
                    if terminal(new_board) is True and utility(new_board) < optimal_utility:
                        optimal_utility = utility(new_board)
                        optimal_action = action

    return optimal_action
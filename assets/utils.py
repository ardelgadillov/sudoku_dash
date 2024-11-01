import copy
import random
from itertools import islice

from dash import Dash, dcc, html, Input, Output, callback


def sudoku_line(base, board, box, line):
    color = {0: 'lightCell',
             1: 'darkCell'}

    regex = {2: '[1-4]',
             3: '[1-9]',
             4: '[1-9]|1[0-6]',
             5: '[1-9]|1[0-9]|2[0-5]',
             6: '[1-9]|1[0-9]|2[0-9]|3[0-6]',
             7: '[1-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]',
             8: '[1-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9]|6[0-4]',
             9: '[1-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9]|6[0-9]|7[0-9]|8[0-1]',
             10: '[1-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9]|6[0-9]|7[0-9]|8[0-9]|9[0-9]|100'}
    if base <= 3:
        max_len = 1
    elif base < 10:
        max_len = 2
    else:
        max_len = 3

    return [dcc.Input(className='cell ' + color[(base * (board + box) + line + col) % 2],
                      id=f'{base * board + line}-{base * box + col}', maxLength=max_len, pattern=regex[base],
                      type='text', inputMode='numeric')
            for col in range(base)]


def sudoku_box_line(base, board, box):
    return [html.Div(className='row', children=sudoku_line(base, board, box, row)) for row in range(base)]


def sudoku_box(base, board):
    return [html.Div(className='box', children=sudoku_box_line(base, board, box)) for box in range(base)]


def sudoku_board(side):
    base = int(side ** 0.5)
    return [html.Div(className='row', children=sudoku_box(base, board)) for board in range(base)]


def pattern(r, c, base):
    return (base * (r % base) + r // base + c) % (base * base)


def shuffle(s):
    return random.sample(s, len(s))


def fast_check(board, base):
    side = base * base
    board_x = [n for row in board for n in row]
    blanks = [i for i, n in enumerate(board_x) if n == 0]
    cover = {(n, i): {*zip([2 * side + r, side + c, r // base * base + c // base], [n] * (n and 3))}
             for i in range(side * side) for r, c in [divmod(i, side)] for n in range(side + 1)}
    used = set().union(*(cover[n, i] for i, n in enumerate(board_x) if n))
    placed = 0
    while 0 <= placed < len(blanks):
        pos = blanks[placed]
        used -= cover[board_x[pos], pos]
        board_x[pos] = next((n for n in range(board_x[pos] + 1, side + 1) if not cover[n, pos] & used), 0)
        used |= cover[board_x[pos], pos]
        placed += 1 if board_x[pos] else -1
        if placed == len(blanks):
            solution_x = [board_x[r:r + side] for r in range(0, side * side, side)]
            yield solution_x
            placed -= 1


def generate_random_sudoku(base, difficult):
    side = base * base
    range_base = range(base)
    # shuffle numbers
    rows = [g * base + r for g in shuffle(range_base) for r in shuffle(range_base)]
    cols = [g * base + c for g in shuffle(range_base) for c in shuffle(range_base)]
    nums = shuffle(range(1, base * base + 1))

    # produce board using randomized baseline pattern
    board = [[nums[pattern(r, c, base)] for c in cols] for r in rows]
    # copy solution
    solution = copy.deepcopy(board)
    # print('solution')
    # for line in solution:
    #     print(line)

    squares = side * side
    empties = int(squares * difficult)
    # print(empties)
    for p in random.sample(range(squares), empties):
        board[p // side][p % side] = 0

    # print('board')
    # for line in board:
    #     print(line)

    if base <= 4:
        solved = [*islice(fast_check(board, base), 2)]
        # print(len(solved))
        while len(solved) > 1:
            # print(len(solved))
            diff_pos = [(r, c) for r in range(side) for c in range(side) if solved[0][r][c] != solved[1][r][c]]
            r, c = random.choice(diff_pos)
            board[r][c] = solution[r][c]
            solved = [*islice(fast_check(board, base), 2)]
            # print(len(solved))

    # numSize = len(str(side))
    # for line in board:
    #     print(*(f"{n or '.':{numSize}} " for n in line))

    return board

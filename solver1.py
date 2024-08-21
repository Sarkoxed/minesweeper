from mineboard import MineBoard
from z3 import Solver, Int, sat, Or
from termcolor import colored
import myboard

board = MineBoard(myboard.board_str)
print(board)
print()
valid = board.partial_check()
print("Is valid?: ", valid)
if not valid:
    exit()
print()

def symbolic_board(board, tag):
    n, m = board.dimensions
    new_board = [[(None, 0) for _ in range(m)] for _ in range(n)]
    syms = []
    
    for i in range(n):
        for j in range(m):
            minibox = board.get_surrounding_box(i, j)
            if all(board.map_[x[0]][x[1]][0] in [None, -1] for y in minibox for x in y):
                continue
            if board.map_[i][j][0] is None:
                new_board[i][j] = (0, Int(f"x_{i}_{j}_{tag}"))
                syms.append((new_board[i][j][1], (i, j)))
            else:
                new_board[i][j] = board.map_[i][j]
    return new_board, syms

def get_surrounding_box(i, j, dimensions):
    box = [
        [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1)],
        [(i, j - 1), (i, j), (i, j + 1)],
        [(i + 1, j - 1), (i + 1, j), (i + 1, j + 1)],
    ]
    if i == 0:
        box = box[1:]
    elif i == dimensions[0] - 1:
        box = box[:-1]

    if j == 0:
        box = [x[1:] for x in box]
    elif j == dimensions[1] - 1:
        box = [x[:-1] for x in box]

    return box

def make_assertion(map_, i, j):
    if map_[i][j][0] is None or map_[i][j][0] == -1 or map_[i][j][0] == 0:
        return None
    
    dimensions = (len(map_), len(map_[0]))
    box = get_surrounding_box(i, j, dimensions)

    res = sum(
        [
            map_[x[0]][x[1]][1]
            for y in box
            for x in y
            if x != (i, j) and map_[x[0]][x[1]] is not None
        ]
    )
    return res == map_[i][j][0]



def init_symbolic_board(s, board, board_tag):
    new_board, variables = symbolic_board(board, board_tag)

    for v, _ in variables:
        s.add(Or(v == 0, v == 1))

    dimensions = (len(new_board), len(new_board[0]))
    for i in range(dimensions[0]):
        for j in range(dimensions[1]):
            tmp = make_assertion(new_board, i, j)
            if tmp is not None:
                s.add(tmp)
    s.add(sum([v for v, _ in variables]) <= myboard.bombs_left)
    return new_board, variables

_, variables = symbolic_board(board, "")
nvars = len(variables)

constant_variables = []
for i in range(nvars):
    s = Solver()
    _, variables_1 = init_symbolic_board(s, board, "board_1")
    _, variables_2 = init_symbolic_board(s, board, "board_2")

    s.add(variables_1[i][0] != variables_2[i][0])
    if s.check() != sat:
        constant_variables.append(i)

if len(constant_variables) > 0:
    s = Solver()
    new_board, variables = init_symbolic_board(s, board, "")
    assert s.check() == sat
    
    subs = {None: " ", -1: "B"}
    tmp_board = [[str(x[0]) if x[0] not in subs else subs[x[0]] for x in y] for y in board.map_]

    m = s.model()
    for t in constant_variables:
        v, pos = variables[t]
        tmp_board[pos[0]][pos[1]] = colored(m[v], 'green')

    print("=" * 50)
    print("\n".join("".join(x) for x in tmp_board))
    print("=" * 50)
    print()   
else:
    no_matches = None
    total_solutions = 0
    s = Solver()
    new_board, variables = init_symbolic_board(s, board, "")
 
    while s.check() == sat:
        total_solutions += 1
        m = s.model()
        
        subs = {None: " ", -1: "B"}
        tmp_board = [[str(x[0]) if x[0] not in subs else subs[x[0]] for x in y] for y in new_board]
        new_assertion = []
    
        for v, pos in variables:
            tmp_board[pos[0]][pos[1]] = colored(m[v], 'green')
            new_assertion.append(v != m[v])
        
        if myboard.log == 1:
            print("=" * 50)
            print("Bombs found: ", [str(m[v]) for v, _ in variables].count('1'))
            print("\n".join("".join(x) for x in tmp_board))
            print("=" * 50)
            print()
        elif myboard.log == 2: 
            print("=" * 50)
            print("Bombs found: ", [str(m[v]) for v, _ in variables].count('1'))
            print([m[v] for v, _ in variables])
            print("=" * 50)
    
        compare = [(str(m[v]), pos) for v, pos in variables]
        if no_matches is None:
            no_matches = [int(x[0]) for x in compare]
        else:
            for i in range(len(no_matches)):
                no_matches[i] += int(compare[i][0]) # counting the amount of ones in the particular cell. That's simple probability that doesn't care about the surroundings
    
        s.add(Or(new_assertion))
    
    subs = {None: " ", -1: "B"}
    tmp_board = [[str(x[0]) if x[0] not in subs else subs[x[0]] for x in y] for y in board.map_]
    
    print("Unfortunately you have to guess now. Here're the probabilities that there's no bomb in certain cell: ")
    for match_number, varpos in zip(no_matches, variables):
        pos = varpos[1]
         
        prob = round( (total_solutions - match_number) * 1000 / total_solutions) / 10
    
        tmp_board[pos[0]][pos[1]] = colored(str(prob)[::-1].zfill(4)[::-1], 'green')
    
    print("=" * 50)
    print("\n".join(" | ".join([t.rjust(4) for t in x]) for x in tmp_board))
    print("=" * 50)
    print()

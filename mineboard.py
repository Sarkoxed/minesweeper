from typing import Optional
from termcolor import colored


class MineBoard:
    def __init__(self, num_map: Optional[str] = None):
        if isinstance(num_map, str):
            self.parse_board(num_map)
        else:
            self.dimensions = (0, 0)
            self.map_ = None

    def parse_board(self, num_map: str):
        num_map_list = num_map.strip().split("\n")
        n = len(num_map_list)
        m = len(num_map_list[0])
        assert n * m == len(num_map.strip()) - n + 1 # \n's

        map_ = [[(None, -1) for _ in range(m)] for _ in range(n)]
        self.dimensions = (n, m)

        for i, line in enumerate(num_map_list):
            for j, col in enumerate(line):
                if col == "#":
                    continue
                elif col.isdecimal():
                    map_[i][j] = (int(col), 0)
                elif col == "b":
                    map_[i][j] = (-1, 1)
        self.map_ = map_

    def get_surrounding_box(self, i, j):
        box = [
            [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1)],
            [(i, j - 1), (i, j), (i, j + 1)],
            [(i + 1, j - 1), (i + 1, j), (i + 1, j + 1)],
        ]
        if i == 0:
            box = box[1:]
        elif i == self.dimensions[0] - 1:
            box = box[:-1]

        if j == 0:
            box = [x[1:] for x in box]
        elif j == self.dimensions[1] - 1:
            box = [x[:-1] for x in box]

        return box
   
    def is_valid_box(self, i, j):
        if self.map_[i][j][0] is None or self.map_[i][j][1] == 1:
            return True

        box = self.get_surrounding_box(i, j)

        res = sum(
            [
                self.map_[x[0]][x[1]][1]
                for y in box
                for x in y
                if x != (i, j) and self.map_[x[0]][x[1]][0] is not None
            ]
        )
        return res <= self.map_[i][j][0]

    def partial_check(self):
        assert self.map_ is not None

        for i in range(self.dimensions[0]):
            for j in range(self.dimensions[1]):
                if self.is_valid_box(i, j):
                    continue
                else:
                    tmp = str(self).split('\n')
                    tmp[i] = tmp[i][:j] + colored(tmp[i][j], 'red') + tmp[i][j+1:]
                    print("\n".join(tmp))
                    return False
        return True

    def __str__(self):
        subs = {-1: "@", None: " "}
        return "\n".join(
            "".join(subs[x[0]] if x[0] in subs else str(x[0]) for x in y)
            for y in self.map_
        )

    def __repr__(self):
        return str(self) + '\n'

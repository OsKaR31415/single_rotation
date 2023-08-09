#!python3
import numpy as np
from random import random
from grid_printer import GridPrinter
from os import get_terminal_size


class Grid():
    def __init__(self, width: int, height: int, proportion: float =.3):
        self.width = 2 * int(width) // 2
        self.height = 2 * int(height) // 2
        self.grid = [[False for _ in range(self.width)]
                     for _ in range(self.height)]
        self.random_grid(proportion)
        self.update_center()

    def set_grid(self, new_grid: list[list[bool]]):
        assert len(new_grid) == self.height
        assert all(len(line) == self.width for line in new_grid)
        self.grid = new_grid

    def random_grid(self, proportion: float =.3):
        self.set_grid([[random() < proportion for _ in range(self.width)]
                       for _ in range(self.height)])

    def random_grid_circle(self, radius: int, proportion: float =.3):
        self.set_grid([[(i**2 + j**2 < radius**2) * (random() < proportion) for i in range(self.width)]
                       for j in range(self.height)])
        self.update_center()

    def __getitem__(self, idx: int):
        return self.grid[idx % self.height]

    def get_item(self, y: int, x: int) -> bool:
        grid_at_idx = self.grid[y % self.height][x % self.width]
        # make sure to get only 0 for False, and only 1 for True
        # important since i inject other values to mark the center
        value = bool(grid_at_idx == 1)
        if np.all([y, x] == self.center):
            return 10 + value
        return bool(grid_at_idx == 1)

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def get_subgrid(self, shift: int):
        width, height = self.width // 2, self.height // 2
        subgrid = [[0 for _ in range(width)] for _ in range(height)]
        for y in range(height):
            for x in range(width):
                Y = shift + 2 * y
                X = shift + 2 * x
                cell = Grid(2, 2)
                cell.set_grid([[self.get_item(Y, X),   self.get_item(Y, X+1)],
                               [self.get_item(Y+1, X), self.get_item(Y+1, X+1)]])
                subgrid[y][x] = cell
        return subgrid

    def set_from_subgrid(self, subgrid):
        def get_elt(y: int, x: int) -> bool:
            return subgrid[y//2][x//2][y%2][x%2]
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = get_elt(y, x)

    def roll(self):
        self.grid = np.array(self.grid)
        self.grid = np.roll(self.grid, 1, axis=0)
        self.grid = np.roll(self.grid, 1, axis=1)

    def step(self, shift: int =0):
        sub = self.get_subgrid(shift=shift)
        sub = rotate_subgrid(sub)
        self.set_from_subgrid(sub)
        if shift:
            self.roll()

    def get_center(self):
        point_vectors = np.transpose(np.where(np.array(self.grid)))
        return np.round(np.sum(point_vectors, axis=0) / len(point_vectors))

    def update_center(self):
        # self.center = (0, 0)
        self.center = self.get_center()

    def __str__(self) -> str:
        res = ""
        for line in self.grid:
            for elt in line:
                res += "▒▒" if elt else "  "
            res += "\n"
        return res

def rotate_cell(cell: Grid) -> Grid:
    new_cell = Grid(2, 2)
    new_cell.set_grid([[cell[0][1], cell[1][1]],
                       [cell[0][0], cell[1][0]]])
    return new_cell


def single_rotation(cell: Grid) -> Grid:
    if sum((cell[0][0] == 1, cell[0][1] == 1, cell[1][0] == 1, cell[1][1] == 1)) == 1:
        # print("single:\n", cell)
        return rotate_cell(cell)
    # print("not single:\n", cell)
    return cell


def rotate_subgrid(sub: list[list[Grid]]) -> list[list[Grid]]:
    new_sub = [[False for _ in range(len(sub[ln]))]
               for ln in range(len(sub))]
    for ln, line in enumerate(sub):
        for col, cell in enumerate(line):
            new_sub[ln][col] = single_rotation(cell)
    return new_sub

if __name__ == "__main__":
    width, height = get_terminal_size()
    G = Grid((width - 2)//2, height - 3)
    G.random_grid_circle(radius=20, proportion=.3)
    printer = GridPrinter(delay=.00)
    while True:
        # for _ in range(1):
        G.step(0)
        printer(G)
        G.step(1)
        printer(G)
        G.update_center()


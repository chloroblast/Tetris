import numpy as np
import copy
import random


class Grid:
    def __init__(self, configurations, x=10, y=24):
        self.configurations = configurations
        self.cci = 0  # current configuration index (affected by rotation)
        self.current_configuration = self.configurations[self.cci]
        self.frozen = []  # static pieces configuration
        self.x = x  # grid width
        self.y = y  # grid height
        self.active = True  # True = movement allowed
        self.game_over = False
        self.grid = np.full((self.y, self.x), '-')  # initialization of an empty grid
        # corrections in initial configurations if grid is wider than default 10
        # grids narrower than 10 are not supported
        if self.x > 10:
            for p in range(len(self.configurations)):
                for n in range(len(self.configurations[p])):
                    if 11 <= self.configurations[p][n] <= 20:
                        self.configurations[p][n] += self.x - 10
                    elif 21 <= self.configurations[p][n] <= 30:
                        self.configurations[p][n] += 2 * (self.x - 10)

    def new_active(self, new_configurations):
        if not self.active:
            self.configurations = new_configurations
            self.cci = 0
            self.current_configuration = self.configurations[self.cci]
            self.active = True
        # if new piece can't move down: game over
        for p in self.current_configuration:
            if p + self.x in self.frozen:
                self.game_over = True

    def print(self):
        self.grid = np.full((self.y, self.x), '-')  # reset grid to empty
        for point in range(self.grid.size):  # update grid with current piece position/configuration
            if point in (self.current_configuration + self.frozen):
                self.grid[point // self.x][point % self.x] = '0'
        for row in self.grid:
            print(' '.join(row))
        print()

    def print_empty(self):
        print()
        self.grid = np.full((self.y, self.x), '-')
        for row in self.grid:
            print(' '.join(row))
        print()

    def rotate(self):
        if self.active:
            next_cci = (self.cci + 1) % (len(self.configurations))
            # check if next rotation is allowed (won't go through wall, floor, or frozen pieces)
            # tt = truth table
            tt = [(n - 1 in self.frozen) or (n + 1 in self.frozen) or (n + self.x in self.frozen)
                  or (n >= self.x * self.y) for n in self.configurations[next_cci]]
            tt1 = [(n % self.x == 0) for n in self.current_configuration]
            tt2 = [(n % self.x == self.x - 1) for n in self.configurations[next_cci]]
            tt3 = [(n % self.x == 0) for n in self.configurations[next_cci]]
            tt4 = [(n % self.x == self.x - 1) for n in self.current_configuration]
            tt.append((any(tt1) and any(tt2)) or (any(tt3) and any(tt4)) or (any(tt2) and any(tt3)))
            if not any(tt):
                self.cci = next_cci
                self.current_configuration = self.configurations[self.cci]

    def left(self):
        if self.active:
            for p in range(len(self.configurations)):
                # check for left wall or static piece contact
                tt = [(n % self.x == 0) or (n - 1 in self.frozen) for n in self.current_configuration]
                if not any(tt):
                    for n in range(len(self.configurations[p])):
                        self.configurations[p][n] -= 1

    def right(self):
        if self.active:
            for p in range(len(self.configurations)):
                # check for right wall or static piece contact
                tt = [(n % self.x == self.x - 1) or (n + 1 in self.frozen) for n in self.current_configuration]
                if not any(tt):
                    for n in range(len(self.configurations[p])):
                        self.configurations[p][n] += 1

    def down(self):
        if self.active:
            for p in range(len(self.configurations)):
                for n in range(len(self.configurations[p])):
                    self.configurations[p][n] += self.x
        # if active piece hit the floor or touched another, freeze it and update static set
        tt = [((self.x * (self.y - 1)) <= n < (self.x * self.y)) or (n + self.x in self.frozen)
              for n in self.current_configuration]
        if any(tt):
            self.frozen += self.current_configuration
            self.configurations = [[]]
            self.current_configuration = []
            self.active = False
        # if any column is completely filled: game over
        for col in range(self.x):
            tt = [(col + row * self.x) in (self.current_configuration + self.frozen) for row in range(self.y)]
            if all(tt):
                self.game_over = True

    def line_clear(self):
        # check for filled lines
        for row in range(self.y):
            tt = [n in self.frozen for n in range((row * self.x), ((row + 1) * self.x))]
            # delete filled line and shift pieces above it down
            if all(tt):
                for p in range(len(self.frozen)):
                    if self.frozen[p] < (row * self.x):
                        self.frozen[p] += self.x
                    elif (row * self.x) <= self.frozen[p] < ((row + 1) * self.x):
                        # move deleted row elements under the edge of the grid :)
                        self.frozen[p] = self.x * self.y + 1


pieces = {'O': [[4, 14, 15, 5]],
          'I': [[4, 14, 24, 34], [13, 14, 15, 16]],
          'S': [[5, 4, 14, 13], [4, 14, 15, 25]],
          'Z': [[4, 5, 15, 16], [5, 15, 14, 24]],
          'L': [[4, 14, 24, 25], [5, 15, 14, 13], [4, 5, 15, 25], [6, 5, 4, 14]],
          'J': [[5, 15, 25, 24], [15, 5, 4, 3], [5, 4, 14, 24], [4, 14, 15, 16]],
          'T': [[4, 14, 24, 15], [4, 13, 14, 15], [4, 14, 24, 13], [13, 14, 15, 24]]}


def get_dimensions():
    dimensions = input("Board dimensions [x y]: ")
    for char in dimensions:
        if char not in "0123456789 ":
            print("Dimensions should be integers!")
            dimensions = get_dimensions()
            print(dimensions)
            break
    return dimensions


dim = get_dimensions().split()
columns = int(dim[0]) if int(dim[0]) >= 10 else 10
rows = int(dim[1])
piece = random.choice("OISZLJT")

grid = Grid(copy.deepcopy(pieces[piece]), columns, rows)
grid.print_empty()
grid.print()

while True:
    command = input("[rt=rotate, l=left, r=right, d=down, exit]: ")
    if command == "rt":
        grid.rotate()
        grid.down()
    elif command == "l":
        grid.left()
        grid.down()
    elif command == "r":
        grid.right()
        grid.down()
    elif command == "d":
        grid.down()
    elif command == "exit":
        break

    if not grid.active:
        new_piece = random.choice("OISZLJT")
        grid.new_active(copy.deepcopy(pieces[new_piece]))

    grid.line_clear()
    grid.print()

    if grid.game_over:
        print("Game Over!")
        break

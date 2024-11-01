import json

import z3
from z3 import Optimize, Int, IntVector, And, Sum, Or, If


def solve():
    with open('pattern.json', 'r') as f:
        grid = json.load(f)

    grid = trim(grid)
    var_grid = [[0 for _ in range(len(grid[0]))] for _ in range(len(grid))]
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            grid[i][j] = int(grid[i][j])
            block = grid[i][j]
            if block in [1, 2]:
                var_grid[i][j] = 1
            elif block == [0, 4]:
                var_grid[i][j] = 0
            elif block == 3:
                var_grid[i][j] = -1

    for l in var_grid:
        print(l)

    sizeh, sizew = len(var_grid), len(var_grid[0])
    solver = Optimize()
    variab = [IntVector(f'row_{i}', sizew) for i in range(sizeh)]
    for i in range(sizeh):
        for j in range(sizew):
            if var_grid[i][j] in [0, -1]:
                solver.add(variab[i][j] == var_grid[i][j])
            else:
                solver.add(Or(variab[i][j] == -1, variab[i][j] == 1))
    for i in range(1, sizeh-1):
        for j in range(1, sizew-1):
            if var_grid[i][j] == 1:
                to_sum = []
                for ii in range(i-1, i+2):
                    for jj in range(j-1, j+2):
                        to_sum.append(variab[ii][jj])
                solver.add(Or([v == -1 for v in to_sum]))

    total_sum = [cell for row in variab for cell in row]
    solver.minimize(Sum([If(c == -1, 1, 0) for c in total_sum]))
    print(solver.check())
    model = solver.model()
    for i in range(sizeh):
        for j in range(sizew):
            if grid[i][j] == 1:
                if model.eval(variab[i][j], model_completion=True).as_long() == -1:
                    grid[i][j] = 5
    for l in grid:
        print(l)
    with open('solution.json', 'w') as f:
        json.dump(grid, f)

def trim(grid: list) -> list:
    x_l, x_r, y_b, y_p = 0, len(grid)-1, 0, len(grid)-1
    for i in range(len(grid)):
        if sum(grid[i]) == 0:
            y_b += 1
        else:
            break
    for i in range(len(grid) - 1, -1, -1):
        if sum(grid[i]) == 0:
            y_p -= 1
        else:
            break
    for j in range(len(grid)):
        col = [a[j] for a in grid]
        if sum(col) == 0:
            x_l += 1
        else:
            break

    for j in range(len(grid) - 1, -1, -1):
        col = [a[j] for a in grid]
        if sum(col) == 0:
            x_r -= 1
        else:
            break

    grid = [[grid[i][j] for j in range(x_l, x_r+1)] for i in range(y_b, y_p+1)]
    return grid


if __name__ == '__main__':
    solve()

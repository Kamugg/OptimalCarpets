import argparse
import json
import time
from pathlib import Path

from z3 import Optimize, And, Sum, If, BoolVector, Not, is_true, Goal, Then, Tactic


def solve(open_path: str, output_name: str, extra_constraint: bool):
    print(f'Opening {open_path}...')
    with open(open_path, 'r') as f:
        grid = json.load(f)

    grid = trim(grid)
    sizeh, sizew = len(grid), len(grid[0])
    solver = Optimize()
    goal = Goal()
    variab = [BoolVector(f'row_{i}', sizew) for i in range(sizeh)]
    spawnable = 0
    print('Preparing the solver...')
    for i in range(sizeh):
        for j in range(sizew):
            if grid[i][j] in [0, 3]:
                goal.add(variab[i][j])
            elif grid[i][j] == 2:
                goal.add(Not(variab[i][j]))
            elif grid[i][j] == 1:
                spawnable += 1
                neighbors = []
                for ii in range(i - 1, i + 2):
                    for jj in range(j - 1, j + 2):
                        # Clip to avoid out of bounds
                        ii = min(ii, sizeh - 1)
                        ii = max(0, ii)
                        jj = min(jj, sizew - 1)
                        jj = max(0, jj)
                        neighbors.append((ii, jj))
                if extra_constraint and (3 in [grid[ii][jj] for ii, jj in neighbors]):
                    goal.add(variab[i][j])
                goal.add(Not(And([variab[ii][jj] for ii, jj in neighbors])))
    print(f'Found {spawnable} spawnable blocks...')
    tactic = Then(Tactic('simplify'), Tactic('propagate-values'))
    simplified_goal = tactic(goal)

    for subgoal in simplified_goal:
        solver.add(subgoal.as_expr())

    total_sum = [cell for row in variab for cell in row]
    solver.minimize(Sum([If(c, 0, 1) for c in total_sum]))
    print('Solving...')
    start_time = time.time()
    res = solver.check()
    end_time = time.time()
    print(f"Instance solved in {end_time - start_time:.4f} seconds")
    if str(res) == 'unsat':
        print('WARNING: It\'s impossible to spawnproof this layout.')
        if extra_constraint:
            print('This is most likely because the --freetrapdoor flag was set. Try removing it and run the solver again.')
        return
    model = solver.model()
    carpets = 0
    for i in range(sizeh):
        for j, v in enumerate(variab[i]):
            val = is_true(model[v])
            if grid[i][j] == 1 and not val:
                carpets += 1
                grid[i][j] = 4
    print(f'Placed {carpets} carpets. ({round((carpets / spawnable) * 100, 2)}% of the total spawnable surface)')
    dirpath = Path('./solutions')
    dirpath.mkdir(parents=True, exist_ok=True)
    output_name = Path(output_name)
    if output_name.suffix == '.json':
        output_name = Path(output_name).with_suffix('.json')
    full_path = dirpath / output_name
    with open(full_path, 'w') as f:
        json.dump(grid, f)
    print(f'Solution saved to {full_path}')


def trim(grid: list) -> list:
    x_l, x_r, y_b, y_p = 0, len(grid) - 1, 0, len(grid) - 1
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

    grid = [[grid[i][j] for j in range(x_l, x_r + 1)] for i in range(y_b, y_p + 1)]
    return grid


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--freetrapdoor', action='store_true', help="If set, the solution won't have carpets adjacent to trapdoors.")
    parser.add_argument('--path', type=str, default='', help='Path of the file to open')
    parser.add_argument('--o', type=str, default='solution.json', help='Name of the output file')
    args = parser.parse_args()
    solve(args.path, args.o, args.freetrapdoor)

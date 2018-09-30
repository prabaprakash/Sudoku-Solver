__author__ = 'Prabakaran'
from copy import deepcopy
import requests
import json
import time
import threading


def create_grid(puzzle):
    grid = []
    grid.append([])
    c = r = 0
    for i in puzzle:
        if i == '.':
            grid[r].append("123456789")
        else:
            grid[r].append(i)
        c += 1
        if c == 9 and r < 8:
            c = 0
            r += 1
            grid.append([])
    return grid


def check_row(grid, row, col):
    for i in range(9):
        if row != i and len(grid[i][col]) == 1:
            grid[row][col] = grid[row][col].replace(grid[i][col], "")
            if len(grid[row][col]) == 0:
                return False
    return True


def check_column(grid, row, col):
    for i in range(9):
        if col != i and len(grid[row][i]) == 1:
            grid[row][col] = grid[row][col].replace(grid[row][i], "")
            if len(grid[row][col]) == 0:
                return False
    return True


def check_box(grid, row, col):
    srow = row - (row % 3)
    scol = col - (col % 3)
    for i in range(3):
        for j in range(3):
            if row != (i + srow) and col != (j + scol) and len(grid[i + srow][j + scol]) == 1:
                grid[row][col] = grid[row][col].replace(grid[i + srow][j + scol], "")
                if len(grid[row][col]) == 0:
                    return False
    return True


def constraint_propagation(grid):
    for i in range(9):
        for j in range(9):
            if len(grid[i][j]) > 1:
                if not check_row(grid, i, j) or not check_column(grid, i, j) or not check_box(grid, i, j):
                    return False
                if len(grid[i][j]) == 1:
                    return constraint_propagation(grid)
    return True


def min_cell(grid):
    row = col = -1
    min = 9
    flag = 0
    for i in range(9):
        for j in range(9):
            if len(grid[i][j]) > 1 and len(grid[i][j]) < min:
                min = len(grid[i][j])
                row = i
                col = j
                flag = 1
    if flag == 1:
        return True, row, col
    else:
        return False, row, col


def solve_puzzle(grid, result):
    check, row, col = min_cell(grid)
    if not check:
        if result == 0:
            return True, grid, result
        else:
            result -= 1
            return False, grid, result
    cell = deepcopy(grid[row][col])
    for i in cell:
        grid[row][col] = i
        clone = deepcopy(grid)
        if constraint_propagation(clone):
            check, final_grid, loop_back = solve_puzzle(clone, result)
            result = loop_back
            if check:
                return check, final_grid, result
    return False, grid, result


def sudoku(puzzle, result):
    grid = create_grid(puzzle)
    constraint_propagation(grid)
    check, final_grid, loop_back = solve_puzzle(grid, result)
    a = [cell for row in final_grid for cell in row]
    # print("".join(a))
    return "".join(a)


def makkhichoose_worker():
    r1 = requests.get('http://localhost:5000')
    if r1.status_code == 200:
        start_time = time.clock()
        print(r1)
        j1 = r1.json()
        print(str(j1))
        soltuion = sudoku(j1["puzzle"], 0)
        out = {"token": j1["token"], "solution": soltuion}
        print(out)
        r2 = requests.post('http://localhost:5000', data=json.dumps(out),
                           headers={'content-type': 'application/json'})
        if r2.status_code == 200:
            j2 = r2.json()
            if j2["isSolved"]:
                print(j2)
            else:
                print("solution incorrect")
                resolve(j1, 1, start_time)


def resolve(j1, loopback, start_time):
    if (time.clock() - start_time) >= 60:
        print("Backtracking Failed time up")
        return
    soltuion = sudoku(j1["puzzle"], loopback)
    out = {"token": j1["token"], "solution": soltuion}
    r2 = requests.post('http://localhost:5000', data=json.dumps(out),
                       headers={'content-type': 'application/json'})
    if r2.status_code == 200:
        j2 = r2.json()
        if j2["isSolved"]:
            print(soltuion)
            print(j2["message"])
            return
        else:
            loopback += 1
            print(str(j2["message"]) + " backtracking depth=" + str(loopback))
            resolve(j1, loopback, start_time)


if __name__ == "__main__":
    threads = []
    for i in range(1):
        t = threading.Thread(target=makkhichoose_worker())
        threads.append(t)
        t.start()

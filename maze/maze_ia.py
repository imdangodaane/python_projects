#!/usr/bin python3
from sys import stdin, stdout


def get_maze():
    """ Get maze from Virtual Agent's response and return
    maze as list for next processing
    Input: None
    Output: Maze map (type: list) """
    maze = []
    x = stdin.readline().rstrip('\n')
    while len(x) > 0:
        maze.append(x)
        x = stdin.readline().rstrip('\n')
    return maze[:-1]


def find_start_point(maze, my_letter):
    """ Find starting point from maze map and return
    its coordinate
    Input: maze map (list) and starting point letter (string)
    Output: coordinate (tuple) """
    for line in maze:
        if my_letter in line:
            return (line.index(my_letter), maze.index(line))


def findPath(maze, start, my_letter):
    """ Find path using BFF algorithm
    Input: maze map (list), starting point (tuple), my letter
    (string)
    Output: path (list of coordinate to point)
    """
    enemy = 'ABCDEFGHIJKLMNOPQRSTUVXYZ'.replace(my_letter, '')
    direction = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    queue = [[start]]
    checked = set(start)
    while queue:
        path = queue.pop(0)
        last_x, last_y = path[-1]
        if maze[last_y][last_x] == '!' and len(path) < 20:
            return path
        elif maze[last_y][last_x] == 'o':
            return path

        for d in direction:
            x, y = last_x + d[0], last_y + d[1]
            if (
                0 <= x < len(maze[0]) and 0 <= y < len(maze) and
                maze[y][x] != '#' and (x, y) not in checked and
                maze[y][x] not in enemy
               ):
                queue.append(path + [(x, y)])
                checked.add((x, y))


def move(start, goal):
    """ Send signal (stdout) to control our movement
    Input: start coordinate (tuple) and goal coordinate
    (tuple)
    Output: write to stdout signal to control movement
    """
    if start[0] < goal[0]:
        return stdout.write('MOVE RIGHT\n\n')
    elif start[0] > goal[0]:
        return stdout.write('MOVE LEFT\n\n')
    elif start[1] < goal[1]:
        return stdout.write('MOVE DOWN\n\n')
    elif start[1] > goal[1]:
        return stdout.write('MOVE UP\n\n')


def evade(maze, start):
    """ Find a path without/evade enemy
    Input: maze map (list) and starting point (tuple)
    Output: a path without enemy (list include starting
    coordinate and next coordinate without enemy)
    """
    direction = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for d in direction:
        x, y = start[0] + d[0], start[1] + d[1]
        if (
            0 <= x < len(maze[0]) and 0 <= y < len(maze) and
            maze[y][x] != '#' and maze[y][x] not in 'ABCDEFGHIJKLMNOPQRSTUVXYZ'
           ):
            return [start, (x, y)]


if __name__ == "__main__":
    """ Main function """
    while True:
        x = stdin.readline()
        if 'HELLO' in x:
            stdout.write('I AM QUI\n\n')
        if 'YOU ARE' in x:
            my_letter = x[-2]
            stdout.write('OK\n\n')
        if 'MAZE' in x:
            maze = get_maze()
            start = find_start_point(maze, my_letter)
            path = findPath(maze, start, my_letter)
            if path:
                move(path[0], path[1])
            else:
                path = evade(maze, start)
                move(path[0], path[1])
        if len(x) == 0:
            break

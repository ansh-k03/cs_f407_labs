from collections import deque
from heapq import heappop, heappush
from itertools import count
from math import hypot
from time import perf_counter


SEARCH_MAP = (
    '#################', '#S....#.........#', '#.###.#.#######.#',
    '#...#.#.......#.#', '###.#.#######.#.#', '#...#.........#.#',
    '#.###########.#.#', '#.............#G#', '#################',
)


class Warehouse:
    def __init__(self, rows):
        self.rows = tuple(rows)
        if not self.rows or any(not row for row in self.rows):
            raise ValueError('Map cannot be empty')
        if any(symbol not in '#.SG' for row in self.rows for symbol in row):
            raise ValueError('Unrecognized map symbol')
        starts = [(r, c) for r, row in enumerate(self.rows) for c, symbol in enumerate(row) if symbol == 'S']
        goals = [(r, c) for r, row in enumerate(self.rows) for c, symbol in enumerate(row) if symbol == 'G']
        if len(starts) != 1 or len(goals) != 1:
            raise ValueError('Map must contain exactly one start and one goal')
        self.start, self.goal = starts[0], goals[0]

    def open(self, position):
        row, column = position
        return (0 <= row < len(self.rows) and 0 <= column < len(self.rows[row])
                and self.rows[row][column] != '#')

    def neighbors(self, position):
        row, column = position
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            destination = (row + dr, column + dc)
            if self.open(destination):
                yield destination

    def heuristic(self, position, kind):
        dr, dc = abs(position[0] - self.goal[0]), abs(position[1] - self.goal[1])
        if kind == 'zero':
            return 0
        if kind == 'euclidean':
            return hypot(dr, dc)
        if kind == 'manhattan':
            return dr + dc
        if kind == 'double':
            return 2 * (dr + dc)
        raise ValueError('Unknown heuristic')

    def draw(self, path):
        rows = [list(row) for row in self.rows]
        for row, column in (path or [])[1:-1]:
            rows[row][column] = '*'
        return '\n'.join(''.join(row) for row in rows)


def reconstruct(parents, node):
    path = []
    while node is not None:
        path.append(node)
        node = parents[node]
    return path[::-1]


def find_path(warehouse, algorithm='astar', heuristic='manhattan'):
    if algorithm not in ('bfs', 'astar'):
        raise ValueError('Unknown search algorithm')
    warehouse.heuristic(warehouse.start, heuristic)
    started = perf_counter()
    parents = {warehouse.start: None}
    distances = {warehouse.start: 0}
    expanded = 0
    path = None
    if algorithm == 'bfs':
        frontier = deque([warehouse.start])
        while frontier:
            current = frontier.popleft()
            expanded += 1
            if current == warehouse.goal:
                path = reconstruct(parents, current)
                break
            for neighbor in warehouse.neighbors(current):
                if neighbor not in parents:
                    parents[neighbor] = current
                    distances[neighbor] = distances[current] + 1
                    frontier.append(neighbor)
    else:
        serial = count()
        frontier = [(warehouse.heuristic(warehouse.start, heuristic), next(serial), 0, warehouse.start)]
        while frontier:
            _, _, cost, current = heappop(frontier)
            if distances.get(current) != cost:
                continue
            expanded += 1
            if current == warehouse.goal:
                path = reconstruct(parents, current)
                break
            for neighbor in warehouse.neighbors(current):
                candidate = cost + 1
                if candidate < distances.get(neighbor, float('inf')):
                    distances[neighbor] = candidate
                    parents[neighbor] = current
                    priority = candidate + warehouse.heuristic(neighbor, heuristic)
                    heappush(frontier, (priority, next(serial), candidate, neighbor))
    return {'found': path is not None, 'path': path,
            'length': len(path) - 1 if path is not None else None,
            'expanded': expanded, 'seconds': perf_counter() - started,
            'rendered_map': warehouse.draw(path)}


def experiment():
    warehouse = Warehouse(SEARCH_MAP)
    results = {'bfs': find_path(warehouse, 'bfs')}
    for heuristic in ('manhattan', 'zero', 'euclidean', 'double'):
        results[heuristic] = find_path(warehouse, heuristic=heuristic)
    cases = {
        'adjacent_goal': ('#####', '#SG##', '#####'),
        'no_solution': ('#######', '#S....#', '###.###', '#...#G#', '#######'),
        'alternative_paths': ('#######', '#S...G#', '#.###.#', '#.....#', '#######'),
    }
    results['test_cases'] = {}
    for name, rows in cases.items():
        problem = Warehouse(rows)
        answer = find_path(problem)
        baseline = find_path(problem, 'bfs')
        assert answer['length'] == baseline['length']
        results['test_cases'][name] = answer
    second_map = Warehouse(('##########', '#S#....#.#', '#..#.#...#',
                            '##.......#', '#......#.#', '##.####.G#', '##########'))
    results['second_map'] = {name: find_path(second_map, heuristic=name)
                             for name in ('zero', 'manhattan', 'euclidean', 'double')}
    return results


if __name__ == '__main__':
    import json
    print(json.dumps(experiment(), indent=2))

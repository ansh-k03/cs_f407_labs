from warehouse_search import Warehouse, find_path


AGENT_MAP = (
    '#####################', '#S....#............G#', '#.##....##########..#',
    '#....##.............#', '#.######.###.#.###..#', '#........#..........#',
    '#####################',
)


class DeliveryAgent:
    def __init__(self, warehouse):
        self.warehouse = warehouse
        self.position = warehouse.start
        self.route = None

    def decide(self):
        self.route = find_path(self.warehouse, algorithm='bfs')
        return self.route

    def run(self):
        result = self.decide()
        if result['path'] is None:
            return result
        for destination in result['path'][1:]:
            if destination not in self.warehouse.neighbors(self.position):
                raise ValueError('Invalid move in planned route')
            self.position = destination
        if self.position != self.warehouse.goal:
            raise ValueError('Agent did not reach its goal')
        return result


def experiment():
    result = DeliveryAgent(Warehouse(AGENT_MAP)).run()
    blocked = list(AGENT_MAP)
    row, column = Warehouse(AGENT_MAP).goal
    for r, c in [(row, column - 1), (row + 1, column)]:
        line = list(blocked[r])
        line[c] = '#'
        blocked[r] = ''.join(line)
    result['blocked_goal'] = DeliveryAgent(Warehouse(blocked)).run()
    assert not result['blocked_goal']['found']
    return result


if __name__ == '__main__':
    import json
    print(json.dumps(experiment(), indent=2))

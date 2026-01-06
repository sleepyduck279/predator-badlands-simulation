from enum import Enum
import random


class TerrainType(Enum):
    EMPTY = "."
    DESERT_CANYON = "~"
    ROCKY_ZONE = "^"
    TRAP = "X"
    HOSTILE_TERRAIN = "#"


class Cell:

    def __init__(self, x, y, terrain=TerrainType.EMPTY):
        self.x = x
        self.y = y
        self.terrain = terrain
        self.occupant = None
        self.is_trap = (terrain == TerrainType.TRAP)
        self.stamina_cost = self._calculate_stamina_cost()

    def _calculate_stamina_cost(self):
        costs = {
            TerrainType.EMPTY: 1,
            TerrainType.DESERT_CANYON: 2,
            TerrainType.ROCKY_ZONE: 3,
            TerrainType.TRAP: 1,
            TerrainType.HOSTILE_TERRAIN: 4
        }
        return costs.get(self.terrain, 1)

    def is_passable(self):
        return self.occupant is None

    def __repr__(self):
        if self.occupant:
            return str(self.occupant)
        return self.terrain.value


class Grid:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = [[Cell(x, y) for y in range(height)] for x in range(width)]
        self._generate_terrain()

    def _generate_terrain(self):
        for _ in range(int(self.width * self.height * 0.20)):
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            self.cells[x][y].terrain = TerrainType.DESERT_CANYON
            self.cells[x][y].stamina_cost = 2

        for _ in range(int(self.width * self.height * 0.15)):
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            self.cells[x][y].terrain = TerrainType.ROCKY_ZONE
            self.cells[x][y].stamina_cost = 3

        for _ in range(int(self.width * self.height * 0.05)):
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            self.cells[x][y].terrain = TerrainType.TRAP
            self.cells[x][y].is_trap = True

        for _ in range(int(self.width * self.height * 0.10)):
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            self.cells[x][y].terrain = TerrainType.HOSTILE_TERRAIN
            self.cells[x][y].stamina_cost = 4

    def get_cell(self, x, y):
        wrapped_x = x % self.width
        wrapped_y = y % self.height
        return self.cells[wrapped_x][wrapped_y]

    def is_valid_position(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def get_neighbors(self, x, y, include_diagonals=False):
        neighbors = []

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        if include_diagonals:
            directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            neighbors.append((nx, ny, self.get_cell(nx, ny)))

        return neighbors

    def get_distance(self, pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2

        dx = min(abs(x2 - x1), self.width - abs(x2 - x1))
        dy = min(abs(y2 - y1), self.height - abs(y2 - y1))

        return dx + dy

    def get_empty_positions(self):
        empty = []
        for x in range(self.width):
            for y in range(self.height):
                cell = self.cells[x][y]
                if cell.is_passable():
                    empty.append((x, y))
        return empty

    def place_agent(self, agent, position):
        x, y = position
        cell = self.get_cell(x, y)

        if cell.occupant is not None:
            raise ValueError(f"Cell ({x}, {y}) already occupied")

        cell.occupant = agent
        agent.position = (x, y)

    def remove_agent(self, position):
        x, y = position
        cell = self.get_cell(x, y)
        cell.occupant = None

    def move_agent(self, old_pos, new_pos):
        old_x, old_y = old_pos
        new_x, new_y = new_pos

        old_cell = self.get_cell(old_x, old_y)
        new_cell = self.get_cell(new_x, new_y)

        if old_cell.occupant is None:
            raise ValueError(f"No agent at position {old_pos}")

        if new_cell.occupant is not None:
            raise ValueError(f"Target position {new_pos} already occupied")

        agent = old_cell.occupant
        old_cell.occupant = None
        new_cell.occupant = agent
        agent.position = new_pos

        return new_cell.stamina_cost

    def __repr__(self):
        lines = []
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                cell = self.cells[x][y]
                line += str(cell) + " "
            lines.append(line)
        return "\n".join(lines)
import numpy as np # type: ignore

class CityMap:
    def __init__(self):
        self.grid = np.full((4, 4), ".", dtype=str)

    def place_agent(self, position, symbol):
        x, y = position
        self.grid[x][y] = symbol

    def display_map(self):
        print("\nOs pontos de entrega sao: (3, 3), (0, 0), (2, 1), (1, 2)")
        print("Agente X deve entregar em todos os pontos")
        print("Agente Z deve entregar apenas (3, 3) e (2, 1)")
        print("Mapa 4x4 da Cidade:\n")
        for row in self.grid:
            print(" ".join(row))

    def get_neighbors(self, pos):
        x, y = pos
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 4 and 0 <= ny < 4 and self.grid[nx][ny] != "#":
                neighbors.append((nx, ny))
        return neighbors
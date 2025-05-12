import numpy as np # type: ignore

class CityMap:
    def __init__(self):
        self.grid = np.zeros((4, 4), dtype=str)
        self.grid[:] = "."  # Inicializa o mapa com pontos (.) para facilitar a visualização

    def place_agent(self, position, symbol):
        x, y = position
        self.grid[x][y] = symbol

    def display_map(self):
        print("Os pontos de entrega sao: (3, 3), (0, 0), (2, 1), (1, 2)")
        print("Agente X deve entregar em todos os pontos")
        print("Agente Z deve entregar apenas (3, 3) e (2, 1)")
        print(f"Mapa 4x4 da Cidade:\n")
        for row in self.grid:
            print(" ".join(row))

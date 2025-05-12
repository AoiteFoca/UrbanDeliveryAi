import numpy as np  # type: ignore

class CityMap:
    def __init__(self):
        self.grid = np.zeros((4, 4), dtype=str)  # Cria uma matriz 4x4 de strings vazias
        self.grid[:] = "."  # Preenche todas as posições com o símbolo "." para representar espaço livre

    def place_agent(self, position, symbol):  # Posicionando um agente no mapa
        x, y = position
        self.grid[x][y] = symbol  # Coloca o símbolo do agente na posição correspondente

    def display_map(self): # Display do mapa
        print("Os pontos de entrega sao: (3, 3), (0, 0), (2, 1), (1, 2)")  # Mostra os pontos de entrega
        print("Agente X deve entregar em todos os pontos")  # Instrução para o Agente X
        print("Agente Z deve entregar apenas (3, 3) e (2, 1)")  # Instrução para o Agente Z
        print(f"Mapa 4x4 da Cidade:\n")  # Título do mapa
        for row in self.grid:
            print(" ".join(row))  # Imprime cada linha do mapa separando os elementos com espaço (" ")
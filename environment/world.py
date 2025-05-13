class World:
    def __init__(self, width=4, height=4):
        self.width = width
        self.height = height
        self.grid = [["." for _ in range(width)] for _ in range(height)]
        self.agents = []

    def add_agent(self, agent):
        self.agents.append(agent)

    def update_positions(self):
        self.grid = [["." for _ in range(self.width)] for _ in range(self.height)]
        for ag in self.agents:
            x, y = ag.position
            self.grid[x][y] = ag.name[0].upper()

    def display(self):
        for row in self.grid:
            print(" ".join(row))
        print()

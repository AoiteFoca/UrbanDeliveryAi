import heapq
from utils import manhattan_distance

class DeliveryAgent:
    def __init__(self, start, deliveries, city_map, name="Agente"):
        self.position = start
        self.deliveries = deliveries
        self.name = name
        self.total_distance = 0
        self.city_map = city_map

    def a_star(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return self.reconstruct_path(came_from, current)

            for neighbor in self.city_map.get_neighbors(current):
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + manhattan_distance(neighbor, goal)
                    heapq.heappush(open_set, (f, neighbor))
        return None

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def deliver(self):
        print(f"\n{self.name} iniciando em {self.position}")
        for delivery in self.deliveries:
            path = self.a_star(self.position, delivery)
            if path:
                for step in path[1:]:
                    print(f"{self.name} moveu-se para {step}")
                    self.total_distance += 1
                    self.position = step
                print(f"{self.name} entregou em {delivery}")
            else:
                print(f"{self.name} nao conseguiu entregar em {delivery} (caminho nao encontrado)")
        print(f"{self.name} total de distancia percorrida: {self.total_distance}")

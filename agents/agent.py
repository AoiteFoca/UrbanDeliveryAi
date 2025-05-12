from utils import manhattan_distance

class DeliveryAgent:
    def __init__(self, start, deliveries, name="Agente"):
        self.position = start
        self.deliveries = deliveries
        self.name = name
        self.total_distance = 0

    def deliver(self):
        print(f"\n{self.name} iniciando em {self.position}")
        for delivery in self.deliveries:
            dist = manhattan_distance(self.position, delivery)
            self.total_distance += dist
            print(f"{self.name} entregou em {delivery} (distancia: {dist})")
            self.position = delivery
        print(f"{self.name} total de distancia percorrida: {self.total_distance}")

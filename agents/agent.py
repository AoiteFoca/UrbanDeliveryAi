from utils import manhattan_distance

class DeliveryAgent:
    def __init__(self, start, deliveries, name="Agente"):  # Inicializa o agente com posição inicial, entregas e nome
        self.position = start  # Posição inicial do agente
        self.deliveries = deliveries  # Lista de entregas (coordenadas)
        self.name = name  # Nome identificador do agente
        self.total_distance = 0  # Distância total percorrida (inicialmente zero)

    def deliver(self):  # Executa as entregas e calcula as distâncias
        print(f"\n{self.name} iniciando em {self.position}")  # Mostra a posição inicial do agente
        for delivery in self.deliveries:
            dist = manhattan_distance(self.position, delivery)  # Calcula a distância até o ponto de entrega
            self.total_distance += dist  # Acumula a distância percorrida
            print(f"{self.name} entregou em {delivery} (distancia: {dist})")  # Informa a entrega realizada
            self.position = delivery  # Atualiza a posição do agente após a entrega
        print(f"{self.name} total de distancia percorrida: {self.total_distance}")  # Mostra a distância total percorrida

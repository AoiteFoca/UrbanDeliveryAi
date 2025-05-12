from map.city_map import CityMap
from agents.agent import DeliveryAgent
import random

# Inicia o mapa
city = CityMap()

# Atribui duas posições aleatórias aos agentes X e Z
pos1 = (random.randint(0, 3), random.randint(0, 3))
pos2 = (random.randint(0, 3), random.randint(0, 3))

# Como o mapa é pequeno (4x4), evitamos que ambos comecem na mesma posição
while pos2 == pos1:
    pos2 = (random.randint(0, 3), random.randint(0, 3))

# Posiciona os agentes no mapa
city.place_agent(pos1, "X")
city.place_agent(pos2, "Z")

# Display do mapa
city.display_map()

# Define pontos de entrega
deliveries = [(3, 3), (0, 0), (2, 1), (1, 2)]

# Inicializa dois agentes
# O agente X deve entregar em todos os pontos da lista de entregas ([0::])
# O agente Z deve entregar apenas nos pontos (3, 3) e (2, 1) ([0::2])
# Utilizamos slicing para definir os pontos de entrega de cada agente
# Ambos os agentes iniciam no ponto start, mas entregam em pontos diferentes
# A estrutura do slicing é [start:end:step]
# Com o Agente Z, o step é 2, então ele entrega em pulando um ponto da lista
agent1 = DeliveryAgent(start=pos1, deliveries=deliveries[0::], name="Agente X")
agent2 = DeliveryAgent(start=pos2, deliveries=deliveries[0::2], name="Agente Z")

# Executa as entregas
agent1.deliver()
agent2.deliver()
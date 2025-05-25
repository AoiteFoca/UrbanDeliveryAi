import os
import time
from dotenv import load_dotenv # type: ignore
from autogen import AssistantAgent, UserProxyAgent # type: ignore
import random
import warnings

# ------------------------------------------------------------------
# 1.  Configuracao da chave e do modelo Groq (LLaMA 3.1 8B-instant)
# ------------------------------------------------------------------
load_dotenv(".env")

warnings.filterwarnings("ignore", category=UserWarning)

llm_config = {
    "config_list": [
        {
            "model":  "llama-3.1-8b-instant",
            "api_key": os.getenv("GROQ_API_KEY"),
            "api_type": "groq",
        }
    ],
    "temperature": 0,        # Valores baixos (ex: 0.0–0.3): respostas mais determinísticas e previsíveis. Valores altos (ex: 0.7–1.0): respostas mais criativas e variadas.
    "max_tokens": 5          # Respostas curtas
}
VALID_MOVES = {"up", "down", "left", "right"}

# ------------------------------------------------------------------
# 2.  Mundo em grade 4×4 e agente “fisico”
# ------------------------------------------------------------------
class World:
    def __init__(self, width=4, height=4, initial_positions=None, num_obstacles=2, forbidden_positions=None):
        self.width = width
        self.height = height
        self.grid = [["." for _ in range(width)] for _ in range(height)]
        self.agents = []
        self.initial_positions = initial_positions or []
        self.forbidden_positions = forbidden_positions or [[0, 0], [3, 3], [0, 1], [3, 2]]  # Adicionado
        self.obstacles = self.generate_obstacles(num_obstacles)

    def generate_obstacles(self, count):
        obstacles = []
        forbidden = self.initial_positions + self.forbidden_positions
        while len(obstacles) < count:
            x = random.randint(0, self.height - 1)
            y = random.randint(0, self.width - 1)
            pos = [x, y]
            if pos not in forbidden and pos not in obstacles:
                obstacles.append(pos)
        return obstacles

    def add_agent(self, agent):
        self.agents.append(agent)

    def update_positions(self):
        self.grid = [["." for _ in range(self.width)] for _ in range(self.height)]
        for ox, oy in self.obstacles:
            self.grid[ox][oy] = "0"
        for ag in self.agents:
            x, y = ag.position
            self.grid[x][y] = ag.name[0].upper()

    def display(self):
        os.system("cls" if os.name == "nt" else "clear")
        print("Mundo Atual (4x4):")
        print("+" + "---+" * self.width)
        for row in self.grid:
            print("| " + " | ".join(row) + " |")
            print("+" + "---+" * self.width)
        print(flush=True)

class Agent:
    def __init__(self, name, position, goal):
        self.name = name
        self.position = position
        self.goal = goal
        self.moves = 0

    def move_with_action(self, direction, world):
        dx = dy = 0
        if direction == "up": dx = -1
        elif direction == "down": dx = 1
        elif direction == "left": dy = -1
        elif direction == "right": dy = 1

        nx, ny = self.position[0] + dx, self.position[1] + dy
        if 0 <= nx < world.height and 0 <= ny < world.width:
            if [nx, ny] not in world.obstacles:
                self.position = [nx, ny]
                self.moves += 1
        world.update_positions()

# ------------------------------------------------------------------
# 3.  Funcoes auxiliares de raciocinio local
# ------------------------------------------------------------------
def options_prompt(agent, other, world):
    moves = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
    lines = []
    for m, (dx, dy) in moves.items():
        nx, ny = agent.position[0] + dx, agent.position[1] + dy
        in_bounds = 0 <= nx < world.height and 0 <= ny < world.width
        collision = [nx, ny] == other.position or [nx, ny] in world.obstacles
        dist = abs(nx - agent.goal[0]) + abs(ny - agent.goal[1]) if in_bounds else 99
        lines.append(f"{m}: pos=({nx},{ny}), dist={dist}, in_bounds={in_bounds}, collision={collision}")
    return "\n".join(lines)

def fallback_best_move(agent, other, world):
    moves = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
    best_move, best_dist = None, 1e9
    for m, (dx, dy) in moves.items():
        nx, ny = agent.position[0] + dx, agent.position[1] + dy
        if not (0 <= nx < world.height and 0 <= ny < world.width):
            continue
        if [nx, ny] == other.position or [nx, ny] in world.obstacles:
            continue
        dist = abs(nx - agent.goal[0]) + abs(ny - agent.goal[1])
        if dist < best_dist:
            best_move, best_dist = m, dist
    return best_move or "up"

def extract_action(response_content: str) -> str:
    """Extrai a primeira palavra valida da resposta do LLM."""
    content = response_content.strip().lower()
    for token in VALID_MOVES:
        if token in content:
            return token
    # tenta ler depois de 'action:' se existir
    if "action:" in content:
        tail = content.split("action:")[-1].strip()
        for token in VALID_MOVES:
            if tail.startswith(token):
                return token
    return ""

# ------------------------------------------------------------------
# 4.  Criacao dos AssistantAgents (x e y)
# ------------------------------------------------------------------
system_msg_template = """
Você controla {nome} em uma grade 4×4.

Sera fornecida uma lista de 4 opcoes, cada uma com:
- posicao resultante
- distância Manhattan ate o objetivo
- in_bounds (se a posicao esta dentro do grid)
- collision (se colide com o outro agente)

REGRAS
1. Escolha a opcao de menor distância com in_bounds=True e collision=False.
2. Se houver empate, prefira: up > down > left > right.
3. Responda **apenas** com uma destas palavras, em minúsculo: up, down, left ou right.
"""

agent_x  = AssistantAgent(
    name="DeliveryAgentx",
    description="Decide o proximo movimento de x",
    system_message=system_msg_template.format(nome="x"),
    llm_config=llm_config,
)
agent_y = AssistantAgent(
    name="DeliveryAgenty",
    description="Decide o proximo movimento de y",
    system_message=system_msg_template.format(nome="y"),
    llm_config=llm_config,
)

# Orquestrador sem intervencao humana
user_proxy = UserProxyAgent(
    name="User",
    llm_config=False,
    human_input_mode="NEVER",
    code_execution_config={"use_docker": False},
)

# ------------------------------------------------------------------
# 5.  Inicializa mundo e roda a simulacao
# ------------------------------------------------------------------
initial_pos_x = [3, 0]
initial_pos_y = [0, 3]
goal_x = [0, 3]
goal_y = [3, 0]

world = World(
    initial_positions=[initial_pos_x, initial_pos_y],
    num_obstacles=2,
    forbidden_positions=[[0, 0], [3, 3], [0, 1], [3, 2]]
)

ag1 = Agent("x", initial_pos_x, goal_x)
ag2 = Agent("y", initial_pos_y, goal_y)
world.add_agent(ag1)
world.add_agent(ag2)
world.update_positions()

# Exibe a mensagem de introdução com explicação
print("\nEste Script irá apresentar uma Simulação de entrega de dois agentes!\n")
print("Agente X: inicia na posição (3, 0) e tem como objetivo (0, 3).")
print("Agente Y: inicia na posição (0, 3) e tem como objetivo (3, 0).\n")
print("Ambos os agentes se movem em uma grade 4x4, tentando alcançar seus objetivos.\n")
print("Observação: Existem 2 obstáculos representados por '0' no mapa, gerados aleatoriamente.\n")
print("Os agentes não podem passar por nenhum obstáculo.")
print("As jogadas válidas dos agentes são: up, down, left e right.")
print("O jogo termina quando ambos os agentes alcançam seus objetivos.")
print("Ao iniciar a simulação, os agentes começarão as entregas...")
input("Pressione Enter para começar...\n")
os.system("cls" if os.name == "nt" else "clear")

while ag1.position != ag1.goal or ag2.position != ag2.goal:

    # ---------- TURNO DE x ----------
    if ag1.position != ag1.goal:
        prompt_x = (
            f"{options_prompt(ag1, ag2, world)}\n"
            f"Objetivo: {ag1.goal}\n"
            "Escolha sua jogada:"
        )
        resp_x = user_proxy.initiate_chat(
            recipient=agent_x,
            message=prompt_x,
            max_turns=1,
        )
        action_x = extract_action(resp_x.chat_history[-1]["content"])
        if action_x not in VALID_MOVES:
            action_x = fallback_best_move(ag1, ag2, world)
        ag1.move_with_action(action_x, world)

    # ---------- TURNO DE y ----------
    if ag2.position != ag2.goal:
        prompt_y = (
            f"{options_prompt(ag2, ag1, world)}\n"
            f"Objetivo: {ag2.goal}\n"
            "Escolha sua jogada:"
        )
        resp_y = user_proxy.initiate_chat(
            recipient=agent_y,
            message=prompt_y,
            max_turns=1,
        )
        action_y = extract_action(resp_y.chat_history[-1]["content"])
        if action_y not in VALID_MOVES:
            action_y = fallback_best_move(ag2, ag1, world)
        ag2.move_with_action(action_y, world)

    world.display()
    time.sleep(1)

print("Entrega concluída!")
print(f"Movimentos do agente X: {ag1.moves}")
print(f"Movimentos do agente Y: {ag2.moves}")
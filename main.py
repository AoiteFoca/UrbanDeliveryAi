# Import de bibliotecas
import os
import time
from dotenv import load_dotenv  # type: ignore
from autogen import AssistantAgent, UserProxyAgent  # type: ignore
import random
import warnings

# ------------------------------------------------------------------
# 1.  Configuracao da chave e do modelo Groq (LLaMA 3.1 8B-instant)
# ------------------------------------------------------------------
load_dotenv(".env") # Chamada do dotenv

warnings.filterwarnings("ignore", category=UserWarning)

llm_config = { # Configuracao geral da LLM
    "config_list": [
        {
            "model": "llama-3.1-8b-instant", # Selecao da LLM
            "api_key": os.getenv("GROQ_API_KEY"), # Insercao da chave da API GROQ em .env
            "api_type": "groq",
        }
    ],
    "temperature": 0,
    "max_tokens": 5
}
VALID_MOVES = {"up", "down", "left", "right"} # Movimentos validos identificados pela IA

# ------------------------------------------------------------------
# 2.  Mundo em grade 4×4 e agente “fisico”
# ------------------------------------------------------------------
class World: # Nessa classe os objetos do mapa sao criados
    def __init__(self, width=4, height=4, initial_positions=None, num_obstacles=2, forbidden_positions=None): # Set do tamanho do mapa, numero de agentes, etc...
        self.width = width
        self.height = height
        self.grid = [["." for _ in range(width)] for _ in range(height)]
        self.agents = []
        self.initial_positions = initial_positions or []
        self.forbidden_positions = forbidden_positions or [[0, 0], [3, 3], [0, 1], [3, 2]] # Valores do grid que os obstáculos nao podem ser criados (iniciais e finais dos agentes).
        self.obstacles = self.generate_obstacles(num_obstacles) # Declaracao dos obstaculos
        self.veiculo_position = self.generate_veiculo_position() # Declaracao do veiculo

    def generate_obstacles(self, count): # Funcao onde os obstaculos (fixos) sao gerados
        obstacles = []
        forbidden = self.initial_positions + self.forbidden_positions
        while len(obstacles) < count:
            x = random.randint(0, self.height - 1)
            y = random.randint(0, self.width - 1)
            pos = [x, y]
            if pos not in forbidden and pos not in obstacles:
                obstacles.append(pos)
        return obstacles

    def generate_veiculo_position(self): # Funcao onde o veiculo (obstaculo movel) e gerado
        forbidden = self.initial_positions + self.forbidden_positions + self.obstacles
        while True:
            x = random.randint(0, self.height - 1)
            y = random.randint(0, self.width - 1)
            if [x, y] not in forbidden:
                return [x, y]

    def move_veiculo(self): # Funcao que controla o movimento do obstaculo movel (veiculo)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx = self.veiculo_position[0] + dx
            ny = self.veiculo_position[1] + dy
            if 0 <= nx < self.height and 0 <= ny < self.width:
                new_pos = [nx, ny]
                if new_pos not in self.obstacles and all(ag.position != new_pos for ag in self.agents):
                    self.veiculo_position = new_pos
                    return

    def add_agent(self, agent): # Funcao que, posteriormente, adiciona os agentes ao mundo
        self.agents.append(agent)

    def update_positions(self): # Funcao que controla a atualizacao das posicoes, trabalha relacionando com obstaculos
        self.grid = [["." for _ in range(self.width)] for _ in range(self.height)]
        for ox, oy in self.obstacles:
            self.grid[ox][oy] = "0"
        vx, vy = self.veiculo_position
        self.grid[vx][vy] = "@"
        for ag in self.agents:
            x, y = ag.position
            self.grid[x][y] = ag.name[0].upper()

    def is_blocked(self, x, y): # Funcao de identificacao de bloqueio no caminho do grid
        return [x, y] in self.obstacles or [x, y] == self.veiculo_position

    def display(self): # Funcao de desenho do grid e personalizacao basica
        os.system("cls" if os.name == "nt" else "clear")
        print("Mundo Atual (4x4):")
        print("+" + "---+" * self.width)
        for row in self.grid:
            print("| " + " | ".join(row) + " |")
            print("+" + "---+" * self.width)
        print(flush=True)

class Agent: # Classe voltada apenas aos agentes
    def __init__(self, name, position, goal): # Aqui definimos valores para eles
        self.name = name
        self.position = position
        self.goal = goal
        self.moves = 0

    def move_with_action(self, direction, world): # Funcao de indicacao das direcoes
        dx = dy = 0
        if direction == "up": dx = -1
        elif direction == "down": dx = 1
        elif direction == "left": dy = -1
        elif direction == "right": dy = 1

        nx, ny = self.position[0] + dx, self.position[1] + dy
        if 0 <= nx < world.height and 0 <= ny < world.width:
            if not world.is_blocked(nx, ny):
                self.position = [nx, ny]
                self.moves += 1
        world.update_positions()

# ------------------------------------------------------------------
# 3.  Funcoes auxiliares de raciocinio local
# ------------------------------------------------------------------

# Como essa parte das funcoes e mais complexa, toda ela sera comentada em detalhes

def options_prompt(agent, other, world): # Funcao de listagem das opcoes possiveis de movimento para cada agente
    moves = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)} # Mapeamento das direcoes com suas respectivas variacoes no grid
    lines = []
    for m, (dx, dy) in moves.items(): # Para cada direcao possivel, calcula-se as informacoes abaixo
        nx, ny = agent.position[0] + dx, agent.position[1] + dy
        in_bounds = 0 <= nx < world.height and 0 <= ny < world.width # Verifica se a nova posicao esta dentro dos limites do grid
        collision = [nx, ny] == other.position or world.is_blocked(nx, ny) # Verifica se a posicao colide com outro agente ou obstaculo
        dist = abs(nx - agent.goal[0]) + abs(ny - agent.goal[1]) if in_bounds else 99 # Calcula a distancia de Manhattan se estiver dentro do grid
        lines.append(f"{m}: pos=({nx},{ny}), dist={dist}, in_bounds={in_bounds}, collision={collision}") # Monta a string com os dados da opcao
    return "\n".join(lines) # Retorna todas as opcoes possiveis em formato de texto para a LLM

def fallback_best_move(agent, other, world): # Funcao de decisao automatica caso a LLM nao retorne um movimento valido
    moves = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)} # Mapeamento das direcoes
    best_move, best_dist = None, 1e9 # Inicializa a melhor opcao com valores altos
    for m, (dx, dy) in moves.items(): # Para cada direcao possivel
        nx, ny = agent.position[0] + dx, agent.position[1] + dy # Calcula a nova posicao
        if not (0 <= nx < world.height and 0 <= ny < world.width): # Ignora se estiver fora dos limites
            continue
        if [nx, ny] == other.position or world.is_blocked(nx, ny): # Ignora se colidir com obstaculos ou outro agente
            continue
        dist = abs(nx - agent.goal[0]) + abs(ny - agent.goal[1]) # Calcula a distancia de Manhattan
        if dist < best_dist: # Atualiza a melhor opcao se a distancia for menor
            best_move, best_dist = m, dist
    return best_move or "up" # Retorna o melhor movimento ou "up" como padrao de seguranca

def extract_action(response_content: str) -> str: # Funcao que extrai a acao (movimento) da resposta da LLM
    content = response_content.strip().lower() # Limpa e padroniza a resposta
    for token in VALID_MOVES: # Verifica se a resposta contem uma direcao valida
        if token in content:
            return token
    if "action:" in content: # Se estiver no formato "action: direcao", extrai a parte final
        tail = content.split("action:")[-1].strip()
        for token in VALID_MOVES:
            if tail.startswith(token):
                return token
    return "" # Se nada valido for encontrado, retorna vazio

# ------------------------------------------------------------------
# 4.  Criacao dos AssistantAgents (x e y)
# ------------------------------------------------------------------
# Template da mensagem de sistema que configura as regras de decisao da LLM
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
3. Responda **apenas** com uma destas palavras, em minusculo: up, down, left ou right.
"""

agent_x = AssistantAgent( # Criacao e configuracao do LLM para o agente "x"
    name="DeliveryAgentx",
    description="Decide o proximo movimento de x",
    system_message=system_msg_template.format(nome="x"),
    llm_config=llm_config,
)

agent_y = AssistantAgent( # Mesma criacao e configuracao do LLM para o agente "y"
    name="DeliveryAgenty",
    description="Decide o proximo movimento de y",
    system_message=system_msg_template.format(nome="y"),
    llm_config=llm_config,
)

user_proxy = UserProxyAgent( 
    name="User",
    llm_config=False, # Desabilita o LLM 
    human_input_mode="NEVER", # Sem input humano
    code_execution_config={"use_docker": False}, # Nao usa docker pro codigo
)

# ------------------------------------------------------------------
# 5.  Inicializa o mundo e roda a simulacao
# ------------------------------------------------------------------
initial_pos_x = [3, 0] # Posicao inicial do Agente X
initial_pos_y = [0, 3] # Posicao inicial do Agente Y
goal_x = [0, 3] # Posicao final do Agente X
goal_y = [3, 0] # Posicao final do Agente Y

world = World( # Atribuicao da classe World para desenvolvimento geral do programa (Adicao de Agentes, posicoes, etc)
    initial_positions=[initial_pos_x, initial_pos_y],
    num_obstacles=2,
    forbidden_positions=[[3, 0], [0, 3], [0, 2], [3, 1]]
)

ag1 = Agent("x", initial_pos_x, goal_x) # Set dos valores do Agente X
ag2 = Agent("y", initial_pos_y, goal_y) # Set dos valores do Agente Y
world.add_agent(ag1) # Adicao do Agente X
world.add_agent(ag2) # Adicao do Agente Y
world.update_positions() # Inicio das atualizacoes de posicao

# Abaixo seguem as mensagens de introducao ao usuario a respeito do programa
# Coloquei uma inicializacao do programa com input enter para dar tempo de entender o contexto

# Mensagem de introducao (sem alteracoes)
print("\nEste Script ira apresentar uma Simulacão de entrega de dois agentes!\n")
print("Agente X: inicia na posicão (3, 0) e tem como objetivo (0, 3).")
print("Agente Y: inicia na posicão (0, 3) e tem como objetivo (3, 0).\n")
print("Ambos os agentes se movem em uma grade 4x4, tentando alcancar seus objetivos.\n")
print("Observacão:")
print("Existem dois obstaculos representados por '0' no mapa, gerados aleatoriamente.")
print("Existe um veiculo representado por '@' que se move aleatoriamente pelo mapa.\n")
print("Os agentes não podem passar por nenhum obstaculo.")
print("As jogadas validas dos agentes são: up, down, left e right.")
print("O jogo termina quando ambos os agentes alcancam seus objetivos.")
print("Ao iniciar a simulacão, os agentes comecarão as entregas...")
input("Pressione Enter para comecar...\n")
os.system("cls" if os.name == "nt" else "clear")

while ag1.position != ag1.goal or ag2.position != ag2.goal: # Coloca os agentes em loop enquanto a posicao atual nao coincidir com o objetivo 
    world.move_veiculo()

    if ag1.position != ag1.goal: # Logica de validacao de posicao atual x goal do 'Agente X'
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

    if ag2.position != ag2.goal: # Logica de validacao de posicao atual x goal do 'Agente Y'
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

    world.display() # Display do mapa
    time.sleep(1) # Controle de 'atraso'

# Saida final e dos valores de movimentos de cada agente
print("Entrega concluida!")
print(f"Movimentos do agente X: {ag1.moves}")
print(f"Movimentos do agente Y: {ag2.moves}")

import time
from dotenv import load_dotenv
from agents.delivery_agent import create_agents, user_proxy
from environment.world import World
from environment.agent_entity import Agent
from utils.prompt import generate_prompt
from utils.display import clear_and_display

load_dotenv(".env")

# Inicializa o mundo e agentes
world = World()
ana = Agent("Ana", [3, 0], [0, 3])
beto = Agent("Beto", [0, 3], [3, 0])
world.add_agent(ana)
world.add_agent(beto)
world.update_positions()

agent_ana, agent_beto = create_agents()

# Loop de simulação
while ana.position != ana.goal or beto.position != beto.goal:
    if ana.position != ana.goal:
        response_ana = user_proxy.initiate_chat(
            recipient=agent_ana,
            message=generate_prompt(ana, beto),
            max_turns=1,
        )
        action = response_ana.chat_history[-1]['content'].strip().lower()
        ana.move_with_action(action, world)

    if beto.position != beto.goal:
        response_beto = user_proxy.initiate_chat(
            recipient=agent_beto,
            message=generate_prompt(beto, ana),
            max_turns=1,
        )
        action = response_beto.chat_history[-1]['content'].strip().lower()
        beto.move_with_action(action, world)

    clear_and_display(world)
    time.sleep(1)

print("Delivery completed!")

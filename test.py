import os
import time
import autogen
from groq import Groq
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent

# Load API key from .env
load_dotenv(".env")

# Groq model configuration (LLaMA 3.1)
llm_config = {
    "config_list": [
        {
            "model": "llama-3.1-8b-instant",
            "api_key": os.environ.get("GROQ_API_KEY"),
            "api_type": "groq",
        }
    ]
}

# 4x4 Grid World
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
        os.system("cls" if os.name == "nt" else "clear")
        for row in self.grid:
            print(" ".join(row))
        print()

class Agent:
    def __init__(self, name, position, goal):
        self.name = name
        self.position = position
        self.goal = goal

    def move_with_action(self, direction, world):
        dx, dy = 0, 0
        if direction == "up":
            dx = -1
        elif direction == "down":
            dx = 1
        elif direction == "left":
            dy = -1
        elif direction == "right":
            dy = 1

        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        if 0 <= new_x < world.height and 0 <= new_y < world.width:
            self.position = [new_x, new_y]
        world.update_positions()

# Create LLM agents
agent_ana = AssistantAgent(
    name="DeliveryAgentAna",
    description="Agent that decides the next move for Ana",
    system_message="""
You control the delivery agent Ana in a 4x4 grid (it's a matrix of four arrays with four elements).
You are given:
- her current position,
- her goal,
- and the position of the other agent (Beto),

just answer with exactly one of the following text options: 'up', 'down', 'left', or 'right'.

Remember:
- Avoid moving outside the grid boundaries [0-3] and do not collide with the other agent;
- The first step of the array indicates the height and the other indicates width;
- Do not answer nothing different then: 'up', 'down', 'left', or 'right';
- If you are in position [0-3], that indicates you are in the first array of height in it last position of width;
- If you are in postion [3-0], that indicates you are in the last array of heigth in it first position of width;
""",
    llm_config=llm_config,
)

agent_beto = AssistantAgent(
    name="DeliveryAgentBeto",
    description="Agent that decides the next move for Beto",
    system_message="""
You control the delivery agent Beto in a 4x4 grid (it's a matrix of four arrays with four elements).
You are given:
- his current position,
- his goal,
- and the position of the other agent (Ana),

just answer with exactly one of the following text options: 'up', 'down', 'left', or 'right'.

Remember:
- Avoid moving outside the grid boundaries [0-3] and do not collide with the other agent;
- The first step of the array indicates the height and the other indicates width;
- Do not answer nothing different then: 'up', 'down', 'left', or 'right';
- If you are in position [0-3], that indicates you are in the first array of height in it last position of width;
- If you are in postion [3-0], that indicates you are in the last array of heigth in it first position of width;
""",
    llm_config=llm_config,
)

# Proxy user agent to orchestrate the LLMs
user_proxy = UserProxyAgent(
    name="User",
    llm_config=False,
    human_input_mode="NEVER",
    code_execution_config={"use_docker": False},
)

# Generate prompt based on current state
def generate_prompt(agent, other_agent):
    return (
        f"Your position: {agent.position}. "
        f"Goal: {agent.goal}. "
        f"Other agent's position: {other_agent.position}. "
        f"What is the next move?"
    )

# Initialize world and agents
world = World()
ag1 = Agent("Ana", [3, 0], [0, 3])
ag2 = Agent("Beto", [0, 3], [3, 0])
world.add_agent(ag1)
world.add_agent(ag2)
world.update_positions()

# Main simulation loop
while ag1.position != ag1.goal or ag2.position != ag2.goal:
    if ag1.position != ag1.goal:
        response_ana = user_proxy.initiate_chat(
            recipient=agent_ana,
            message=generate_prompt(ag1, ag2),
            max_turns=1,
        )
        action_ana = response_ana.chat_history[-1]['content'].strip().lower()
        ag1.move_with_action(action_ana, world)

    if ag2.position != ag2.goal:
        response_beto = user_proxy.initiate_chat(
            recipient=agent_beto,
            message=generate_prompt(ag2, ag1),
            max_turns=1,
        )
        action_beto = response_beto.chat_history[-1]['content'].strip().lower()
        ag2.move_with_action(action_beto, world)

    world.display()
    time.sleep(1)

print("Delivery completed!")
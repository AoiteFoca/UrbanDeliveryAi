from autogen import UserProxyAgent
from agents.assistant_config import get_ana, get_beto

def create_agents():
    agent_ana = get_ana()
    agent_beto = get_beto()
    return agent_ana, agent_beto

user_proxy = UserProxyAgent(
    name="User",
    llm_config=False,
    human_input_mode="NEVER",
    code_execution_config={"use_docker": False},
)
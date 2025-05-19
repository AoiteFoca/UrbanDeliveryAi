def generate_prompt(agent, other_agent):
    return (
        f"Your position: {agent.position}. "
        f"Goal: {agent.goal}. "
        f"Other agent's position: {other_agent.position}. "
        f"What is the next move?"
    )

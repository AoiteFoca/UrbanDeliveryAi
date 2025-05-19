from config.groq_config import llm_config
from autogen import AssistantAgent # type: ignore

def get_ana():
    return AssistantAgent(
        name="DeliveryAgentAna",
        description="Agent that decides the next move for Ana",
        system_message="""
You control the delivery agent Ana in a 4x4 grid...
(já está no seu código original)
""",
        llm_config=llm_config,
    )

def get_beto():
    return AssistantAgent(
        name="DeliveryAgentBeto",
        description="Agent that decides the next move for Beto",
        system_message="""
You control the delivery agent Beto in a 4x4 grid...
(mesmo esquema)
""",
        llm_config=llm_config,
    )

import os

llm_config = {
    "config_list": [
        {
            "model": "llama-3.1-8b-instant",
            "api_key": os.environ.get("GROQ_API_KEY"),
            "api_type": "groq",
        }
    ]
}

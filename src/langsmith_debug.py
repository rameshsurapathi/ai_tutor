# langsmith_debug.py
"""
This file sets up LangSmith monitoring for your AI agent.
Store your LangSmith API key, project name, and other config here.
Import this module in your main ai_iit_teacher.py file to enable monitoring.
"""

import os
from dotenv import load_dotenv
load_dotenv()

LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT_NAME")

LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true")


    

"""
Root compatibility module re-exporting agent package features.
"""

from agent.controller import AgentController, run_agent
from agent.state import InvestigationState
from agent.prompts import SYSTEM_PROMPT

__all__ = [
    "AgentController",
    "InvestigationState",
    "SYSTEM_PROMPT",
    "run_agent",
]

if __name__ == "__main__":
    user_input = "What does Flask.wsgi_app do when handling an incoming request?"
    print("Running AI Codebase Mentor Agent...")
    res = run_agent(user_input)
    print("Status:", res.get("status"))
    print("Answer:", res.get("answer"))
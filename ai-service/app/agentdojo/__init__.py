"""
AgentDojo Benchmark Integration Module for SentinelAI
Integrates ETH Zurich SPY Lab's AgentDojo dynamic evaluation framework.
"""

from app.agentdojo.adapter import AgentDojoAdapter, agentdojo_adapter
from app.agentdojo.guardrail_bridge import SentinelAIGuardrailBridge
from app.agentdojo.environments import (
    BaseEnvironment,
    WorkspaceEnvironment,
    BankingEnvironment,
    SlackEnvironment,
    TravelEnvironment,
    EnvironmentFactory
)

__all__ = [
    "AgentDojoAdapter",
    "agentdojo_adapter",
    "SentinelAIGuardrailBridge",
    "BaseEnvironment",
    "WorkspaceEnvironment",
    "BankingEnvironment",
    "SlackEnvironment",
    "TravelEnvironment",
    "EnvironmentFactory"
]

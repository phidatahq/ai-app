from dataclasses import dataclass


@dataclass
class ApiEndpoints:
    AGENT: str = "/agent"
    CHAT: str = "/chat"
    PROMPT: str = "/prompt"
    PING: str = "/ping"
    HEALTH: str = "/health"


endpoints = ApiEndpoints()

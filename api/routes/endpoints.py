from dataclasses import dataclass


@dataclass
class ApiEndpoints:
    PING: str = "/ping"
    HEALTH: str = "/health"
    TRAIN: str = "/train"
    PREDICT: str = "/predict"


endpoints = ApiEndpoints()

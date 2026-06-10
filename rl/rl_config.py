from dataclasses import dataclass

@dataclass
class RLConfig:
    gamma: float = 0.95
    epsilon_start: float = 1.0
    epsilon_end: float = 0.1
    epsilon_decay: float = 0.995
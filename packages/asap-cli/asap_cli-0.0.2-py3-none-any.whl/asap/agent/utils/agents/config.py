from dataclasses import dataclass
from typing import List, Any

@dataclass
class AgentConfig:
    model: Any
    tools: List[Any]
    checkpointer: Any
    system: str = ""

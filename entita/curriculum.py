from dataclasses import dataclass, field
from typing import List
from entita.esperienza import Esperienza

@dataclass
class Curriculum:
    matricola_operaio: str     # Funge da identificatore univoco del Curriculum
    sintesi: str
    formazione: str
    competenze: str
    esperienze: List[Esperienza] = field(default_factory=list)
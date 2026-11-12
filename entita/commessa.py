from dataclasses import dataclass, field
from typing import List

@dataclass
class Commessa:
    codice_modello: str        # Identificatore univoco della commessa
    matricola_referente: str   # Matricola dell'operaio referente
    tipologia: str             # modello, taglio, confezionamento
    stato: str                 # da avviare, in corso, chiuso
    data_inizio: str
    data_fine: str
    budget: float
    dettagli: str
    operai_assegnati: List[str] = field(default_factory=list) # Lista di matricole operai
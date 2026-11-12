from dataclasses import dataclass

@dataclass
class Esperienza:
    id_esperienza: str
    matricola_curriculum: str  # Corrisponde alla matricola dell'operaio
    azienda: str
    periodo: str
    commessa: str
    descrizione: str
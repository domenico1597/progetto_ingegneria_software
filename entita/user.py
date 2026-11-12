from dataclasses import dataclass

@dataclass
class User:
    username: str
    password: str
    ruolo: str              # "amministratore" oppure "operaio"
    matricola: str          # matricola dell'operaio associato (se ruolo == "operaio")
    primo_accesso: bool = True
from dataclasses import dataclass

@dataclass
class Operaio:
    matricola: str          # Identificatore univoco
    nome: str
    cognome: str
    genere: str
    data_nascita: str
    luogo_nascita: str
    provincia: str
    comune: str
    cap: str
    indirizzo: str
    email: str
    telefono: str
    ruolo: str              # amministrazione, macchinista, manutentore, responsabile commesse, documentazione
    stato: str = "attivo"   # attivo / inattivo
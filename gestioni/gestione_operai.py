import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional
from entita.operaio import Operaio


class GestioneOperai:
    def __init__(self, filepath: str = "data/operai.json"):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self._operai: List[Operaio] = []
        self.carica()

    def carica(self):
        """Carica gli operai dal file JSON all'avvio. Se non esiste, crea i dati iniziali."""
        if not self.filepath.exists():
            self._operai = [
                Operaio(
                    matricola="101", nome="Mario", cognome="Rossi", genere="M",
                    data_nascita="1985-05-12", luogo_nascita="Milano", provincia="MI",
                    comune="Milano", cap="20100", indirizzo="Via Roma 1",
                    email="mario.rossi@azienda.it", telefono="3331234567",
                    ruolo="macchinista", stato="attivo"
                ),
                Operaio(
                    matricola="102", nome="Anna", cognome="Verdi", genere="F",
                    data_nascita="1990-08-22", luogo_nascita="Monza", provincia="MB",
                    comune="Monza", cap="20900", indirizzo="Via Milano 5",
                    email="anna.verdi@azienda.it", telefono="3337654321",
                    ruolo="manutentore", stato="attivo"
                )
            ]
            self.salva()
            return

        with open(self.filepath, "r", encoding="utf-8") as f:
            dati = json.load(f)
            self._operai = [Operaio(**d) for d in dati]

    def salva(self):
        """Salva la lista corrente degli operai in formato JSON."""
        dati_da_salvare = [asdict(o) for o in self._operai]
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(dati_da_salvare, f, indent=2, ensure_ascii=False)

    def get_tutti(self) -> List[Operaio]:
        """Requisito RF3: List View Operai."""
        return self._operai

    def aggiungi_operaio(self, operaio: Operaio) -> bool:
        """Requisiti RF2 e RNF4: Aggiunta operaio, controllo matricola univoca e salvataggio."""
        if any(o.matricola == operaio.matricola for o in self._operai):
            return False  # Matricola già in uso (RNF4)
        self._operai.append(operaio)
        self.salva()
        return True

    def modifica_operaio(self, operaio_aggiornato: Operaio) -> bool:
        """Requisito RF2: Modifica dati operaio e salvataggio."""
        for idx, o in enumerate(self._operai):
            if o.matricola == operaio_aggiornato.matricola:
                self._operai[idx] = operaio_aggiornato
                self.salva()
                return True
        return False

    def rimuovi_operaio(self, matricola: str) -> bool:
        """Requisito RF9: Rimuovi Operaio e salvataggio."""
        operaio = self.ricerca_operaio(matricola)
        if operaio:
            self._operai.remove(operaio)
            self.salva()
            return True
        return False

    def ricerca_operaio(self, matricola: str) -> Optional[Operaio]:
        """Requisito RF7: Ricerca Operaio per matricola."""
        for o in self._operai:
            if o.matricola == matricola:
                return o
        return None

    def filtra_operai(self, testo_ricerca: str = "", ruolo: str = "Tutti", stato: str = "Tutti") -> List[Operaio]:
        """Requisito RF4: Filtra List View Operai."""
        risultato = []
        testo = testo_ricerca.lower().strip()

        for o in self._operai:
            corrisponde_testo = (
                not testo or
                testo in o.nome.lower() or
                testo in o.cognome.lower() or
                testo in o.matricola
            )
            corrisponde_ruolo = (ruolo == "Tutti" or o.ruolo == ruolo)
            corrisponde_stato = (stato == "Tutti" or o.stato == stato)

            if corrisponde_testo and corrisponde_ruolo and corrisponde_stato:
                risultato.append(o)

        return risultato
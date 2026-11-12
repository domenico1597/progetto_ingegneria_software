import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional
from entita.commessa import Commessa


class GestioneCommesse:
    def __init__(self, filepath: str = "data/commesse.json"):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self._commesse: List[Commessa] = []
        self.carica()

    def carica(self):
        """Carica le commesse dal file JSON. Se non esiste, crea i dati iniziali di prova."""
        if not self.filepath.exists():
            self._commesse = [
                Commessa(
                    codice_modello="COM_2026_01",
                    matricola_referente="101",
                    tipologia="confezionamento",
                    stato="in corso",
                    data_inizio="2026-01-15",
                    data_fine="2026-04-30",
                    budget=15000.0,
                    dettagli="Produzione lotti cappotti invernali doppio petto.",
                    operai_assegnati=["101", "102"]
                )
            ]
            self.salva()
            return

        with open(self.filepath, "r", encoding="utf-8") as f:
            dati = json.load(f)
            self._commesse = [Commessa(**d) for d in dati]

    def salva(self):
        """Salva la lista corrente delle commesse su file JSON."""
        dati_da_salvare = [asdict(c) for c in self._commesse]
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(dati_da_salvare, f, indent=2, ensure_ascii=False)

    def get_tutte(self) -> List[Commessa]:
        """Requisito RF21: List View Commesse."""
        return self._commesse

    def aggiungi_commessa(self, commessa: Commessa) -> bool:
        """Requisito RF19: Inserimento commessa con ID univoco e salvataggio."""
        if any(c.codice_modello == commessa.codice_modello for c in self._commesse):
            return False  # Codice modello già esistente
        self._commesse.append(commessa)
        self.salva()
        return True

    def modifica_commessa(self, commessa_aggiornata: Commessa) -> bool:
        """Requisito RF19: Modifica commessa e salvataggio."""
        for idx, c in enumerate(self._commesse):
            if c.codice_modello == commessa_aggiornata.codice_modello:
                self._commesse[idx] = commessa_aggiornata
                self.salva()
                return True
        return False

    def rimuovi_commessa(self, codice_modello: str) -> bool:
        """Requisito RF19: Rimuovi commessa e salvataggio."""
        c = self.ricerca_commessa(codice_modello)
        if c:
            self._commesse.remove(c)
            self.salva()
            return True
        return False

    def ricerca_commessa(self, codice_modello: str) -> Optional[Commessa]:
        """Requisito RF24: Ricerca Commessa per codice modello."""
        for c in self._commesse:
            if c.codice_modello == codice_modello:
                return c
        return None

    def filtra_commesse(self, testo_ricerca: str = "", tipologia: str = "Tutti", stato: str = "Tutti") -> List[Commessa]:
        """Requisito RF22: Filtra List View Commesse."""
        risultato = []
        testo = testo_ricerca.lower().strip()

        for c in self._commesse:
            corrisponde_testo = not testo or testo in c.codice_modello.lower() or testo in c.dettagli.lower()
            corrisponde_tipo = (tipologia == "Tutti" or c.tipologia == tipologia)
            corrisponde_stato = (stato == "Tutti" or c.stato == stato)

            if corrisponde_testo and corrisponde_tipo and corrisponde_stato:
                risultato.append(c)

        return risultato

    def get_commesse_per_operaio(self, matricola: str) -> List[Commessa]:
        """Restituisce le commesse a cui è assegnato un determinato operaio."""
        return [c for c in self._commesse if matricola in c.operai_assegnati or c.matricola_referente == matricola]
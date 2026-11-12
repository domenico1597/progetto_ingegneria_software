from typing import List, Optional
from entita.esperienza import Esperienza
from gestioni.gestione_curriculum import GestioneCurriculum


class GestioneEsperienze:
    def __init__(self, gestione_curriculum: GestioneCurriculum):
        self.gestione_curriculum = gestione_curriculum

    def get_esperienze_curriculum(self, matricola_curriculum: str) -> List[Esperienza]:
        """Restituisce tutte le esperienze associate a un curriculum."""
        cv = self.gestione_curriculum.ricerca_curriculum(matricola_curriculum)
        if not cv:
            return []
        return list(cv.esperienze)

    def ricerca_esperienza(self, matricola_curriculum: str, id_esperienza: str) -> Optional[Esperienza]:
        """Ricerca una singola esperienza tramite ID all'interno di un curriculum."""
        cv = self.gestione_curriculum.ricerca_curriculum(matricola_curriculum)
        if not cv:
            return None
        for exp in cv.esperienze:
            if exp.id_esperienza == id_esperienza:
                return exp
        return None

    def cud_esperienza(
        self,
        matricola_curriculum: str,
        esperienza: Esperienza,
        operazione: str = "aggiungi"
    ) -> bool:
        """
        Esegue Creazione, Aggiornamento o Rimozione di un'esperienza
        e salva immediatamente su JSON tramite GestioneCurriculum.
        """
        cv = self.gestione_curriculum.ricerca_curriculum(matricola_curriculum)
        if not cv:
            return False

        if operazione == "aggiungi":
            for exp in cv.esperienze:
                if exp.id_esperienza == esperienza.id_esperienza:
                    return False
            cv.esperienze.append(esperienza)
            self.gestione_curriculum.salva()
            return True

        elif operazione == "aggiorna":
            for i, exp in enumerate(cv.esperienze):
                if exp.id_esperienza == esperienza.id_esperienza:
                    cv.esperienze[i] = esperienza
                    self.gestione_curriculum.salva()
                    return True
            return False

        elif operazione == "rimuovi":
            for i, exp in enumerate(cv.esperienze):
                if exp.id_esperienza == esperienza.id_esperienza:
                    cv.esperienze.pop(i)
                    self.gestione_curriculum.salva()
                    return True
            return False

        return False
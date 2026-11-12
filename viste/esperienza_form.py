import uuid
from typing import Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QTextEdit, QPushButton, QMessageBox
)
from entita.esperienza import Esperienza
from gestioni.gestione_esperienze import GestioneEsperienze
from gestioni.gestione_commesse import GestioneCommesse


class EsperienzaFormDialog(QDialog):
    def __init__(
        self,
        matricola_curriculum: str,
        gestione_esperienze: GestioneEsperienze,
        gestione_commesse: GestioneCommesse,
        esperienza: Optional[Esperienza] = None,
        parent=None
    ):
        super().__init__(parent)
        self.matricola_curriculum = matricola_curriculum
        self.gestione_esperienze = gestione_esperienze
        self.gestione_commesse = gestione_commesse
        self.esperienza = esperienza
        self.is_edit = esperienza is not None

        self.setWindowTitle("Modifica Esperienza" if self.is_edit else "Aggiungi Esperienza")
        self.resize(450, 380)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.azienda = QLineEdit()
        self.azienda.setPlaceholderText("Nome azienda...")

        self.periodo = QLineEdit()
        self.periodo.setPlaceholderText("Es. Gennaio 2026 - Aprile 2026")

        # Menu a tendina popolato esclusivamente con le commesse salvate aventi stato "chiuso"
        self.commessa_combo = QComboBox()
        self._popola_commesse_chiuse()

        self.descrizione = QTextEdit()
        self.descrizione.setPlaceholderText("Attività svolte, mansioni, responsabilità...")
        self.descrizione.setMaximumHeight(120)

        if self.is_edit:
            self._popola_campi(self.esperienza)

        form.addRow("Azienda *:", self.azienda)
        form.addRow("Periodo *:", self.periodo)
        form.addRow("Commessa (Chiusa) *:", self.commessa_combo)
        form.addRow("Descrizione:", self.descrizione)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()

        btn_cancel = QPushButton("Annulla")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        if self.is_edit:
            btn_delete = QPushButton("Delete")
            btn_delete.clicked.connect(self.elimina)
            btn_layout.addWidget(btn_delete)

        btn_save = QPushButton("Save" if self.is_edit else "Salva Esperienza")
        btn_save.clicked.connect(self.salva)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _popola_commesse_chiuse(self):
        self.commessa_combo.clear()
        commesse_chiuse = self.gestione_commesse.filtra_commesse(stato="chiuso")
        for com in commesse_chiuse:
            self.commessa_combo.addItem(
                f"{com.codice_modello} ({com.tipologia} - {com.stato})",
                com.codice_modello
            )

    def _popola_campi(self, exp: Esperienza):
        self.azienda.setText(exp.azienda)
        self.periodo.setText(exp.periodo)
        self.descrizione.setPlainText(exp.descrizione)

        idx = self.commessa_combo.findData(exp.commessa)
        if idx >= 0:
            self.commessa_combo.setCurrentIndex(idx)
        elif exp.commessa:
            self.commessa_combo.addItem(f"{exp.commessa} (esistente)", exp.commessa)
            self.commessa_combo.setCurrentIndex(self.commessa_combo.count() - 1)

    def salva(self):
        azienda_txt = self.azienda.text().strip()
        periodo_txt = self.periodo.text().strip()
        commessa_codice = self.commessa_combo.currentData()
        descrizione_txt = self.descrizione.toPlainText().strip()

        if not azienda_txt or not periodo_txt:
            QMessageBox.warning(self, "Errore", "Azienda e Periodo sono obbligatori!")
            return

        if not commessa_codice:
            QMessageBox.warning(
                self,
                "Nessuna Commessa Chiusa",
                "Non ci sono commesse con stato 'chiuso' nel sistema!\n"
                "Chiudi prima una commessa nella sezione Gestione Commesse."
            )
            return

        com_obj = self.gestione_commesse.ricerca_commessa(commessa_codice)
        if not com_obj or com_obj.stato != "chiuso":
            QMessageBox.warning(
                self,
                "Commessa non valida",
                "La commessa selezionata deve esistere ed avere stato 'chiuso'."
            )
            return

        id_exp = self.esperienza.id_esperienza if self.is_edit else f"EXP_{uuid.uuid4().hex[:8].upper()}"

        exp_dati = Esperienza(
            id_esperienza=id_exp,
            matricola_curriculum=self.matricola_curriculum,
            azienda=azienda_txt,
            periodo=periodo_txt,
            commessa=commessa_codice,
            descrizione=descrizione_txt
        )

        operazione = "aggiorna" if self.is_edit else "aggiungi"
        if self.gestione_esperienze.cud_esperienza(self.matricola_curriculum, exp_dati, operazione=operazione):
            msg = "Esperienza aggiornata con successo!" if self.is_edit else "Esperienza aggiunta con successo!"
            QMessageBox.information(self, "Successo", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "Errore", "Impossibile salvare l'esperienza.")

    def elimina(self):
        conferma = QMessageBox.question(
            self,
            "Conferma Eliminazione",
            f"Vuoi eliminare l'esperienza presso '{self.esperienza.azienda}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if conferma == QMessageBox.Yes:
            if self.gestione_esperienze.cud_esperienza(
                self.matricola_curriculum,
                self.esperienza,
                operazione="rimuovi"
            ):
                QMessageBox.information(self, "Eliminata", "Esperienza rimossa con successo!")
                self.accept()
            else:
                QMessageBox.warning(self, "Errore", "Errore durante la rimozione dell'esperienza.")
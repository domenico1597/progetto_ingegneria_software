from typing import Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QMessageBox
)
from entita.operaio import Operaio
from gestioni.gestione_operai import GestioneOperai
from gestioni.gestione_curriculum import GestioneCurriculum
from gestioni.gestione_esperienze import GestioneEsperienze
from gestioni.gestione_commesse import GestioneCommesse
from viste.curriculum_form import CurriculumFormDialog


class OperaioFormDialog(QDialog):
    def __init__(
        self,
        gestione_operai: GestioneOperai,
        gestione_curriculum: Optional[GestioneCurriculum] = None,
        gestione_esperienze: Optional[GestioneEsperienze] = None,
        gestione_commesse: Optional[GestioneCommesse] = None,
        operaio: Optional[Operaio] = None,
        parent=None
    ):
        super().__init__(parent)
        self.gestione_operai = gestione_operai
        self.gestione_curriculum = gestione_curriculum
        self.gestione_esperienze = gestione_esperienze
        self.gestione_commesse = gestione_commesse
        self.operaio = operaio
        self.is_edit = operaio is not None

        self.setWindowTitle("Modifica Operaio" if self.is_edit else "Aggiungi Nuovo Operaio")
        self.resize(440, 520)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.matricola = QLineEdit()
        self.nome = QLineEdit()
        self.cognome = QLineEdit()
        self.genere = QComboBox()
        self.genere.addItems(["M", "F", "Altro"])
        self.data_nascita = QLineEdit()
        self.data_nascita.setPlaceholderText("YYYY-MM-DD")
        self.luogo_nascita = QLineEdit()
        self.provincia = QLineEdit()
        self.comune = QLineEdit()
        self.cap = QLineEdit()
        self.indirizzo = QLineEdit()
        self.email = QLineEdit()
        self.telefono = QLineEdit()
        self.ruolo = QComboBox()
        self.ruolo.addItems([
            "amministrazione", "macchinista", "manutentore",
            "responsabile commesse", "documentazione"
        ])
        self.stato = QComboBox()
        self.stato.addItems(["attivo", "inattivo"])

        form.addRow("Matricola *:", self.matricola)
        form.addRow("Nome *:", self.nome)
        form.addRow("Cognome *:", self.cognome)
        form.addRow("Genere:", self.genere)
        form.addRow("Data di nascita:", self.data_nascita)
        form.addRow("Luogo di nascita:", self.luogo_nascita)
        form.addRow("Provincia:", self.provincia)
        form.addRow("Comune:", self.comune)
        form.addRow("CAP:", self.cap)
        form.addRow("Indirizzo:", self.indirizzo)
        form.addRow("Email:", self.email)
        form.addRow("Telefono:", self.telefono)
        form.addRow("Ruolo:", self.ruolo)
        form.addRow("Stato:", self.stato)

        layout.addLayout(form)

        if self.is_edit:
            self._popola_campi(self.operaio)
            self.matricola.setReadOnly(True)

        btn_layout = QHBoxLayout()

        btn_cancel = QPushButton("Annulla")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        if self.is_edit:
            btn_delete = QPushButton("Delete")
            btn_delete.clicked.connect(self.elimina)
            btn_layout.addWidget(btn_delete)

            btn_cv = QPushButton("Curriculum")
            btn_cv.clicked.connect(self.apri_curriculum)
            btn_layout.addWidget(btn_cv)

        btn_salva = QPushButton("Save" if self.is_edit else "Salva Operaio")
        btn_salva.clicked.connect(self.salva)
        btn_layout.addWidget(btn_salva)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _popola_campi(self, op: Operaio):
        self.matricola.setText(op.matricola)
        self.nome.setText(op.nome)
        self.cognome.setText(op.cognome)
        self.genere.setCurrentText(op.genere)
        self.data_nascita.setText(op.data_nascita)
        self.luogo_nascita.setText(op.luogo_nascita)
        self.provincia.setText(op.provincia)
        self.comune.setText(op.comune)
        self.cap.setText(op.cap)
        self.indirizzo.setText(op.indirizzo)
        self.email.setText(op.email)
        self.telefono.setText(op.telefono)
        self.ruolo.setCurrentText(op.ruolo)
        self.stato.setCurrentText(op.stato)

    def salva(self):
        mat = self.matricola.text().strip()
        nom = self.nome.text().strip()
        cog = self.cognome.text().strip()

        if not mat or not nom or not cog:
            QMessageBox.warning(self, "Errore", "Matricola, Nome e Cognome sono obbligatori!")
            return

        op_dati = Operaio(
            matricola=mat,
            nome=nom,
            cognome=cog,
            genere=self.genere.currentText(),
            data_nascita=self.data_nascita.text().strip(),
            luogo_nascita=self.luogo_nascita.text().strip(),
            provincia=self.provincia.text().strip(),
            comune=self.comune.text().strip(),
            cap=self.cap.text().strip(),
            indirizzo=self.indirizzo.text().strip(),
            email=self.email.text().strip(),
            telefono=self.telefono.text().strip(),
            ruolo=self.ruolo.currentText(),
            stato=self.stato.currentText()
        )

        if self.is_edit:
            if self.gestione_operai.modifica_operaio(op_dati):
                QMessageBox.information(self, "Successo", f"Operaio {nom} {cog} aggiornato!")
                self.accept()
            else:
                QMessageBox.warning(self, "Errore", "Impossibile aggiornare l'operaio.")
        else:
            if self.gestione_operai.aggiungi_operaio(op_dati):
                QMessageBox.information(self, "Successo", f"Operaio {nom} {cog} aggiunto e salvato in JSON!")
                self.accept()
            else:
                QMessageBox.warning(self, "Errore", f"La matricola '{mat}' è già in uso! (RNF4)")

    def elimina(self):
        conferma = QMessageBox.question(
            self,
            "Conferma Eliminazione",
            f"Sei sicuro di voler eliminare l'operaio {self.operaio.nome} {self.operaio.cognome} (Matricola: {self.operaio.matricola})?",
            QMessageBox.Yes | QMessageBox.No
        )
        if conferma == QMessageBox.Yes:
            if self.gestione_operai.rimuovi_operaio(self.operaio.matricola):
                QMessageBox.information(self, "Eliminato", "Operaio rimosso con successo!")
                self.accept()
            else:
                QMessageBox.warning(self, "Errore", "Errore durante la rimozione dell'operaio.")

    def apri_curriculum(self):
        if not self.gestione_curriculum:
            QMessageBox.warning(self, "Errore", "Gestione Curriculum non disponibile.")
            return
        dialog = CurriculumFormDialog(
            self.operaio,
            self.gestione_curriculum,
            gestione_esperienze=self.gestione_esperienze,
            gestione_commesse=self.gestione_commesse,
            parent=self
        )
        dialog.exec_()
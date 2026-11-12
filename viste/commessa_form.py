from typing import Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QTextEdit, QDoubleSpinBox,
    QListWidget, QListWidgetItem, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from entita.commessa import Commessa
from gestioni.gestione_commesse import GestioneCommesse
from gestioni.gestione_operai import GestioneOperai


class CommessaFormDialog(QDialog):
    def __init__(
        self,
        gestione_commesse: GestioneCommesse,
        gestione_operai: GestioneOperai,
        commessa: Optional[Commessa] = None,
        parent=None
    ):
        super().__init__(parent)
        self.gestione_commesse = gestione_commesse
        self.gestione_operai = gestione_operai
        self.commessa = commessa
        self.is_edit = commessa is not None

        self.setWindowTitle("Modifica Commessa" if self.is_edit else "Aggiungi Nuova Commessa")
        self.resize(480, 560)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.codice_modello = QLineEdit()
        self.codice_modello.setPlaceholderText("Es. COM_2026_02")

        self.referente = QComboBox()
        operai = self.gestione_operai.get_tutti()
        for op in operai:
            self.referente.addItem(f"{op.matricola} - {op.nome} {op.cognome} ({op.ruolo})", op.matricola)

        self.tipologia = QComboBox()
        self.tipologia.addItems(["modello", "taglio", "confezionamento"])

        self.stato = QComboBox()
        self.stato.addItems(["da avviare", "in corso", "chiuso"])

        self.data_inizio = QLineEdit()
        self.data_inizio.setPlaceholderText("YYYY-MM-DD")

        self.data_fine = QLineEdit()
        self.data_fine.setPlaceholderText("YYYY-MM-DD")

        self.budget = QDoubleSpinBox()
        self.budget.setRange(0.0, 10000000.0)
        self.budget.setDecimals(2)
        self.budget.setSuffix(" €")

        self.dettagli = QTextEdit()
        self.dettagli.setPlaceholderText("Descrizione lavorazione, specifiche capispalla...")
        self.dettagli.setMaximumHeight(80)

        self.lista_operai = QListWidget()
        self.lista_operai.setMaximumHeight(120)
        for op in operai:
            item = QListWidgetItem(f"{op.matricola} - {op.nome} {op.cognome} ({op.ruolo})")
            item.setData(Qt.UserRole, op.matricola)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.lista_operai.addItem(item)

        form.addRow("Codice Modello *:", self.codice_modello)
        form.addRow("Referente Commessa *:", self.referente)
        form.addRow("Tipologia:", self.tipologia)
        form.addRow("Stato:", self.stato)
        form.addRow("Data Inizio:", self.data_inizio)
        form.addRow("Data Fine:", self.data_fine)
        form.addRow("Budget:", self.budget)
        form.addRow("Dettagli:", self.dettagli)
        form.addRow("Operai Assegnati:", self.lista_operai)

        layout.addLayout(form)

        if self.is_edit:
            self._popola_campi(self.commessa)
            self.codice_modello.setReadOnly(True)

        btn_layout = QHBoxLayout()

        btn_cancel = QPushButton("Annulla")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        if self.is_edit:
            btn_delete = QPushButton("Delete")
            btn_delete.clicked.connect(self.elimina)
            btn_layout.addWidget(btn_delete)

        btn_salva = QPushButton("Save" if self.is_edit else "Salva Commessa")
        btn_salva.clicked.connect(self.salva)
        btn_layout.addWidget(btn_salva)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _popola_campi(self, com: Commessa):
        self.codice_modello.setText(com.codice_modello)
        idx_ref = self.referente.findData(com.matricola_referente)
        if idx_ref >= 0:
            self.referente.setCurrentIndex(idx_ref)
        self.tipologia.setCurrentText(com.tipologia)
        self.stato.setCurrentText(com.stato)
        self.data_inizio.setText(com.data_inizio)
        self.data_fine.setText(com.data_fine)
        self.budget.setValue(float(com.budget))
        self.dettagli.setPlainText(com.dettagli)

        for i in range(self.lista_operai.count()):
            item = self.lista_operai.item(i)
            mat = item.data(Qt.UserRole)
            if mat in com.operai_assegnati:
                item.setCheckState(Qt.Checked)

    def salva(self):
        codice = self.codice_modello.text().strip()
        mat_ref = self.referente.currentData()

        if not codice:
            QMessageBox.warning(self, "Errore", "Il Codice Modello è obbligatorio!")
            return
        if not mat_ref:
            QMessageBox.warning(self, "Errore", "Seleziona un Referente Commessa valido!")
            return

        assegnati = []
        for i in range(self.lista_operai.count()):
            item = self.lista_operai.item(i)
            if item.checkState() == Qt.Checked:
                assegnati.append(item.data(Qt.UserRole))

        com_dati = Commessa(
            codice_modello=codice,
            matricola_referente=mat_ref,
            tipologia=self.tipologia.currentText(),
            stato=self.stato.currentText(),
            data_inizio=self.data_inizio.text().strip(),
            data_fine=self.data_fine.text().strip(),
            budget=self.budget.value(),
            dettagli=self.dettagli.toPlainText().strip(),
            operai_assegnati=assegnati
        )

        if self.is_edit:
            if self.gestione_commesse.modifica_commessa(com_dati):
                QMessageBox.information(self, "Successo", f"Commessa '{codice}' aggiornata!")
                self.accept()
            else:
                QMessageBox.warning(self, "Errore", "Impossibile aggiornare la commessa.")
        else:
            if self.gestione_commesse.aggiungi_commessa(com_dati):
                QMessageBox.information(self, "Successo", f"Commessa '{codice}' aggiunta e salvata in JSON!")
                self.accept()
            else:
                QMessageBox.warning(self, "Errore", f"Il codice modello '{codice}' è già esistente!")

    def elimina(self):
        conferma = QMessageBox.question(
            self,
            "Conferma Eliminazione",
            f"Sei sicuro di voler eliminare la commessa '{self.commessa.codice_modello}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if conferma == QMessageBox.Yes:
            if self.gestione_commesse.rimuovi_commessa(self.commessa.codice_modello):
                QMessageBox.information(self, "Eliminata", "Commessa rimossa con successo!")
                self.accept()
            else:
                QMessageBox.warning(self, "Errore", "Errore durante la rimozione della commessa.")
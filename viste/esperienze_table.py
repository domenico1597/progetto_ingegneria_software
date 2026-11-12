from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QMessageBox
)
from entita.operaio import Operaio
from gestioni.gestione_esperienze import GestioneEsperienze
from gestioni.gestione_commesse import GestioneCommesse
from viste.esperienza_form import EsperienzaFormDialog


class EsperienzeTableDialog(QDialog):
    def __init__(
        self,
        operaio: Operaio,
        gestione_esperienze: GestioneEsperienze,
        gestione_commesse: GestioneCommesse,
        parent=None
    ):
        super().__init__(parent)
        self.operaio = operaio
        self.gestione_esperienze = gestione_esperienze
        self.gestione_commesse = gestione_commesse
        self.esperienze_correnti = []

        self.setWindowTitle(f"Esperienze Lavorative - {operaio.nome} {operaio.cognome}")
        self.resize(720, 420)

        layout = QVBoxLayout()

        lbl_titolo = QLabel(
            f"<b>Esperienze di {operaio.nome} {operaio.cognome}</b> (Matricola: {operaio.matricola})"
        )
        layout.addWidget(lbl_titolo)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Azienda", "Periodo", "Commessa", "Descrizione"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.cellDoubleClicked.connect(self.apri_modifica_da_riga)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()

        btn_chiudi = QPushButton("Chiudi")
        btn_chiudi.clicked.connect(self.accept)
        btn_layout.addWidget(btn_chiudi)

        btn_layout.addStretch()

        btn_aggiorna = QPushButton("Aggiorna Esperienza")
        btn_aggiorna.clicked.connect(self.apri_modifica_selezionata)
        btn_layout.addWidget(btn_aggiorna)

        btn_aggiungi = QPushButton("Aggiungi Esperienza")
        btn_aggiungi.clicked.connect(self.apri_aggiungi)
        btn_layout.addWidget(btn_aggiungi)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.refresh_table()

    def refresh_table(self):
        self.esperienze_correnti = self.gestione_esperienze.get_esperienze_curriculum(
            self.operaio.matricola
        )
        self.table.setRowCount(len(self.esperienze_correnti))
        for r, exp in enumerate(self.esperienze_correnti):
            self.table.setItem(r, 0, QTableWidgetItem(exp.azienda))
            self.table.setItem(r, 1, QTableWidgetItem(exp.periodo))
            self.table.setItem(r, 2, QTableWidgetItem(exp.commessa))
            self.table.setItem(r, 3, QTableWidgetItem(exp.descrizione))

    def apri_aggiungi(self):
        dialog = EsperienzaFormDialog(
            matricola_curriculum=self.operaio.matricola,
            gestione_esperienze=self.gestione_esperienze,
            gestione_commesse=self.gestione_commesse,
            esperienza=None,
            parent=self
        )
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_table()

    def apri_modifica_selezionata(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.esperienze_correnti):
            QMessageBox.warning(self, "Attenzione", "Seleziona prima un'esperienza dalla tabella.")
            return
        self.apri_modifica_da_riga(row, 0)

    def apri_modifica_da_riga(self, row: int, column: int):
        if 0 <= row < len(self.esperienze_correnti):
            exp_selezionata = self.esperienze_correnti[row]
            dialog = EsperienzaFormDialog(
                matricola_curriculum=self.operaio.matricola,
                gestione_esperienze=self.gestione_esperienze,
                gestione_commesse=self.gestione_commesse,
                esperienza=exp_selezionata,
                parent=self
            )
            if dialog.exec_() == QDialog.Accepted:
                self.refresh_table()
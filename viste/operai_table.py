from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QDialog
)
from gestioni.gestione_operai import GestioneOperai
from gestioni.gestione_curriculum import GestioneCurriculum
from gestioni.gestione_esperienze import GestioneEsperienze
from gestioni.gestione_commesse import GestioneCommesse
from viste.operaio_form import OperaioFormDialog


class OperaiTableView(QWidget):
    def __init__(
        self,
        gestione_operai: GestioneOperai,
        gestione_curriculum: GestioneCurriculum,
        gestione_esperienze: GestioneEsperienze,
        gestione_commesse: GestioneCommesse,
        parent=None
    ):
        super().__init__(parent)
        self.gestione_operai = gestione_operai
        self.gestione_curriculum = gestione_curriculum
        self.gestione_esperienze = gestione_esperienze
        self.gestione_commesse = gestione_commesse

        layout = QVBoxLayout(self)

        # Barra Filtri e Azioni (RF4, RF5)
        filter_box = QHBoxLayout()
        self.op_search = QLineEdit()
        self.op_search.setPlaceholderText("Cerca Nome, Cognome o Matricola...")
        self.op_search.textChanged.connect(self.refresh_table)

        self.op_role = QComboBox()
        self.op_role.addItems([
            "Tutti", "amministrazione", "macchinista", "manutentore",
            "responsabile commesse", "documentazione"
        ])
        self.op_role.currentTextChanged.connect(self.refresh_table)

        btn_reset = QPushButton("Azzera Filtri")
        btn_reset.clicked.connect(self.reset_filtri)

        btn_aggiungi = QPushButton("+ Aggiungi Operaio")
        btn_aggiungi.clicked.connect(self.apri_aggiungi)

        filter_box.addWidget(QLabel("Cerca:"))
        filter_box.addWidget(self.op_search)
        filter_box.addWidget(QLabel("Ruolo:"))
        filter_box.addWidget(self.op_role)
        filter_box.addWidget(btn_reset)
        filter_box.addWidget(btn_aggiungi)
        layout.addLayout(filter_box)

        # Tabella Operai (RF3, RF8)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Matricola", "Nome", "Cognome", "Ruolo", "Email", "Stato"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.apri_modifica)
        layout.addWidget(self.table)

        self.refresh_table()

    def refresh_table(self):
        testo = self.op_search.text()
        ruolo = self.op_role.currentText()
        operai = self.gestione_operai.filtra_operai(testo_ricerca=testo, ruolo=ruolo)

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(operai))
        for r, o in enumerate(operai):
            self.table.setItem(r, 0, QTableWidgetItem(o.matricola))
            self.table.setItem(r, 1, QTableWidgetItem(o.nome))
            self.table.setItem(r, 2, QTableWidgetItem(o.cognome))
            self.table.setItem(r, 3, QTableWidgetItem(o.ruolo))
            self.table.setItem(r, 4, QTableWidgetItem(o.email))
            self.table.setItem(r, 5, QTableWidgetItem(o.stato))
        self.table.setSortingEnabled(True)

    def reset_filtri(self):
        self.op_search.clear()
        self.op_role.setCurrentIndex(0)

    def apri_aggiungi(self):
        dialog = OperaioFormDialog(self.gestione_operai, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_table()

    def apri_modifica(self, row: int, column: int):
        matricola = self.table.item(row, 0).text()
        operaio = self.gestione_operai.ricerca_operaio(matricola)
        if operaio:
            dialog = OperaioFormDialog(
                self.gestione_operai,
                gestione_curriculum=self.gestione_curriculum,
                gestione_esperienze=self.gestione_esperienze,
                gestione_commesse=self.gestione_commesse,
                operaio=operaio,
                parent=self
            )
            if dialog.exec_() == QDialog.Accepted:
                self.refresh_table()
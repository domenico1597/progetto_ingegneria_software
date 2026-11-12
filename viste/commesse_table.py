from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QDialog
)
from gestioni.gestione_commesse import GestioneCommesse
from gestioni.gestione_operai import GestioneOperai
from viste.commessa_form import CommessaFormDialog


class CommesseTableView(QWidget):
    def __init__(
        self,
        gestione_commesse: GestioneCommesse,
        gestione_operai: GestioneOperai,
        parent=None
    ):
        super().__init__(parent)
        self.gestione_commesse = gestione_commesse
        self.gestione_operai = gestione_operai

        layout = QVBoxLayout(self)

        # Barra Filtri Commessa (RF21, RF22, RF23)
        filter_box = QHBoxLayout()
        self.com_search = QLineEdit()
        self.com_search.setPlaceholderText("Cerca Codice Modello...")
        self.com_search.textChanged.connect(self.refresh_table)

        self.com_tipo = QComboBox()
        self.com_tipo.addItems(["Tutti", "modello", "taglio", "confezionamento"])
        self.com_tipo.currentTextChanged.connect(self.refresh_table)

        self.com_stato = QComboBox()
        self.com_stato.addItems(["Tutti", "da avviare", "in corso", "chiuso"])
        self.com_stato.currentTextChanged.connect(self.refresh_table)

        btn_reset = QPushButton("Azzera Filtri")
        btn_reset.clicked.connect(self.reset_filtri)

        btn_aggiungi = QPushButton("+ Aggiungi Commessa")
        btn_aggiungi.clicked.connect(self.apri_aggiungi)

        filter_box.addWidget(QLabel("Cerca:"))
        filter_box.addWidget(self.com_search)
        filter_box.addWidget(QLabel("Tipologia:"))
        filter_box.addWidget(self.com_tipo)
        filter_box.addWidget(QLabel("Stato:"))
        filter_box.addWidget(self.com_stato)
        filter_box.addWidget(btn_reset)
        filter_box.addWidget(btn_aggiungi)
        layout.addLayout(filter_box)

        # Tabella Commesse (RF25)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Codice Modello", "Referente", "Tipologia", "Stato", "Data Inizio", "Operai Assegnati"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.apri_modifica)
        layout.addWidget(self.table)

        self.refresh_table()

    def refresh_table(self):
        testo = self.com_search.text()
        tipo = self.com_tipo.currentText()
        stato = self.com_stato.currentText()
        commesse = self.gestione_commesse.filtra_commesse(
            testo_ricerca=testo,
            tipologia=tipo,
            stato=stato
        )

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(commesse))
        for r, c in enumerate(commesse):
            operai_str = ", ".join(c.operai_assegnati) if c.operai_assegnati else "-"
            self.table.setItem(r, 0, QTableWidgetItem(c.codice_modello))
            self.table.setItem(r, 1, QTableWidgetItem(c.matricola_referente))
            self.table.setItem(r, 2, QTableWidgetItem(c.tipologia))
            self.table.setItem(r, 3, QTableWidgetItem(c.stato))
            self.table.setItem(r, 4, QTableWidgetItem(c.data_inizio))
            self.table.setItem(r, 5, QTableWidgetItem(operai_str))
        self.table.setSortingEnabled(True)

    def reset_filtri(self):
        self.com_search.clear()
        self.com_tipo.setCurrentIndex(0)
        self.com_stato.setCurrentIndex(0)

    def apri_aggiungi(self):
        dialog = CommessaFormDialog(self.gestione_commesse, self.gestione_operai, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_table()

    def apri_modifica(self, row: int, column: int):
        codice = self.table.item(row, 0).text()
        commessa = self.gestione_commesse.ricerca_commessa(codice)
        if commessa:
            dialog = CommessaFormDialog(
                self.gestione_commesse,
                self.gestione_operai,
                commessa=commessa,
                parent=self
            )
            if dialog.exec_() == QDialog.Accepted:
                self.refresh_table()
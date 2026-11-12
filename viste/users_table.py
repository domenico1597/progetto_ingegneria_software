from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QDialog
)
from gestioni.gestione_user import GestioneUser
from gestioni.gestione_operai import GestioneOperai
from viste.user_form import UserFormDialog


class UsersTableView(QWidget):
    def __init__(
        self,
        gestione_user: GestioneUser,
        gestione_operai: GestioneOperai,
        parent=None
    ):
        super().__init__(parent)
        self.gestione_user = gestione_user
        self.gestione_operai = gestione_operai

        layout = QVBoxLayout(self)

        top_box = QHBoxLayout()
        top_box.addWidget(QLabel("<b>Elenco Account Utenti</b>"))
        top_box.addStretch()

        btn_crea_user = QPushButton("+ Crea User")
        btn_crea_user.clicked.connect(self.apri_aggiungi)
        top_box.addWidget(btn_crea_user)
        layout.addLayout(top_box)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Username", "Ruolo", "Matricola Associata", "Primo Accesso"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.apri_modifica)
        layout.addWidget(self.table)

        self.refresh_table()

    def refresh_table(self):
        users = self.gestione_user.get_tutti()

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(users))
        for r, u in enumerate(users):
            self.table.setItem(r, 0, QTableWidgetItem(u.username))
            self.table.setItem(r, 1, QTableWidgetItem(u.ruolo))
            self.table.setItem(r, 2, QTableWidgetItem(u.matricola if u.matricola else "-"))
            self.table.setItem(r, 3, QTableWidgetItem("Sì" if u.primo_accesso else "No"))
        self.table.setSortingEnabled(True)

    def apri_aggiungi(self):
        dialog = UserFormDialog(self.gestione_user, self.gestione_operai, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_table()

    def apri_modifica(self, row: int, column: int):
        username = self.table.item(row, 0).text()
        user = self.gestione_user.ricerca_user(username)
        if user:
            dialog = UserFormDialog(self.gestione_user, self.gestione_operai, user=user, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh_table()
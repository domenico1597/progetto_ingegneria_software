from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget
)

from entita.user import User
from gestioni.gestione_user import GestioneUser
from gestioni.gestione_operai import GestioneOperai
from gestioni.gestione_commesse import GestioneCommesse
from gestioni.gestione_curriculum import GestioneCurriculum
from gestioni.gestione_esperienze import GestioneEsperienze

from viste.operai_table import OperaiTableView
from viste.commesse_table import CommesseTableView
from viste.users_table import UsersTableView


class MainWindow(QMainWindow):
    def __init__(
        self,
        user: User,
        gestione_user: GestioneUser,
        gestione_operai: GestioneOperai,
        gestione_commesse: GestioneCommesse,
        gestione_curriculum: GestioneCurriculum,
        gestione_esperienze: GestioneEsperienze
    ):
        super().__init__()
        self.user = user
        self.gestione_user = gestione_user
        self.gestione_operai = gestione_operai
        self.gestione_commesse = gestione_commesse
        self.gestione_curriculum = gestione_curriculum
        self.gestione_esperienze = gestione_esperienze

        self.setWindowTitle(f"Gestionale Capispalla - Utente: {user.username} ({user.ruolo.upper()})")
        self.resize(1000, 650)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Header superiore
        header_layout = QHBoxLayout()
        lbl_info = QLabel(f"Utente connesso: <b>{user.username}</b> | Ruolo: <b>{user.ruolo}</b>")
        header_layout.addWidget(lbl_info)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Menu di navigazione a pulsanti
        nav_layout = QHBoxLayout()
        self.btn_nav_operai = QPushButton("Gestione Operai")
        self.btn_nav_commesse = QPushButton("Gestione Commesse")
        self.btn_nav_users = QPushButton("Gestione User")

        self.btn_nav_operai.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_nav_commesse.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_nav_users.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        nav_layout.addWidget(self.btn_nav_operai)
        nav_layout.addWidget(self.btn_nav_commesse)
        nav_layout.addWidget(self.btn_nav_users)
        main_layout.addLayout(nav_layout)

        # QStackedWidget per il cambio schermata
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # Inizializza le 3 viste separate
        self.view_operai = OperaiTableView(
            self.gestione_operai,
            self.gestione_curriculum,
            self.gestione_esperienze,
            self.gestione_commesse,
            parent=self
        )
        self.view_commesse = CommesseTableView(
            self.gestione_commesse,
            self.gestione_operai,
            parent=self
        )
        self.view_users = UsersTableView(
            self.gestione_user,
            self.gestione_operai,
            parent=self
        )

        self.stack.addWidget(self.view_operai)
        self.stack.addWidget(self.view_commesse)
        self.stack.addWidget(self.view_users)

        # Se l'utente è un operaio semplice, limita l'accesso (RF1)
        if self.user.ruolo == "operaio":
            self.btn_nav_commesse.setEnabled(False)
            self.btn_nav_users.setEnabled(False)
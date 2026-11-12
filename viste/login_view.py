from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import pyqtSignal
from entita.user import User
from gestioni.gestione_user import GestioneUser

class LoginView(QDialog):
    login_successo = pyqtSignal(User)

    def __init__(self, gestione_user: GestioneUser):
        super().__init__()
        self.gestione_user = gestione_user
        self.setWindowTitle("Sistema Gestionale Capispalla - Login")
        self.resize(350, 220)

        layout = QVBoxLayout()
        title = QLabel("Autenticazione Sistema Capispalla")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username o Matricola")
        form.addRow("Username:", self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        form.addRow("Password:", self.pass_input)

        layout.addLayout(form)

        self.btn_login = QPushButton("Accedi")
        self.btn_login.clicked.connect(self.handle_login)
        layout.addWidget(self.btn_login)

        self.setLayout(layout)

    def handle_login(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text()

        user = self.gestione_user.autentica(username, password)
        if user is None:
            QMessageBox.warning(self, "Errore Login", "Credenziali non valide!")
            return

        # Controllo Primo Accesso (Reimpostazione Password obbligatoria)
        if user.primo_accesso:
            QMessageBox.information(
                self, "Primo Accesso",
                "Al primo accesso è necessario cambiare la password (minimo 8 caratteri)."
            )
            dialog_cambio = CambioPasswordDialog(username, password, self.gestione_user, self)
            if dialog_cambio.exec_() != QDialog.Accepted:
                return  # Non fa proseguire se annulla o sballa la nuova password

        self.login_successo.emit(user)
        self.accept()


class CambioPasswordDialog(QDialog):
    def __init__(self, username: str, vecchia_pass: str, gestione_user: GestioneUser, parent=None):
        super().__init__(parent)
        self.username = username
        self.vecchia_pass = vecchia_pass
        self.gestione_user = gestione_user

        self.setWindowTitle("Reimpostazione Password")
        self.resize(320, 180)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.nuova_pass_input = QLineEdit()
        self.nuova_pass_input.setEchoMode(QLineEdit.Password)
        form.addRow("Nuova Password:", self.nuova_pass_input)

        self.conferma_pass_input = QLineEdit()
        self.conferma_pass_input.setEchoMode(QLineEdit.Password)
        form.addRow("Conferma Password:", self.conferma_pass_input)

        layout.addLayout(form)

        btn_salva = QPushButton("Salva Nuova Password")
        btn_salva.clicked.connect(self.handle_cambio)
        layout.addWidget(btn_salva)

        self.setLayout(layout)

    def handle_cambio(self):
        nuova_pass = self.nuova_pass_input.text()
        conferma_pass = self.conferma_pass_input.text()

        if nuova_pass != conferma_pass:
            QMessageBox.warning(self, "Errore", "Le password inserite non coincidono!")
            return

        if not self.gestione_user.valida_password(nuova_pass):
            QMessageBox.warning(self, "Errore", "La password deve contenere almeno 8 caratteri (RNF3)!")
            return

        esito = self.gestione_user.cambia_password(self.username, self.vecchia_pass, nuova_pass)
        if esito:
            QMessageBox.information(self, "Successo", "Password aggiornata con successo!")
            self.accept()
        else:
            QMessageBox.warning(self, "Errore", "Impossibile aggiornare la password.")
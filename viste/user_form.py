from typing import Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QMessageBox
)
from entita.user import User
from gestioni.gestione_user import GestioneUser
from gestioni.gestione_operai import GestioneOperai


class UserFormDialog(QDialog):
    def __init__(
        self,
        gestione_user: GestioneUser,
        gestione_operai: GestioneOperai,
        user: Optional[User] = None,
        parent=None
    ):
        super().__init__(parent)
        self.gestione_user = gestione_user
        self.gestione_operai = gestione_operai
        self.user = user
        self.is_edit = user is not None

        self.setWindowTitle("Modifica User" if self.is_edit else "Crea Nuovo User")
        self.resize(400, 260)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText(
            "Lascia vuoto per non cambiare" if self.is_edit else "Minimo 8 caratteri"
        )

        self.ruolo = QComboBox()
        self.ruolo.addItems(["operaio", "amministratore"])
        self.ruolo.currentTextChanged.connect(self.aggiorna_stato_matricola)

        self.matricola_combo = QComboBox()
        self.popola_matricole_disponibili()

        form.addRow("Username *:", self.username)
        form.addRow("Password:" if self.is_edit else "Password *:", self.password)
        form.addRow("Ruolo:", self.ruolo)
        form.addRow("Operaio (Matricola):", self.matricola_combo)

        layout.addLayout(form)

        if self.is_edit:
            self._popola_campi(self.user)
            self.username.setReadOnly(True)

        # Barra pulsanti inferiore
        btn_layout = QHBoxLayout()

        btn_cancel = QPushButton("Annulla")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        if self.is_edit:
            btn_delete = QPushButton("Delete")
            btn_delete.clicked.connect(self.elimina)
            btn_layout.addWidget(btn_delete)

        btn_salva = QPushButton("Save" if self.is_edit else "Crea User")
        btn_salva.clicked.connect(self.salva)
        btn_layout.addWidget(btn_salva)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def popola_matricole_disponibili(self):
        """Inserisce gli operai senza account, più l'eventuale operaio già associato allo user."""
        self.matricola_combo.clear()
        matricole_usate = self.gestione_user.get_matricole_associate()
        matricola_attuale = self.user.matricola if self.is_edit else ""

        for op in self.gestione_operai.get_tutti():
            if op.matricola not in matricole_usate or op.matricola == matricola_attuale:
                self.matricola_combo.addItem(
                    f"{op.matricola} - {op.nome} {op.cognome}",
                    op.matricola
                )

    def _popola_campi(self, u: User):
        self.username.setText(u.username)
        self.ruolo.setCurrentText(u.ruolo)
        self.aggiorna_stato_matricola(u.ruolo)
        if u.matricola:
            idx = self.matricola_combo.findData(u.matricola)
            if idx != -1:
                self.matricola_combo.setCurrentIndex(idx)

    def aggiorna_stato_matricola(self, ruolo: str):
        """Abilita la scelta della matricola solo se il ruolo è 'operaio'."""
        self.matricola_combo.setEnabled(ruolo == "operaio")

    def salva(self):
        usr = self.username.text().strip()
        pwd = self.password.text()
        ruolo = self.ruolo.currentText()

        if not usr:
            QMessageBox.warning(self, "Errore", "Lo Username è obbligatorio!")
            return

        if not self.is_edit and not pwd:
            QMessageBox.warning(self, "Errore", "La Password è obbligatoria!")
            return

        if pwd and not self.gestione_user.valida_password(pwd):
            QMessageBox.warning(self, "Errore", "La password deve contenere almeno 8 caratteri (RNF3)!")
            return

        if ruolo == "operaio":
            if self.matricola_combo.count() == 0:
                QMessageBox.warning(self, "Errore", "Nessun operaio disponibile senza account!")
                return
            matricola = self.matricola_combo.currentData()
        else:
            matricola = ""

        if self.is_edit:
            user_aggiornato = User(
                username=usr,
                password="",  # Gestita in modifica_user
                ruolo=ruolo,
                matricola=matricola,
                primo_accesso=self.user.primo_accesso
            )
            if self.gestione_user.modifica_user(user_aggiornato, nuova_password_in_chiaro=pwd):
                QMessageBox.information(self, "Successo", f"User '{usr}' aggiornato!")
                self.accept()
            else:
                QMessageBox.warning(self, "Errore", "Impossibile aggiornare lo user.")
        else:
            nuovo_user = User(
                username=usr,
                password=pwd,
                ruolo=ruolo,
                matricola=matricola,
                primo_accesso=True
            )
            if self.gestione_user.aggiungi_user(nuovo_user):
                QMessageBox.information(self, "Successo", f"User '{usr}' creato e salvato!")
                self.accept()
            else:
                QMessageBox.warning(self, "Errore", f"Lo username '{usr}' è già in uso!")

    def elimina(self):
        conferma = QMessageBox.question(
            self,
            "Conferma Eliminazione",
            f"Sei sicuro di voler eliminare lo user '{self.user.username}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if conferma == QMessageBox.Yes:
            if self.gestione_user.rimuovi_user(self.user.username):
                QMessageBox.information(self, "Eliminato", "User rimosso con successo!")
                self.accept()
            else:
                QMessageBox.warning(self, "Errore", "Errore durante la rimozione dello user.")
import sys
from PyQt5.QtWidgets import QApplication, QDialog

from gestioni.gestione_user import GestioneUser
from gestioni.gestione_operai import GestioneOperai
from gestioni.gestione_commesse import GestioneCommesse
from gestioni.gestione_curriculum import GestioneCurriculum
from gestioni.gestione_esperienze import GestioneEsperienze

from viste.login_view import LoginView
from viste.main_window import MainWindow


class AppController:
    """Controller principale che coordina l'avvio e la navigazione tra le finestre."""

    def __init__(self):
        # 1. Inizializzazione delle Gestioni (Business Logic & Data Access)
        self.gestione_user = GestioneUser()
        self.gestione_operai = GestioneOperai()
        self.gestione_commesse = GestioneCommesse()
        self.gestione_curriculum = GestioneCurriculum()

        # GestioneEsperienze riceve l'istanza di GestioneCurriculum per operare sui CV
        self.gestione_esperienze = GestioneEsperienze(self.gestione_curriculum)

        self.main_window = None

    def start(self):
        # 2. Avvio del Dialog di Login
        login_dialog = LoginView(self.gestione_user)
        login_dialog.login_successo.connect(self.apri_dashboard)

        # Se il login ha esito positivo (QDialog.Accepted), mostra la Dashboard principale
        if login_dialog.exec_() == QDialog.Accepted:
            if self.main_window is not None:
                self.main_window.show()

    def apri_dashboard(self, user):
        # 3. Istanziazione della Finestra Principale con il profilo utente e le gestioni
        self.main_window = MainWindow(
            user=user,
            gestione_user=self.gestione_user,
            gestione_operai=self.gestione_operai,
            gestione_commesse=self.gestione_commesse,
            gestione_curriculum=self.gestione_curriculum,
            gestione_esperienze=self.gestione_esperienze
        )


if __name__ == "__main__":
    # Avvio dell'applicazione Qt
    app = QApplication(sys.argv)

    controller = AppController()
    controller.start()

    sys.exit(app.exec_())
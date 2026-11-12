from typing import Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QTextEdit, QPushButton, QMessageBox
)
from entita.operaio import Operaio
from entita.curriculum import Curriculum
from gestioni.gestione_curriculum import GestioneCurriculum
from gestioni.gestione_esperienze import GestioneEsperienze
from gestioni.gestione_commesse import GestioneCommesse
from viste.esperienze_table import EsperienzeTableDialog


class CurriculumFormDialog(QDialog):
    def __init__(
        self,
        operaio: Operaio,
        gestione_curriculum: GestioneCurriculum,
        gestione_esperienze: Optional[GestioneEsperienze] = None,
        gestione_commesse: Optional[GestioneCommesse] = None,
        parent=None
    ):
        super().__init__(parent)
        self.operaio = operaio
        self.gestione_curriculum = gestione_curriculum
        self.gestione_esperienze = gestione_esperienze
        self.gestione_commesse = gestione_commesse
        self.cv_esistente = self.gestione_curriculum.ricerca_curriculum(operaio.matricola)

        self.setWindowTitle(f"Curriculum - {operaio.nome} {operaio.cognome} (Mat. {operaio.matricola})")
        self.resize(540, 480)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.lbl_operaio = QLabel(
            f"<b>{operaio.nome} {operaio.cognome}</b> — Matricola: {operaio.matricola} ({operaio.ruolo})"
        )
        layout.addWidget(self.lbl_operaio)

        self.sintesi = QTextEdit()
        self.sintesi.setPlaceholderText("Breve sintesi professionale...")
        self.sintesi.setMaximumHeight(90)

        self.formazione = QTextEdit()
        self.formazione.setPlaceholderText("Titoli di studio, corsi, attestati...")
        self.formazione.setMaximumHeight(90)

        self.competenze = QTextEdit()
        self.competenze.setPlaceholderText("Competenze tecniche...")
        self.competenze.setMaximumHeight(90)

        if self.cv_esistente:
            self.sintesi.setPlainText(self.cv_esistente.sintesi)
            self.formazione.setPlainText(self.cv_esistente.formazione)
            self.competenze.setPlainText(self.cv_esistente.competenze)

        form.addRow("Sintesi:", self.sintesi)
        form.addRow("Formazione:", self.formazione)
        form.addRow("Competenze:", self.competenze)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()

        btn_cancel = QPushButton("Annulla")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        if self.cv_esistente:
            btn_elimina = QPushButton("Elimina CV")
            btn_elimina.clicked.connect(self.elimina_cv)
            btn_layout.addWidget(btn_elimina)

        btn_esperienze = QPushButton("Esperienze")
        btn_esperienze.clicked.connect(self.apri_esperienze)
        btn_layout.addWidget(btn_esperienze)

        btn_genera = QPushButton("Genera PDF")
        btn_genera.clicked.connect(self.genera_pdf)
        btn_layout.addWidget(btn_genera)

        btn_salva = QPushButton("Salva CV")
        btn_salva.clicked.connect(self.salva_cv)
        btn_layout.addWidget(btn_salva)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _crea_oggetto_cv(self) -> Curriculum:
        self.cv_esistente = self.gestione_curriculum.ricerca_curriculum(self.operaio.matricola)
        esperienze_attuali = self.cv_esistente.esperienze if self.cv_esistente else []
        return Curriculum(
            matricola_operaio=self.operaio.matricola,
            sintesi=self.sintesi.toPlainText().strip(),
            formazione=self.formazione.toPlainText().strip(),
            competenze=self.competenze.toPlainText().strip(),
            esperienze=esperienze_attuali
        )

    def apri_esperienze(self):
        if not self.gestione_esperienze or not self.gestione_commesse:
            QMessageBox.warning(self, "Errore", "Gestione Esperienze o Commesse non disponibile.")
            return

        cv = self._crea_oggetto_cv()
        self.gestione_curriculum.cud_curriculum(cv, operazione="salva")
        self.cv_esistente = self.gestione_curriculum.ricerca_curriculum(self.operaio.matricola)

        dialog = EsperienzeTableDialog(
            self.operaio,
            self.gestione_esperienze,
            self.gestione_commesse,
            self
        )
        dialog.exec_()

        self.cv_esistente = self.gestione_curriculum.ricerca_curriculum(self.operaio.matricola)

    def salva_cv(self):
        cv = self._crea_oggetto_cv()
        if self.gestione_curriculum.cud_curriculum(cv, operazione="salva"):
            self.cv_esistente = self.gestione_curriculum.ricerca_curriculum(self.operaio.matricola)
            QMessageBox.information(self, "Successo", "Curriculum salvato con successo!")
            self.accept()
        else:
            QMessageBox.warning(self, "Errore", "Impossibile salvare il curriculum.")

    def elimina_cv(self):
        conferma = QMessageBox.question(
            self,
            "Conferma Eliminazione",
            f"Vuoi eliminare i dati del curriculum di {self.operaio.nome} {self.operaio.cognome}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if conferma == QMessageBox.Yes:
            cv = self._crea_oggetto_cv()
            if self.gestione_curriculum.cud_curriculum(cv, operazione="rimuovi"):
                QMessageBox.information(self, "Eliminato", "Curriculum rimosso con successo!")
                self.accept()
            else:
                QMessageBox.warning(self, "Errore", "Errore durante la rimozione del curriculum.")

    def genera_pdf(self):
        cv = self._crea_oggetto_cv()
        self.gestione_curriculum.cud_curriculum(cv, operazione="salva")
        self.cv_esistente = self.gestione_curriculum.ricerca_curriculum(self.operaio.matricola)

        path_salvato = self.gestione_curriculum.genera_pdf_curriculum(self.operaio)
        QMessageBox.information(
            self,
            "PDF Generato",
            f"Curriculum PDF generato con successo!\nSalvato in:\n{path_salvato}"
        )
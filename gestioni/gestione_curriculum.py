import json
from dataclasses import asdict
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from entita.curriculum import Curriculum
from entita.esperienza import Esperienza
from entita.operaio import Operaio


class GestioneCurriculum:
    def __init__(self, filepath: str = "data/curricula.json"):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self._curricula: List[Curriculum] = []
        self.carica()

    def carica(self):
        """Carica i curriculum da JSON, oppure crea un dato di prova al primo avvio."""
        if not self.filepath.exists():
            self._curricula = [
                Curriculum(
                    matricola_operaio="101",
                    sintesi="Operaio specializzato nel confezionamento capispalla di alta moda.",
                    formazione="Diploma Tecnico Tessile",
                    competenze="Taglio tessuti, Macchine da cucire industriali, Controllo qualità",
                    esperienze=[]
                )
            ]
            self.salva()
            return

        with open(self.filepath, "r", encoding="utf-8") as f:
            dati_grezzi = json.load(f)
            self._curricula = []
            for d in dati_grezzi:
                esperienze_obj = [Esperienza(**e) for e in d.get("esperienze", [])]
                d["esperienze"] = esperienze_obj
                self._curricula.append(Curriculum(**d))

    def salva(self):
        """Salva tutti i curriculum su file JSON."""
        dati_da_salvare = [asdict(cv) for cv in self._curricula]
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(dati_da_salvare, f, indent=2, ensure_ascii=False)

    def ricerca_curriculum(self, matricola_operaio: str) -> Optional[Curriculum]:
        """Requisito RF12: Ricerca Curriculum tramite la matricola dell'operaio associato."""
        for cv in self._curricula:
            if cv.matricola_operaio == matricola_operaio:
                return cv
        return None

    def cud_curriculum(self, curriculum: Curriculum, operazione: str = "salva") -> bool:
        """Requisito RF10: Operazioni CUD sui Curriculum (Inserimento, Modifica, Rimozione)."""
        cv_esistente = self.ricerca_curriculum(curriculum.matricola_operaio)

        if operazione == "salva":
            if cv_esistente:
                cv_esistente.sintesi = curriculum.sintesi
                cv_esistente.formazione = curriculum.formazione
                cv_esistente.competenze = curriculum.competenze
            else:
                self._curricula.append(curriculum)
            self.salva()
            return True

        elif operazione == "rimuovi":
            if cv_esistente:
                self._curricula.remove(cv_esistente)
                self.salva()
                return True
            return False

        return False

    def genera_pdf_curriculum(self, operaio: Operaio, output_path: str = None) -> str:
        """Requisito RF13 e RNF2: Genera il curriculum relativo a un operaio in formato PDF."""
        cv = self.ricerca_curriculum(operaio.matricola)

        if output_path is None:
            output_dir = Path("curriculum_pdf")
            output_dir.mkdir(exist_ok=True)
            output_path = str(output_dir / f"CV_{operaio.matricola}_{operaio.cognome}.pdf")

        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Intestazione Dati Operaio
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, leading=22)
        story.append(Paragraph(f"Curriculum Vitae - {operaio.nome} {operaio.cognome}", title_style))
        story.append(Spacer(1, 10))

        info_text = (
            f"<b>Matricola:</b> {operaio.matricola} | <b>Ruolo:</b> {operaio.ruolo} | <b>Email:</b> {operaio.email}<br/>"
            f"<b>Telefono:</b> {operaio.telefono} | <b>Indirizzo:</b> {operaio.indirizzo}, {operaio.comune} ({operaio.provincia})"
        )
        story.append(Paragraph(info_text, styles['Normal']))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, spaceAfter=15))

        if cv:
            story.append(Paragraph("<b>Sintesi Professionale:</b>", styles['Heading3']))
            story.append(Paragraph(cv.sintesi or "N/D", styles['Normal']))
            story.append(Spacer(1, 10))

            story.append(Paragraph("<b>Formazione:</b>", styles['Heading3']))
            story.append(Paragraph(cv.formazione or "N/D", styles['Normal']))
            story.append(Spacer(1, 10))

            story.append(Paragraph("<b>Competenze Tecniche:</b>", styles['Heading3']))
            story.append(Paragraph(cv.competenze or "N/D", styles['Normal']))
            story.append(Spacer(1, 15))

            story.append(Paragraph("<b>Esperienze Lavorative:</b>", styles['Heading3']))
            if cv.esperienze:
                for exp in cv.esperienze:
                    exp_text = f"• <b>{exp.azienda}</b> ({exp.periodo}) - Commessa: {exp.commessa}<br/><i>{exp.descrizione}</i>"
                    story.append(Paragraph(exp_text, styles['Normal']))
                    story.append(Spacer(1, 5))
            else:
                story.append(Paragraph("Nessuna esperienza registrata.", styles['Normal']))
        else:
            story.append(Paragraph("<i>Dati Curriculum non ancora compilati.</i>", styles['Normal']))

        story.append(Spacer(1, 20))
        data_generazione = datetime.now().strftime("%d/%m/%Y %H:%M")
        story.append(
            Paragraph(f"<font size=8 color=gray>Documento generato il {data_generazione}</font>", styles['Normal'])
        )

        doc.build(story)
        return output_path
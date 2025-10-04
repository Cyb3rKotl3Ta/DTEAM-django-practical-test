from abc import ABC, abstractmethod
from typing import Dict, Any, BinaryIO, Optional
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import logging
from ..models import CV
from .translation_service import get_translation_service
from ..utils.cv_data_utils import prepare_cv_data

logger = logging.getLogger(__name__)


class PDFGenerator(ABC):
    @abstractmethod
    def generate(self, data: Dict[str, Any]) -> BinaryIO:
        pass


class CVPDFGenerator(PDFGenerator):
    def __init__(self, page_size=A4):
        self.page_size = page_size
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='CVTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.darkblue,
            borderPadding=5
        ))

        self.styles.add(ParagraphStyle(
            name='SkillItem',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20
        ))

        self.styles.add(ParagraphStyle(
            name='ProjectTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=6,
            textColor=colors.darkgreen
        ))

    def generate(self, cv: CV, language: Optional[str] = None) -> BinaryIO:
        buffer = HttpResponse(content_type='application/pdf')

        # Prepare CV data for potential translation
        cv_data = prepare_cv_data(cv)
        translated_data = None

        if language:
            try:
                translation_service = get_translation_service()
                translated_data = translation_service.translate_cv_content(cv_data, language)
            except Exception as e:
                logger.warning(f"Translation failed for language {language}: {e}")
                translated_data = None

        filename = f"{cv.full_name.replace(' ', '_')}_CV"
        if language:
            filename += f"_{language}"
        filename += ".pdf"

        buffer['Content-Disposition'] = f'attachment; filename="{filename}"'

        doc = SimpleDocTemplate(buffer, pagesize=self.page_size)
        story = []

        story.extend(self._build_header(cv, translated_data))
        story.extend(self._build_contact_info(cv, translated_data))
        story.extend(self._build_bio(cv, translated_data))
        story.extend(self._build_skills(cv, translated_data))
        story.extend(self._build_projects(cv, translated_data))

        doc.build(story)
        return buffer


    def _build_header(self, cv: CV, translated_data: Optional[Dict] = None) -> list:
        if translated_data and translated_data.get('first_name') and translated_data.get('last_name'):
            full_name = f"{translated_data['first_name']} {translated_data['last_name']}"
        else:
            full_name = cv.full_name

        return [
            Paragraph(full_name, self.styles['CVTitle']),
            Spacer(1, 12)
        ]

    def _build_contact_info(self, cv: CV, translated_data: Optional[Dict] = None) -> list:
        contacts = cv.contacts.filter(is_public=True)
        if not contacts.exists():
            return []

        contact_data = []
        for contact in contacts:
            contact_data.append([
                contact.get_contact_type_display(),
                contact.value
            ])

        contact_table = Table(contact_data, colWidths=[1.5*inch, 4*inch])
        contact_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        return [
            Paragraph("Contact Information", self.styles['SectionHeader']),
            contact_table,
            Spacer(1, 12)
        ]

    def _build_bio(self, cv: CV, translated_data: Optional[Dict] = None) -> list:
        bio_text = translated_data.get('bio') if translated_data else cv.bio
        if not bio_text:
            return []

        return [
            Paragraph("Professional Summary", self.styles['SectionHeader']),
            Paragraph(bio_text, self.styles['Normal']),
            Spacer(1, 12)
        ]

    def _build_skills(self, cv: CV, translated_data: Optional[Dict] = None) -> list:
        skills = cv.skills.all()
        if not skills.exists():
            return []

        skills_by_category = {}
        for skill in skills:
            category = skill.get_category_display()
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(skill)

        story = [Paragraph("Skills & Expertise", self.styles['SectionHeader'])]

        for category, category_skills in skills_by_category.items():
            story.append(Paragraph(f"<b>{category}</b>", self.styles['Normal']))
            for skill in category_skills:
                skill_text = f"• {skill.name} ({skill.proficiency_level}/5)"
                if skill.description:
                    skill_text += f" - {skill.description}"
                story.append(Paragraph(skill_text, self.styles['SkillItem']))
            story.append(Spacer(1, 6))

        story.append(Spacer(1, 12))
        return story

    def _build_projects(self, cv: CV, translated_data: Optional[Dict] = None) -> list:
        projects = cv.projects.all()
        if not projects.exists():
            return []

        story = [Paragraph("Projects", self.styles['SectionHeader'])]

        for project in projects:
            story.append(Paragraph(project.title, self.styles['ProjectTitle']))

            project_info = []
            if project.status:
                project_info.append(f"<b>Status:</b> {project.get_status_display()}")
            if project.start_date:
                end_date = project.end_date.strftime("%B %Y") if project.end_date else "Present"
                project_info.append(f"<b>Duration:</b> {project.start_date.strftime('%B %Y')} - {end_date}")
            if project.technologies_used:
                project_info.append(f"<b>Technologies:</b> {project.technologies_used}")
            if project.project_url:
                project_info.append(f"<b>URL:</b> {project.project_url}")

            for info in project_info:
                story.append(Paragraph(info, self.styles['Normal']))

            if project.description:
                story.append(Paragraph(project.description, self.styles['Normal']))

            story.append(Spacer(1, 12))

        return story


class PDFService:
    def __init__(self, generator: PDFGenerator = None):
        self.generator = generator or CVPDFGenerator()

    def generate_cv_pdf(self, cv: CV, language: Optional[str] = None) -> HttpResponse:
        return self.generator.generate(cv, language)

    def generate_cv_pdf_inline(self, cv: CV, language: Optional[str] = None) -> HttpResponse:
        buffer = HttpResponse(content_type='application/pdf')

        # Prepare CV data for potential translation
        cv_data = prepare_cv_data(cv)
        translated_data = None

        if language:
            try:
                translation_service = get_translation_service()
                translated_data = translation_service.translate_cv_content(cv_data, language)
            except Exception as e:
                logger.warning(f"Translation failed for language {language}: {e}")
                translated_data = None

        filename = f"{cv.full_name.replace(' ', '_')}_CV"
        if language:
            filename += f"_{language}"
        filename += ".pdf"

        buffer['Content-Disposition'] = f'inline; filename="{filename}"'

        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []

        story.extend(self.generator._build_header(cv, translated_data))
        story.extend(self.generator._build_contact_info(cv, translated_data))
        story.extend(self.generator._build_bio(cv, translated_data))
        story.extend(self.generator._build_skills(cv, translated_data))
        story.extend(self.generator._build_projects(cv, translated_data))

        doc.build(story)
        return buffer

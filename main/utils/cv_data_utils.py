from typing import Dict, Any
from ..models import CV


def prepare_cv_data(cv: CV) -> Dict[str, Any]:
    return {
        'first_name': cv.first_name,
        'last_name': cv.last_name,
        'bio': cv.bio,
        'skills': [{'name': skill.name, 'description': skill.description} for skill in cv.skills.all()],
        'projects': [{'title': project.title, 'description': project.description} for project in cv.projects.all()],
        'contacts': [{'value': contact.value, 'contact_type': contact.get_contact_type_display()} for contact in cv.contacts.filter(is_public=True)]
    }

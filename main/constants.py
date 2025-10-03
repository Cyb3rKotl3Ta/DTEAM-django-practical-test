"""
Constants for the main app.

Following DRY principle by centralizing constants.
"""

# CV Status choices
CV_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('published', 'Published'),
    ('archived', 'Archived'),
]

# Skill categories
SKILL_CATEGORIES = [
    ('technical', 'Technical'),
    ('soft', 'Soft Skills'),
    ('language', 'Languages'),
    ('certification', 'Certifications'),
]

# Project status
PROJECT_STATUS_CHOICES = [
    ('completed', 'Completed'),
    ('in_progress', 'In Progress'),
    ('planned', 'Planned'),
]

# Contact types
CONTACT_TYPES = [
    ('email', 'Email'),
    ('phone', 'Phone'),
    ('linkedin', 'LinkedIn'),
    ('github', 'GitHub'),
    ('website', 'Website'),
    ('other', 'Other'),
]

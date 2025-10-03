"""
Custom managers for CV model.

Following Single Responsibility Principle - each manager handles specific queries.
"""

from django.db import models


class CVManager(models.Manager):
    """
    Custom manager for CV model.
    
    Following Single Responsibility Principle - handles CV-specific queries.
    """
    
    def active(self):
        """Return only active CVs."""
        return self.filter(is_active=True)
    
    def published(self):
        """Return only published CVs."""
        return self.filter(status='published', is_active=True)
    
    def draft(self):
        """Return only draft CVs."""
        return self.filter(status='draft')
    
    def by_name(self, first_name=None, last_name=None):
        """Filter CVs by name."""
        queryset = self.all()
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)
        return queryset
    
    def with_skills(self):
        """Return CVs that have at least one skill."""
        return self.filter(skills__isnull=False).distinct()
    
    def with_projects(self):
        """Return CVs that have at least one project."""
        return self.filter(projects__isnull=False).distinct()
    
    def featured_projects(self):
        """Return CVs that have featured projects."""
        return self.filter(projects__is_featured=True).distinct()


class SkillManager(models.Manager):
    """
    Custom manager for Skill model.
    
    Following Single Responsibility Principle - handles skill-specific queries.
    """
    
    def by_category(self, category):
        """Return skills filtered by category."""
        return self.filter(category=category)
    
    def technical(self):
        """Return only technical skills."""
        return self.filter(category='technical')
    
    def soft_skills(self):
        """Return only soft skills."""
        return self.filter(category='soft')
    
    def languages(self):
        """Return only language skills."""
        return self.filter(category='language')
    
    def certifications(self):
        """Return only certification skills."""
        return self.filter(category='certification')
    
    def high_proficiency(self, level=4):
        """Return skills with proficiency level >= specified level."""
        return self.filter(proficiency_level__gte=level)
    
    def by_proficiency(self, min_level=1, max_level=5):
        """Return skills within proficiency range."""
        return self.filter(proficiency_level__gte=min_level, proficiency_level__lte=max_level)


class ProjectManager(models.Manager):
    """
    Custom manager for Project model.
    
    Following Single Responsibility Principle - handles project-specific queries.
    """
    
    def active(self):
        """Return only active projects."""
        return self.filter(status='in_progress')
    
    def completed(self):
        """Return only completed projects."""
        return self.filter(status='completed')
    
    def planned(self):
        """Return only planned projects."""
        return self.filter(status='planned')
    
    def featured(self):
        """Return only featured projects."""
        return self.filter(is_featured=True)
    
    def recent(self, days=30):
        """Return projects from the last N days."""
        from django.utils import timezone
        from datetime import timedelta
        cutoff_date = timezone.now().date() - timedelta(days=days)
        return self.filter(start_date__gte=cutoff_date)
    
    def by_technology(self, technology):
        """Return projects that use specific technology."""
        return self.filter(technologies_used__icontains=technology)
    
    def ongoing(self):
        """Return projects that are currently ongoing."""
        return self.filter(status='in_progress', end_date__isnull=True)


class ContactManager(models.Manager):
    """
    Custom manager for Contact model.
    
    Following Single Responsibility Principle - handles contact-specific queries.
    """
    
    def primary(self):
        """Return only primary contacts."""
        return self.filter(is_primary=True)
    
    def public(self):
        """Return only public contacts."""
        return self.filter(is_public=True)
    
    def by_type(self, contact_type):
        """Return contacts of specific type."""
        return self.filter(contact_type=contact_type)
    
    def emails(self):
        """Return only email contacts."""
        return self.filter(contact_type='email')
    
    def phones(self):
        """Return only phone contacts."""
        return self.filter(contact_type='phone')
    
    def social_media(self):
        """Return social media contacts."""
        return self.filter(contact_type__in=['linkedin', 'github'])
    
    def websites(self):
        """Return website contacts."""
        return self.filter(contact_type='website')

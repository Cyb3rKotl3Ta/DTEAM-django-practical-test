from django.db import models


class CVManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)
    
    def published(self):
        return self.filter(status='published', is_active=True)
    
    def draft(self):
        return self.filter(status='draft')
    
    def by_name(self, first_name=None, last_name=None):
        queryset = self.all()
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)
        return queryset
    
    def with_skills(self):
        return self.filter(skills__isnull=False).distinct()
    
    def with_projects(self):
        return self.filter(projects__isnull=False).distinct()
    
    def featured_projects(self):
        return self.filter(projects__is_featured=True).distinct()


class SkillManager(models.Manager):
    def by_category(self, category):
        return self.filter(category=category)
    
    def technical(self):
        return self.filter(category='technical')
    
    def soft_skills(self):
        return self.filter(category='soft')
    
    def languages(self):
        return self.filter(category='language')
    
    def certifications(self):
        return self.filter(category='certification')
    
    def high_proficiency(self, level=4):
        return self.filter(proficiency_level__gte=level)
    
    def by_proficiency(self, min_level=1, max_level=5):
        return self.filter(proficiency_level__gte=min_level, proficiency_level__lte=max_level)


class ProjectManager(models.Manager):
    def active(self):
        return self.filter(status='in_progress')
    
    def completed(self):
        return self.filter(status='completed')
    
    def planned(self):
        return self.filter(status='planned')
    
    def featured(self):
        return self.filter(is_featured=True)
    
    def recent(self, days=30):
        from django.utils import timezone
        from datetime import timedelta
        cutoff_date = timezone.now().date() - timedelta(days=days)
        return self.filter(start_date__gte=cutoff_date)
    
    def by_technology(self, technology):
        return self.filter(technologies_used__icontains=technology)
    
    def ongoing(self):
        return self.filter(status='in_progress', end_date__isnull=True)


class ContactManager(models.Manager):
    def primary(self):
        return self.filter(is_primary=True)
    
    def public(self):
        return self.filter(is_public=True)
    
    def by_type(self, contact_type):
        return self.filter(contact_type=contact_type)
    
    def emails(self):
        return self.filter(contact_type='email')
    
    def phones(self):
        return self.filter(contact_type='phone')
    
    def social_media(self):
        return self.filter(contact_type__in=['linkedin', 'github'])
    
    def websites(self):
        return self.filter(contact_type='website')

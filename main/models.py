"""
Models for the main app.

Following SOLID principles, DRY approach, and proper data organization.
"""

from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator
from django.utils import timezone
from .constants import CV_STATUS_CHOICES, SKILL_CATEGORIES, PROJECT_STATUS_CHOICES, CONTACT_TYPES
from .managers.cv_manager import CVManager, SkillManager, ProjectManager, ContactManager


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides created_at and updated_at fields.
    
    Following DRY principle by providing common fields to all models.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CV(TimeStampedModel):
    """
    Main CV model representing a person's curriculum vitae.
    
    Following Single Responsibility Principle - handles only CV data.
    """
    first_name = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(2)],
        help_text="Person's first name"
    )
    last_name = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(2)],
        help_text="Person's last name"
    )
    bio = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Personal biography and summary"
    )
    status = models.CharField(
        max_length=20,
        choices=CV_STATUS_CHOICES,
        default='draft',
        help_text="Current status of the CV"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this CV is currently active"
    )

    # Custom managers
    objects = CVManager()

    class Meta:
        verbose_name = "CV"
        verbose_name_plural = "CVs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        """Return the full name of the person."""
        return f"{self.first_name} {self.last_name}"

    def get_skills_by_category(self, category):
        """Get skills filtered by category."""
        return self.skills.filter(category=category)

    def get_active_projects(self):
        """Get only active projects."""
        return self.projects.filter(status='in_progress')

    def get_primary_contact(self, contact_type):
        """Get primary contact of specific type."""
        return self.contacts.filter(contact_type=contact_type, is_primary=True).first()


class Skill(TimeStampedModel):
    """
    Skill model representing a person's skills.
    
    Following Single Responsibility Principle - handles only skill data.
    """
    cv = models.ForeignKey(
        CV,
        on_delete=models.CASCADE,
        related_name='skills',
        help_text="CV this skill belongs to"
    )
    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(2)],
        help_text="Name of the skill"
    )
    category = models.CharField(
        max_length=20,
        choices=SKILL_CATEGORIES,
        help_text="Category of the skill"
    )
    proficiency_level = models.PositiveIntegerField(
        default=1,
        choices=[(i, f"{i}/5") for i in range(1, 6)],
        help_text="Proficiency level from 1 to 5"
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        help_text="Additional description of the skill"
    )

    # Custom managers
    objects = SkillManager()

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"
        ordering = ['category', 'name']
        unique_together = ['cv', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['proficiency_level']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Project(TimeStampedModel):
    """
    Project model representing a person's projects.
    
    Following Single Responsibility Principle - handles only project data.
    """
    cv = models.ForeignKey(
        CV,
        on_delete=models.CASCADE,
        related_name='projects',
        help_text="CV this project belongs to"
    )
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3)],
        help_text="Title of the project"
    )
    description = models.TextField(
        max_length=1000,
        help_text="Detailed description of the project"
    )
    status = models.CharField(
        max_length=20,
        choices=PROJECT_STATUS_CHOICES,
        default='completed',
        help_text="Current status of the project"
    )
    start_date = models.DateField(
        help_text="Project start date"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Project end date (null if ongoing)"
    )
    technologies_used = models.TextField(
        max_length=500,
        blank=True,
        help_text="Technologies and tools used in the project"
    )
    project_url = models.URLField(
        blank=True,
        help_text="URL to the project (GitHub, live demo, etc.)"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Whether this project should be featured prominently"
    )

    # Custom managers
    objects = ProjectManager()

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-start_date', '-is_featured']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return self.title

    @property
    def duration(self):
        """Calculate project duration."""
        if self.end_date:
            return self.end_date - self.start_date
        return timezone.now().date() - self.start_date

    def is_ongoing(self):
        """Check if project is currently ongoing."""
        return self.end_date is None and self.status == 'in_progress'


class Contact(TimeStampedModel):
    """
    Contact model representing different ways to contact a person.
    
    Following Single Responsibility Principle - handles only contact data.
    """
    cv = models.ForeignKey(
        CV,
        on_delete=models.CASCADE,
        related_name='contacts',
        help_text="CV this contact belongs to"
    )
    contact_type = models.CharField(
        max_length=20,
        choices=CONTACT_TYPES,
        help_text="Type of contact information"
    )
    value = models.CharField(
        max_length=200,
        help_text="The actual contact value (email, phone, URL, etc.)"
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Whether this is the primary contact of this type"
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Whether this contact should be publicly visible"
    )

    # Custom managers
    objects = ContactManager()

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
        ordering = ['contact_type', '-is_primary']
        unique_together = ['cv', 'contact_type', 'is_primary']
        indexes = [
            models.Index(fields=['contact_type']),
            models.Index(fields=['is_primary']),
            models.Index(fields=['is_public']),
        ]

    def __str__(self):
        return f"{self.get_contact_type_display()}: {self.value}"

    def clean(self):
        """Validate contact data based on type."""
        from django.core.exceptions import ValidationError
        
        if self.contact_type == 'email':
            EmailValidator()(self.value)
        elif self.contact_type == 'phone' and not self.value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValidationError("Phone number should contain only digits, spaces, hyphens, and plus sign")
        elif self.contact_type in ['linkedin', 'github', 'website'] and not self.value.startswith(('http://', 'https://')):
            self.value = f"https://{self.value}"
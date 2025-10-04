from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator
from django.utils import timezone
from .constants.choices import CV_STATUS_CHOICES, SKILL_CATEGORIES, PROJECT_STATUS_CHOICES, CONTACT_TYPES
from .managers.cv_manager import CVManager, SkillManager, ProjectManager, ContactManager


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CV(TimeStampedModel):
    first_name = models.CharField(max_length=50, validators=[MinLengthValidator(2)])
    last_name = models.CharField(max_length=50, validators=[MinLengthValidator(2)])
    bio = models.TextField(max_length=1000, blank=True)
    status = models.CharField(max_length=20, choices=CV_STATUS_CHOICES, default='draft')
    is_active = models.BooleanField(default=True)

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
        return f"{self.first_name} {self.last_name}"

    def get_skills_by_category(self, category):
        return self.skills.filter(category=category)

    def get_active_projects(self):
        return self.projects.filter(status='in_progress')

    def get_primary_contact(self, contact_type):
        return self.contacts.filter(contact_type=contact_type, is_primary=True).first()


class Skill(TimeStampedModel):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100, validators=[MinLengthValidator(2)])
    category = models.CharField(max_length=20, choices=SKILL_CATEGORIES)
    proficiency_level = models.PositiveIntegerField(default=1, choices=[(i, f"{i}/5") for i in range(1, 6)])
    description = models.TextField(max_length=500, blank=True)

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
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200, validators=[MinLengthValidator(3)])
    description = models.TextField(max_length=1000)
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='completed')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    technologies_used = models.TextField(max_length=500, blank=True)
    project_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)

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
        if self.end_date:
            return self.end_date - self.start_date
        return timezone.now().date() - self.start_date

    def is_ongoing(self):
        return self.end_date is None and self.status == 'in_progress'


class Contact(TimeStampedModel):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='contacts')
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPES)
    value = models.CharField(max_length=200)
    is_primary = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)

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
        from django.core.exceptions import ValidationError

        if self.contact_type == 'email':
            EmailValidator()(self.value)
        elif self.contact_type == 'phone' and not self.value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValidationError("Phone number should contain only digits, spaces, hyphens, and plus sign")
        elif self.contact_type in ['linkedin', 'github', 'website'] and not self.value.startswith(('http://', 'https://')):
            self.value = f"https://{self.value}"
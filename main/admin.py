from django.contrib import admin
from django.utils.html import format_html
from .models import CV, Skill, Project, Contact


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1
    fields = ['name', 'category', 'proficiency_level', 'description']
    ordering = ['category', 'name']


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1
    fields = ['title', 'status', 'start_date', 'end_date', 'is_featured']
    ordering = ['-start_date']


class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1
    fields = ['contact_type', 'value', 'is_primary', 'is_public']
    ordering = ['contact_type', '-is_primary']


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'status', 'is_active', 'skills_count', 'projects_count', 'created_at']
    list_filter = ['status', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'bio']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SkillInline, ProjectInline, ContactInline]
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'bio')
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def skills_count(self, obj):
        return obj.skills.count()
    skills_count.short_description = 'Skills'
    
    def projects_count(self, obj):
        return obj.projects.count()
    projects_count.short_description = 'Projects'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'cv', 'category', 'proficiency_level', 'created_at']
    list_filter = ['category', 'proficiency_level', 'created_at']
    search_fields = ['name', 'description', 'cv__first_name', 'cv__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Skill Information', {
            'fields': ('cv', 'name', 'category', 'proficiency_level', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'cv', 'status', 'start_date', 'end_date', 'is_featured', 'duration_display']
    list_filter = ['status', 'is_featured', 'start_date', 'created_at']
    search_fields = ['title', 'description', 'technologies_used', 'cv__first_name', 'cv__last_name']
    readonly_fields = ['created_at', 'updated_at', 'duration_display']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Project Information', {
            'fields': ('cv', 'title', 'description', 'status')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'duration_display')
        }),
        ('Details', {
            'fields': ('technologies_used', 'project_url', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        if obj.end_date:
            duration = obj.end_date - obj.start_date
            return f"{duration.days} days"
        elif obj.status == 'in_progress':
            duration = obj.duration
            return f"{duration.days} days (ongoing)"
        return "N/A"
    duration_display.short_description = 'Duration'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['contact_type', 'value', 'cv', 'is_primary', 'is_public', 'created_at']
    list_filter = ['contact_type', 'is_primary', 'is_public', 'created_at']
    search_fields = ['value', 'cv__first_name', 'cv__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('cv', 'contact_type', 'value')
        }),
        ('Settings', {
            'fields': ('is_primary', 'is_public')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

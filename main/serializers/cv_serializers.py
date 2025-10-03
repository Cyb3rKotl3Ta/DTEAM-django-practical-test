from rest_framework import serializers
from ..models import CV, Skill, Project, Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'contact_type', 'value', 'is_primary', 'is_public']
        read_only_fields = ['id']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'proficiency_level', 'description']
        read_only_fields = ['id']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'status', 'start_date',
            'end_date', 'technologies_used', 'project_url', 'is_featured'
        ]
        read_only_fields = ['id']


class CVListSerializer(serializers.ModelSerializer):
    skills_count = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()

    class Meta:
        model = CV
        fields = [
            'id', 'first_name', 'last_name', 'bio', 'status',
            'is_active', 'created_at', 'updated_at', 'skills_count', 'projects_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_skills_count(self, obj):
        return obj.skills.count()

    def get_projects_count(self, obj):
        return obj.projects.count()


class CVDetailSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    contacts = ContactSerializer(many=True, read_only=True)
    skills_by_category = serializers.SerializerMethodField()
    featured_projects = serializers.SerializerMethodField()
    other_projects = serializers.SerializerMethodField()

    class Meta:
        model = CV
        fields = [
            'id', 'first_name', 'last_name', 'bio', 'status', 'is_active',
            'created_at', 'updated_at', 'skills', 'projects', 'contacts',
            'skills_by_category', 'featured_projects', 'other_projects'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_skills_by_category(self, obj):
        skills_by_category = {}
        for skill in obj.skills.all().order_by('category', 'name'):
            category = skill.get_category_display()
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(SkillSerializer(skill).data)
        return skills_by_category

    def get_featured_projects(self, obj):
        featured = obj.projects.filter(is_featured=True).order_by('-start_date')
        return ProjectSerializer(featured, many=True).data

    def get_other_projects(self, obj):
        other = obj.projects.filter(is_featured=False).order_by('-start_date')
        return ProjectSerializer(other, many=True).data


class CVCreateUpdateSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, required=False)
    projects = ProjectSerializer(many=True, required=False)
    contacts = ContactSerializer(many=True, required=False)

    class Meta:
        model = CV
        fields = [
            'id', 'first_name', 'last_name', 'bio', 'status', 'is_active',
            'skills', 'projects', 'contacts'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        skills_data = validated_data.pop('skills', [])
        projects_data = validated_data.pop('projects', [])
        contacts_data = validated_data.pop('contacts', [])

        cv = CV.objects.create(**validated_data)

        for skill_data in skills_data:
            Skill.objects.create(cv=cv, **skill_data)

        for project_data in projects_data:
            Project.objects.create(cv=cv, **project_data)

        for contact_data in contacts_data:
            Contact.objects.create(cv=cv, **contact_data)

        return cv

    def update(self, instance, validated_data):
        skills_data = validated_data.pop('skills', None)
        projects_data = validated_data.pop('projects', None)
        contacts_data = validated_data.pop('contacts', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if skills_data is not None:
            instance.skills.all().delete()
            for skill_data in skills_data:
                Skill.objects.create(cv=instance, **skill_data)

        if projects_data is not None:
            instance.projects.all().delete()
            for project_data in projects_data:
                Project.objects.create(cv=instance, **project_data)

        if contacts_data is not None:
            instance.contacts.all().delete()
            for contact_data in contacts_data:
                Contact.objects.create(cv=instance, **contact_data)

        return instance

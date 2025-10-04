from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import CV, Skill, Project, Contact
from .constants.choices import CV_STATUS_CHOICES, SKILL_CATEGORIES, PROJECT_STATUS_CHOICES, CONTACT_TYPES


class CVViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.cv1 = CV.objects.create(
            first_name="John",
            last_name="Doe",
            bio="Test bio for John Doe",
            status="published",
            is_active=True
        )

        self.cv2 = CV.objects.create(
            first_name="Jane",
            last_name="Smith",
            bio="Test bio for Jane Smith",
            status="draft",
            is_active=True
        )

        self.skill1 = Skill.objects.create(
            cv=self.cv1,
            name="Python",
            category="technical",
            proficiency_level=5,
            description="Expert Python developer"
        )

        self.skill2 = Skill.objects.create(
            cv=self.cv1,
            name="Leadership",
            category="soft",
            proficiency_level=4,
            description="Team leadership skills"
        )

        self.project1 = Project.objects.create(
            cv=self.cv1,
            title="Test Project",
            description="A test project description",
            status="completed",
            start_date="2023-01-01",
            end_date="2023-06-30",
            technologies_used="Python, Django",
            is_featured=True
        )

        self.contact1 = Contact.objects.create(
            cv=self.cv1,
            contact_type="email",
            value="john@example.com",
            is_primary=True,
            is_public=True
        )

    def test_cv_list_view_returns_published_cvs_only(self):
        response = self.client.get(reverse('main:cv_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertNotContains(response, "Jane Smith")
        self.assertContains(response, "Professional CVs")

    def test_cv_list_view_template_used(self):
        response = self.client.get(reverse('main:cv_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/cv_list.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_cv_list_view_context_data(self):
        response = self.client.get(reverse('main:cv_list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('cvs', response.context)
        self.assertIn('total_cvs', response.context)
        self.assertEqual(response.context['total_cvs'], 1)

    def test_cv_detail_view_returns_correct_cv(self):
        response = self.client.get(reverse('main:cv_detail', args=[self.cv1.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertContains(response, "Test bio for John Doe")
        self.assertContains(response, "Python")
        self.assertContains(response, "Test Project")

    def test_cv_detail_view_template_used(self):
        response = self.client.get(reverse('main:cv_detail', args=[self.cv1.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/cv_detail.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_cv_detail_view_context_data(self):
        response = self.client.get(reverse('main:cv_detail', args=[self.cv1.id]))

        self.assertEqual(response.status_code, 200)
        self.assertIn('cv', response.context)
        self.assertIn('skills_by_category', response.context)
        self.assertIn('featured_projects', response.context)
        self.assertIn('other_projects', response.context)
        self.assertIn('total_skills', response.context)
        self.assertIn('total_projects', response.context)
        self.assertIn('total_contacts', response.context)

        self.assertEqual(response.context['cv'], self.cv1)
        self.assertEqual(response.context['total_skills'], 2)
        self.assertEqual(response.context['total_projects'], 1)
        self.assertEqual(response.context['total_contacts'], 1)

    def test_cv_detail_view_skills_by_category(self):
        response = self.client.get(reverse('main:cv_detail', args=[self.cv1.id]))

        self.assertEqual(response.status_code, 200)
        skills_by_category = response.context['skills_by_category']

        self.assertIn('Technical', skills_by_category)
        self.assertIn('Soft Skills', skills_by_category)
        self.assertEqual(len(skills_by_category['Technical']), 1)
        self.assertEqual(len(skills_by_category['Soft Skills']), 1)

    def test_cv_detail_view_featured_projects(self):
        response = self.client.get(reverse('main:cv_detail', args=[self.cv1.id]))

        self.assertEqual(response.status_code, 200)
        featured_projects = response.context['featured_projects']

        self.assertEqual(len(featured_projects), 1)
        self.assertEqual(featured_projects[0], self.project1)

    def test_cv_detail_view_404_for_draft_cv(self):
        response = self.client.get(reverse('main:cv_detail', args=[self.cv2.id]))

        self.assertEqual(response.status_code, 404)

    def test_cv_detail_view_404_for_nonexistent_cv(self):
        response = self.client.get(reverse('main:cv_detail', args=[999]))

        self.assertEqual(response.status_code, 404)

    def test_api_home_view_returns_json(self):
        response = self.client.get(reverse('main:api_home'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = response.json()
        self.assertEqual(data['message'], 'CVProject is working!')
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['version'], '1.0.0')

    def test_cv_list_view_with_no_cvs(self):
        CV.objects.filter(status='published').delete()

        response = self.client.get(reverse('main:cv_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No CVs Found")
        self.assertEqual(response.context['total_cvs'], 0)

    def test_cv_detail_view_contact_links(self):
        response = self.client.get(reverse('main:cv_detail', args=[self.cv1.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "mailto:john@example.com")

    def test_cv_detail_view_project_status_badges(self):
        response = self.client.get(reverse('main:cv_detail', args=[self.cv1.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Completed")

    def test_cv_detail_view_skill_proficiency_bars(self):
        response = self.client.get(reverse('main:cv_detail', args=[self.cv1.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "5/5")
        self.assertContains(response, "4/5")


class CVModelsTestCase(TestCase):
    def setUp(self):
        self.cv = CV.objects.create(
            first_name="Test",
            last_name="User",
            bio="Test bio",
            status="published",
            is_active=True
        )

    def test_cv_full_name_property(self):
        self.assertEqual(self.cv.full_name, "Test User")

    def test_cv_str_representation(self):
        self.assertEqual(str(self.cv), "Test User")

    def test_cv_published_manager(self):
        CV.objects.create(
            first_name="Draft",
            last_name="User",
            bio="Draft bio",
            status="draft",
            is_active=True
        )

        published_cvs = CV.objects.published()
        self.assertEqual(published_cvs.count(), 1)
        self.assertEqual(published_cvs.first(), self.cv)

    def test_skill_str_representation(self):
        skill = Skill.objects.create(
            cv=self.cv,
            name="Python",
            category="technical",
            proficiency_level=5
        )
        self.assertEqual(str(skill), "Python (Technical)")

    def test_project_str_representation(self):
        project = Project.objects.create(
            cv=self.cv,
            title="Test Project",
            description="Test description",
            status="completed",
            start_date="2023-01-01"
        )
        self.assertEqual(str(project), "Test Project")

    def test_contact_str_representation(self):
        contact = Contact.objects.create(
            cv=self.cv,
            contact_type="email",
            value="test@example.com",
            is_primary=True,
            is_public=True
        )
        self.assertEqual(str(contact), "Email: test@example.com")
from django.test import TestCase
# from django.urls import reverse  # Using direct URLs instead
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
import json

from ..models import CV, Skill, Project, Contact


class CVAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)

        self.cv_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'bio': 'Test bio for API testing',
            'status': 'published',
            'is_active': True
        }

        self.skill_data = {
            'name': 'Python',
            'category': 'technical',
            'proficiency_level': 5,
            'description': 'Advanced Python programming'
        }

        self.project_data = {
            'title': 'Test Project',
            'description': 'Test project description',
            'status': 'completed',
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'technologies_used': 'Python, Django',
            'project_url': 'https://example.com',
            'is_featured': True
        }

        self.contact_data = {
            'contact_type': 'email',
            'value': 'john.doe@example.com',
            'is_primary': True,
            'is_public': True
        }

    def test_cv_list_unauthorized(self):
        response = self.client.get('/api/cvs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_cv_list_authorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/cvs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_cv_create_unauthorized(self):
        response = self.client.post('/api/cvs/', self.cv_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cv_create_authorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/cvs/', self.cv_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CV.objects.count(), 1)
        self.assertEqual(CV.objects.first().first_name, 'John')

    def test_cv_create_with_related_data(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        cv_with_relations = {
            **self.cv_data,
            'skills': [self.skill_data],
            'projects': [self.project_data],
            'contacts': [self.contact_data]
        }

        response = self.client.post(
            reverse('cv-list'),
            json.dumps(cv_with_relations),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cv = CV.objects.first()
        self.assertEqual(cv.skills.count(), 1)
        self.assertEqual(cv.projects.count(), 1)
        self.assertEqual(cv.contacts.count(), 1)

    def test_cv_retrieve_unauthorized(self):
        cv = CV.objects.create(**self.cv_data)
        response = self.client.get(reverse('cv-detail', kwargs={'pk': cv.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'John')

    def test_cv_retrieve_authorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        cv = CV.objects.create(**self.cv_data)
        response = self.client.get(reverse('cv-detail', kwargs={'pk': cv.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'John')

    def test_cv_update_unauthorized(self):
        cv = CV.objects.create(**self.cv_data)
        update_data = {'first_name': 'Jane'}
        response = self.client.put(
            reverse('cv-detail', kwargs={'pk': cv.pk}),
            json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cv_update_authorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        cv = CV.objects.create(**self.cv_data)
        update_data = {**self.cv_data, 'first_name': 'Jane'}
        response = self.client.put(
            reverse('cv-detail', kwargs={'pk': cv.pk}),
            json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cv.refresh_from_db()
        self.assertEqual(cv.first_name, 'Jane')

    def test_cv_partial_update_authorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        cv = CV.objects.create(**self.cv_data)
        update_data = {'first_name': 'Jane'}
        response = self.client.patch(
            reverse('cv-detail', kwargs={'pk': cv.pk}),
            json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cv.refresh_from_db()
        self.assertEqual(cv.first_name, 'Jane')

    def test_cv_delete_unauthorized(self):
        cv = CV.objects.create(**self.cv_data)
        response = self.client.delete(reverse('cv-detail', kwargs={'pk': cv.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cv_delete_authorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        cv = CV.objects.create(**self.cv_data)
        response = self.client.delete(reverse('cv-detail', kwargs={'pk': cv.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CV.objects.count(), 0)

    def test_cv_not_found(self):
        response = self.client.get(reverse('cv-detail', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cv_skills_endpoint(self):
        cv = CV.objects.create(**self.cv_data)
        Skill.objects.create(cv=cv, **self.skill_data)

        response = self.client.get(reverse('cv-skills', kwargs={'pk': cv.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Python')

    def test_cv_projects_endpoint(self):
        cv = CV.objects.create(**self.cv_data)
        Project.objects.create(cv=cv, **self.project_data)

        response = self.client.get(reverse('cv-projects', kwargs={'pk': cv.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Project')

    def test_cv_contacts_endpoint(self):
        cv = CV.objects.create(**self.cv_data)
        Contact.objects.create(cv=cv, **self.contact_data)

        response = self.client.get(reverse('cv-contacts', kwargs={'pk': cv.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['value'], 'john.doe@example.com')

    def test_cv_featured_projects_endpoint(self):
        cv = CV.objects.create(**self.cv_data)
        Project.objects.create(cv=cv, **self.project_data)

        response = self.client.get(reverse('cv-featured-projects', kwargs={'pk': cv.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Project')

    def test_cv_skills_by_category_endpoint(self):
        cv = CV.objects.create(**self.cv_data)
        Skill.objects.create(cv=cv, **self.skill_data)

        response = self.client.get(reverse('cv-skills-by-category', kwargs={'pk': cv.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Technical', response.data)
        self.assertEqual(len(response.data['Technical']), 1)

    def test_cv_filtering_by_status(self):
        CV.objects.create(**self.cv_data)
        draft_cv = CV.objects.create(
            first_name='Jane',
            last_name='Smith',
            bio='Draft CV',
            status='draft'
        )

        response = self.client.get(reverse('cv-list'), {'status': 'published'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'published')

    def test_cv_search(self):
        CV.objects.create(**self.cv_data)

        response = self.client.get(reverse('cv-list'), {'search': 'John'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'John')

    def test_cv_ordering(self):
        cv1 = CV.objects.create(
            first_name='Alice',
            last_name='Smith',
            bio='Test bio',
            status='published'
        )
        cv2 = CV.objects.create(
            first_name='Bob',
            last_name='Johnson',
            bio='Test bio',
            status='published'
        )

        response = self.client.get(reverse('cv-list'), {'ordering': 'first_name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['first_name'], 'Alice')
        self.assertEqual(response.data['results'][1]['first_name'], 'Bob')

    def test_cv_pagination(self):
        for i in range(25):
            CV.objects.create(
                first_name=f'User{i}',
                last_name='Test',
                bio='Test bio',
                status='published'
            )

        response = self.client.get(reverse('cv-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 20)
        self.assertIsNotNone(response.data['next'])

    def test_cv_validation_errors(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        invalid_data = {
            'first_name': '',  # Empty name should fail
            'last_name': 'Doe',
            'bio': 'Test bio',
            'status': 'invalid_status'  # Invalid status
        }

        response = self.client.post(reverse('cv-list'), invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response.data)
        self.assertIn('status', response.data)


class SkillAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)

        self.cv = CV.objects.create(
            first_name='John',
            last_name='Doe',
            bio='Test bio',
            status='published'
        )

        self.skill_data = {
            'cv': self.cv.id,
            'name': 'Python',
            'category': 'technical',
            'proficiency_level': 5,
            'description': 'Advanced Python programming'
        }

    def test_skill_create_unauthorized(self):
        response = self.client.post(reverse('skill-list'), self.skill_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_skill_create_authorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(reverse('skill-list'), self.skill_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Skill.objects.count(), 1)

    def test_skill_list(self):
        Skill.objects.create(cv=self.cv, **{k: v for k, v in self.skill_data.items() if k != 'cv'})
        response = self.client.get(reverse('skill-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_skill_retrieve(self):
        skill = Skill.objects.create(cv=self.cv, **{k: v for k, v in self.skill_data.items() if k != 'cv'})
        response = self.client.get(reverse('skill-detail', kwargs={'pk': skill.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Python')

    def test_skill_update_authorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        skill = Skill.objects.create(cv=self.cv, **{k: v for k, v in self.skill_data.items() if k != 'cv'})
        update_data = {**self.skill_data, 'name': 'JavaScript'}
        response = self.client.put(
            reverse('skill-detail', kwargs={'pk': skill.pk}),
            json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        skill.refresh_from_db()
        self.assertEqual(skill.name, 'JavaScript')

    def test_skill_delete_authorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        skill = Skill.objects.create(cv=self.cv, **{k: v for k, v in self.skill_data.items() if k != 'cv'})
        response = self.client.delete(reverse('skill-detail', kwargs={'pk': skill.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Skill.objects.count(), 0)


class ProjectAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)

        self.cv = CV.objects.create(
            first_name='John',
            last_name='Doe',
            bio='Test bio',
            status='published'
        )

        self.project_data = {
            'cv': self.cv.id,
            'title': 'Test Project',
            'description': 'Test project description',
            'status': 'completed',
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'technologies_used': 'Python, Django',
            'project_url': 'https://example.com',
            'is_featured': True
        }

    def test_project_create_unauthorized(self):
        response = self.client.post(reverse('project-list'), self.project_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_project_create_authorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(reverse('project-list'), self.project_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)

    def test_project_list(self):
        Project.objects.create(cv=self.cv, **{k: v for k, v in self.project_data.items() if k != 'cv'})
        response = self.client.get(reverse('project-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_project_retrieve(self):
        project = Project.objects.create(cv=self.cv, **{k: v for k, v in self.project_data.items() if k != 'cv'})
        response = self.client.get(reverse('project-detail', kwargs={'pk': project.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Project')

    def test_project_update_authorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        project = Project.objects.create(cv=self.cv, **{k: v for k, v in self.project_data.items() if k != 'cv'})
        update_data = {**self.project_data, 'title': 'Updated Project'}
        response = self.client.put(
            reverse('project-detail', kwargs={'pk': project.pk}),
            json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project.refresh_from_db()
        self.assertEqual(project.title, 'Updated Project')

    def test_project_delete_authorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        project = Project.objects.create(cv=self.cv, **{k: v for k, v in self.project_data.items() if k != 'cv'})
        response = self.client.delete(reverse('project-detail', kwargs={'pk': project.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)


class ContactAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)

        self.cv = CV.objects.create(
            first_name='John',
            last_name='Doe',
            bio='Test bio',
            status='published'
        )

        self.contact_data = {
            'cv': self.cv.id,
            'contact_type': 'email',
            'value': 'john.doe@example.com',
            'is_primary': True,
            'is_public': True
        }

    def test_contact_create_unauthorized(self):
        response = self.client.post(reverse('contact-list'), self.contact_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_contact_create_authorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(reverse('contact-list'), self.contact_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.count(), 1)

    def test_contact_list(self):
        Contact.objects.create(cv=self.cv, **{k: v for k, v in self.contact_data.items() if k != 'cv'})
        response = self.client.get(reverse('contact-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_contact_retrieve(self):
        contact = Contact.objects.create(cv=self.cv, **{k: v for k, v in self.contact_data.items() if k != 'cv'})
        response = self.client.get(reverse('contact-detail', kwargs={'pk': contact.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 'john.doe@example.com')

    def test_contact_update_authorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        contact = Contact.objects.create(cv=self.cv, **{k: v for k, v in self.contact_data.items() if k != 'cv'})
        update_data = {**self.contact_data, 'value': 'jane.doe@example.com'}
        response = self.client.put(
            reverse('contact-detail', kwargs={'pk': contact.pk}),
            json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contact.refresh_from_db()
        self.assertEqual(contact.value, 'jane.doe@example.com')

    def test_contact_delete_authorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        contact = Contact.objects.create(cv=self.cv, **{k: v for k, v in self.contact_data.items() if k != 'cv'})
        response = self.client.delete(reverse('contact-detail', kwargs={'pk': contact.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Contact.objects.count(), 0)

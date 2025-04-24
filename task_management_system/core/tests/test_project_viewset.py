from django.urls import reverse
from django.db.models import Q
from rest_framework.test import APITestCase
from rest_framework import status

from ..models import User, Project
from ..constants import ADMIN, PROJECT_MANAGER, TECH_LEAD, DEVELOPER, CLIENT


class ProjectViewSetTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@deloitte.com",
            username="admin",
            password="password",
            role="ADMIN",
        )
        self.project_manager = User.objects.create_user(
            email="project_manager@deloitte.com",
            username="project_manager",
            password="password",
            role=PROJECT_MANAGER,
        )
        self.tech_lead = User.objects.create_user(
            email="tech_lead@deloitte.com",
            username="tech_lead",
            password="password",
            role=TECH_LEAD,
        )
        self.developer = User.objects.create_user(
            email="developer@deloitte.com",
            username="developer",
            password="password",
            role=DEVELOPER,
        )
        self.client_user = User.objects.create_user(
            email="client@deloitte.com",
            username="client",
            password="password",
            role=CLIENT,
        )

        self.project1 = Project.objects.create(
            name="PM_Project", description="desc", created_by=self.project_manager
        )
        self.project1.members.add(self.developer, self.tech_lead)

        self.project2 = Project.objects.create(
            name="TL_Project", description="desc", created_by=self.tech_lead
        )
        self.project2.members.add(
            self.developer, self.client_user, self.project_manager
        )
        self.project3 = Project.objects.create(
            name="Admin_Project", description="desc", created_by=self.admin
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_admin_can_list_all_projects(self):
        self.authenticate(self.admin)
        url = reverse("project-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project_names = [project["name"] for project in response.data]
        self.assertIn(self.project1.name, project_names)
        self.assertIn(self.project2.name, project_names)

    def test_project_manager_can_list_their_projects(self):
        self.authenticate(self.project_manager)
        url = reverse("project-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project_names = [project["name"] for project in response.data]
        self.assertIn(self.project1.name, project_names)
        self.assertIn(self.project2.name, project_names)
        self.assertNotIn(self.project3.name, project_names)

    def test_tech_lead_lists_projects_they_are_member_of(self):
        self.authenticate(self.tech_lead)
        url = reverse("project-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        project_names = [project["name"] for project in response.data]
        self.assertIn(self.project1.name, project_names)
        self.assertNotIn(self.project2.name, project_names)

    def test_developer_lists_projects_they_are_member_of(self):
        self.authenticate(self.developer)
        url = reverse("project-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        project_names = [project["name"] for project in response.data]
        self.assertIn(self.project1.name, project_names)
        self.assertNotIn(self.project3.name, project_names)

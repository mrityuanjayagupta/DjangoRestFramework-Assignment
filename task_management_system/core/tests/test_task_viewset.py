from django.urls import reverse
from django.db.models import Q
from rest_framework.test import APITestCase
from rest_framework import status

from ..models import Task, User, Project
from ..constants import ADMIN, PROJECT_MANAGER, DEVELOPER, TECH_LEAD, CLIENT


class TaskViewSetTestCase(APITestCase):
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
        self.other_developer = User.objects.create_user(
            email="developer2@deloitte.com",
            username="developer2",
            password="password",
            role=DEVELOPER,
        )

        self.project1 = Project.objects.create(
            name="PM_Project", description="desc", created_by=self.project_manager
        )
        self.project1.members.add(self.developer, self.tech_lead)

        self.project2 = Project.objects.create(
            name="TL_Project", description="desc", created_by=self.tech_lead
        )
        self.project2.members.add(self.client_user)

        self.task1 = Task.objects.create(
            title="Task 1",
            description="Task 1 desc",
            created_by=self.project_manager,
            project_id=self.project1,
            assigned_to=self.tech_lead,
            status="OPEN",
            priority="HIGH",
        )

        self.task2 = Task.objects.create(
            title="Task 2",
            description="Task 2 desc",
            created_by=self.tech_lead,
            project_id=self.project2,
            assigned_to=self.client_user,
            status="OPEN",
            priority="LOW",
        )

        self.task3 = Task.objects.create(
            title="Task 3",
            description="Task 3 desc",
            created_by=self.other_developer,
            project_id=self.project2,
            assigned_to=self.other_developer,
            status="OPEN",
            priority="MEDIUM",
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_admin_can_list_all_tasks(self):
        self.authenticate(self.admin)
        url = reverse("task-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task_titles = [task["title"] for task in response.data]
        self.assertIn(self.task1.title, task_titles)
        self.assertIn(self.task2.title, task_titles)
        self.assertIn(self.task3.title, task_titles)

    def test_project_manager_can_list_tasks_in_their_projects(self):
        self.authenticate(self.project_manager)
        url = reverse("task-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task_titles = [task["title"] for task in response.data]
        self.assertIn(self.task1.title, task_titles)
        self.assertNotIn(self.task2.title, task_titles)
        self.assertNotIn(self.task3.title, task_titles)

    def test_tech_lead_can_list_tasks_assigned_or_created(self):
        self.authenticate(self.tech_lead)
        url = reverse("task-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task_titles = [task["title"] for task in response.data]
        self.assertIn(self.task1.title, task_titles)
        self.assertIn(self.task2.title, task_titles)
        self.assertNotIn(self.task3.title, task_titles)

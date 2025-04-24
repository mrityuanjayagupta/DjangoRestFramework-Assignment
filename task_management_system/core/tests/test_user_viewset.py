from django.urls import reverse
from django.db.models import Q
from rest_framework.test import APITestCase
from rest_framework import status

from ..models import User, Project
from ..constants import ADMIN, PROJECT_MANAGER, DEVELOPER, TECH_LEAD, CLIENT


class UserViewSetTestCase(APITestCase):
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
            role=DEVELOPER
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

    def authenticate(self, as_user):
        self.client.force_authenticate(user=as_user)

    def test_admin_can_list_all_users(self):
        self.authenticate(self.admin)
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = set([u["id"] for u in response.data])
        all_ids = set(User.objects.values_list("id", flat=True))
        self.assertEqual(returned_ids, all_ids)

    def test_project_manager_can_list_project_members(self):
        self.authenticate(self.project_manager)
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        projects = Project.objects.filter(
            Q(created_by=self.project_manager) | Q(members=self.project_manager)
        ).distinct()
        allowed_ids = set(
            User.objects.filter(
                Q(project_members__in=projects) | Q(projects__in=projects)
            ).values_list("id", flat=True)
        )
        returned_ids = set([u["id"] for u in response.data])
        self.assertEqual(returned_ids, allowed_ids)

    def test_developer_cannot_list_users(self):
        self.authenticate(self.developer)
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Permission denied for user.')

    def test_admin_can_retrieve_any_user(self):
        self.authenticate(self.admin)
        url = reverse("user-detail", kwargs={"pk": self.developer.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.developer.id)

    def test_project_manager_can_retrieve_self(self):
        self.authenticate(self.project_manager)
        url = reverse("user-detail", kwargs={"pk": self.project_manager.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.project_manager.id)

    def test_project_manager_can_retrieve_user_in_their_project(self):
        self.authenticate(self.project_manager)
        url = reverse("user-detail", kwargs={"pk": self.developer.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.developer.id)

    def test_project_manager_cannot_retrieve_user_not_in_their_project(self):
        self.authenticate(self.project_manager)
        url = reverse("user-detail", kwargs={"pk": self.other_developer.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_developer_can_retrieve_self(self):
        self.authenticate(self.developer)
        url = reverse("user-detail", kwargs={"pk": self.developer.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.developer.id)
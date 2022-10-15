from datetime import datetime, timedelta, timezone

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from events.tests.factories import IssueFactory, ProjectFactory


class IssueListTests(TestCase):
    def setUp(self):
        super(IssueListTests, self).setUp()
        self.username = "admin"
        self.password = "admin"

        user = User.objects.create_user(
            username=self.username, password=self.password
        )
        user.save()

        self.client = Client()
        response = self.client.post(
            reverse("login"),
            {"username": self.username, "password": self.password},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_list_issues_when_there_are_no_issues(self):
        response = self.client.get(reverse("issue-list"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["object_list"], [])
        self.assertFalse(response.context["page_obj"].has_previous())
        self.assertFalse(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertTemplateUsed("web/issues/list.html")

    def test_list_issues(self):
        issue_1 = IssueFactory(project=ProjectFactory())
        issue_2 = IssueFactory(project=ProjectFactory())

        response = self.client.get(reverse("issue-list"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["object_list"], [issue_2, issue_1]
        )
        self.assertFalse(response.context["page_obj"].has_previous())
        self.assertFalse(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertTemplateUsed("web/issues/list.html")

    def test_list_issues_does_not_show_resolved_issues(self):
        IssueFactory(
            resolved=True,
            resolved_at=datetime.utcnow().replace(tzinfo=timezone.utc),
        )
        issue = IssueFactory()

        response = self.client.get(reverse("issue-list"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["object_list"], [issue])
        self.assertFalse(response.context["page_obj"].has_previous())
        self.assertFalse(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertTemplateUsed("web/issue/list.html")

    def test_list_issue_pagination(self):
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)

        issues = [
            IssueFactory(last_seen_at=current_time - timedelta(seconds=i))
            for i in range(30)
        ]

        response = self.client.get(reverse("issue-list"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["object_list"], issues[0:10])
        self.assertFalse(response.context["page_obj"].has_previous())
        self.assertTrue(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertTemplateUsed("web/issues/list.html")

        response = self.client.get(reverse("issue-list"), {"page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["object_list"], issues[10:20]
        )
        self.assertTrue(response.context["page_obj"].has_previous())
        self.assertTrue(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertTemplateUsed("web/issues/list.html")

        response = self.client.get(reverse("issue-list"), {"page": 3})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["object_list"], issues[20:30]
        )
        self.assertTrue(response.context["page_obj"].has_previous())
        self.assertFalse(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].number, 3)
        self.assertTemplateUsed("web/issues/list.html")

    def test_list_issue_pagination_with_invalid_page_number(self):
        IssueFactory()

        response = self.client.get(reverse("issue-list"), {"page": 10000})

        self.assertEqual(response.status_code, 404)
        self.assertNotIn("object_list", response.context)
        self.assertNotIn("page_obj", response.context)
        self.assertTemplateNotUsed("web/issue/list.html")

    def test_list_issues_filter_using_project(self):
        project_1 = ProjectFactory()
        issue_1 = IssueFactory(project=project_1)
        IssueFactory(project=ProjectFactory())

        response = self.client.get(
            reverse("issue-list"), {"project": project_1.id}
        )

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["object_list"], [issue_1])
        self.assertFalse(response.context["page_obj"].has_previous())
        self.assertFalse(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertTemplateUsed("web/issues/list.html")

    def test_list_issues_filter_using_project_that_does_not_exist(self):
        IssueFactory(project=ProjectFactory())
        IssueFactory(project=ProjectFactory())

        response = self.client.get(reverse("issue-list"), {"project": 1000})

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["object_list"], [])
        self.assertFalse(response.context["page_obj"].has_previous())
        self.assertFalse(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertTemplateUsed("web/issues/list.html")

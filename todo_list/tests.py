from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Task


class RootRedirectTests(TestCase):
    def test_root_redirects_to_home(self):
        response = self.client.get('/')
        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)


class RegisterViewTests(TestCase):
    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'strongpass123',
            'password_confirm': 'strongpass123',
        })
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertIn('_auth_user_id', self.client.session)

    def test_register_rejects_mismatched_passwords(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'password': 'strongpass123',
            'password_confirm': 'differentpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser2').exists())
        self.assertContains(response, 'Passwords do not match')

    def test_register_rejects_invalid_email(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser3',
            'email': 'not-an-email',
            'password': 'strongpass123',
            'password_confirm': 'strongpass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser3').exists())


class LoginLogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pw12345')

    def test_login_success_redirects_home(self):
        response = self.client.post(reverse('login'), {
            'username': 'alice',
            'password': 'pw12345',
        })
        self.assertRedirects(response, reverse('home'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_failure_does_not_authenticate(self):
        response = self.client.post(reverse('login'), {
            'username': 'alice',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_clears_session(self):
        self.client.login(username='alice', password='pw12345')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)


class HomeViewAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bob', password='pw12345')

    def test_home_requires_login(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_home_accessible_when_logged_in(self):
        self.client.login(username='bob', password='pw12345')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


class TaskCRUDTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='carol', password='pw12345')
        self.other_user = User.objects.create_user(username='dave', password='pw12345')
        self.client.login(username='carol', password='pw12345')

    def test_add_task_creates_task_for_logged_in_user(self):
        response = self.client.post(reverse('add_task'), {
            'title': 'Buy milk',
            'due_date': '',
        })
        self.assertRedirects(response, reverse('home'))
        task = Task.objects.get(title='Buy milk')
        self.assertEqual(task.user, self.user)
        self.assertFalse(task.completed)
        self.assertFalse(task.important)

    def test_add_task_with_blank_title_shows_errors_without_creating_task(self):
        response = self.client.post(reverse('add_task'), {
            'title': '',
            'due_date': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), 0)
        self.assertContains(response, 'This field is required')

    def test_toggle_complete_flips_state_and_is_scoped_to_owner(self):
        task = Task.objects.create(user=self.user, title='Task 1')
        response = self.client.get(reverse('toggle_complete', args=[task.id]))
        self.assertRedirects(response, reverse('home'))
        task.refresh_from_db()
        self.assertTrue(task.completed)

        response = self.client.get(reverse('toggle_complete', args=[task.id]))
        task.refresh_from_db()
        self.assertFalse(task.completed)

    def test_toggle_important_flips_state(self):
        task = Task.objects.create(user=self.user, title='Task 1')
        self.client.get(reverse('toggle_important', args=[task.id]))
        task.refresh_from_db()
        self.assertTrue(task.important)

    def test_toggle_complete_on_other_users_task_returns_404(self):
        other_task = Task.objects.create(user=self.other_user, title='Not yours')
        response = self.client.get(reverse('toggle_complete', args=[other_task.id]))
        self.assertEqual(response.status_code, 404)
        other_task.refresh_from_db()
        self.assertFalse(other_task.completed)

    def test_edit_task_updates_fields(self):
        task = Task.objects.create(user=self.user, title='Old title')
        response = self.client.post(reverse('edit_task', args=[task.id]), {
            'title': 'New title',
            'important': 'on',
            'due_date': '2026-08-01',
        })
        self.assertRedirects(response, reverse('home'))
        task.refresh_from_db()
        self.assertEqual(task.title, 'New title')
        self.assertTrue(task.important)
        self.assertEqual(str(task.due_date), '2026-08-01')

    def test_edit_task_on_other_users_task_returns_404(self):
        other_task = Task.objects.create(user=self.other_user, title='Not yours')
        response = self.client.post(reverse('edit_task', args=[other_task.id]), {
            'title': 'Hacked title',
        })
        self.assertEqual(response.status_code, 404)
        other_task.refresh_from_db()
        self.assertEqual(other_task.title, 'Not yours')

    def test_delete_task_removes_it(self):
        task = Task.objects.create(user=self.user, title='Delete me')
        response = self.client.post(reverse('delete_task', args=[task.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_delete_task_on_other_users_task_returns_404(self):
        other_task = Task.objects.create(user=self.other_user, title='Not yours')
        response = self.client.post(reverse('delete_task', args=[other_task.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Task.objects.filter(id=other_task.id).exists())


class HomeDashboardContentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='erin', password='pw12345')
        self.client.login(username='erin', password='pw12345')

    def test_tasks_are_split_into_correct_sections(self):
        active = Task.objects.create(user=self.user, title='Active task')
        important = Task.objects.create(user=self.user, title='Important task', important=True)
        completed = Task.objects.create(user=self.user, title='Completed task', completed=True)

        response = self.client.get(reverse('home'))

        self.assertContains(response, 'Active task')
        self.assertContains(response, 'Important task')
        self.assertContains(response, 'Completed task')

        self.assertIn(active, response.context['active_tasks'])
        self.assertIn(important, response.context['important_tasks'])
        self.assertIn(completed, response.context['completed_tasks'])
        self.assertNotIn(active, response.context['important_tasks'])
        self.assertNotIn(active, response.context['completed_tasks'])

    def test_active_tasks_ordered_by_soonest_due_date_first_then_no_date_last(self):
        today = timezone.localdate()
        no_date = Task.objects.create(user=self.user, title='No date')
        later = Task.objects.create(user=self.user, title='Later', due_date=today + timedelta(days=5))
        soonest = Task.objects.create(user=self.user, title='Soonest', due_date=today + timedelta(days=1))

        response = self.client.get(reverse('home'))
        ordered_titles = [task.title for task in response.context['active_tasks']]

        self.assertEqual(ordered_titles, ['Soonest', 'Later', 'No date'])

    def test_overdue_task_is_flagged_in_rendered_page(self):
        today = timezone.localdate()
        Task.objects.create(user=self.user, title='Overdue task', due_date=today - timedelta(days=1))

        response = self.client.get(reverse('home'))
        self.assertContains(response, 'overdue')

    def test_tasks_from_other_users_not_shown(self):
        other_user = User.objects.create_user(username='frank', password='pw12345')
        Task.objects.create(user=other_user, title='Not my task')

        response = self.client.get(reverse('home'))
        self.assertNotContains(response, 'Not my task')


class StaticAssetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='grace', password='pw12345')
        self.client.login(username='grace', password='pw12345')

    def test_home_references_stylesheet_and_script(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'styles/styles.css')
        self.assertContains(response, 'js/script.js')

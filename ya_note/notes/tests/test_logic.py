from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug',
            author=cls.author
        )

    def test_anonymous_user_cant_create_note(self):
        notes_count = Note.objects.count()
        url = reverse('notes:add')
        response = self.client.post(
            url,
            data={
                'title': 'Новый заголовок',
                'text': 'Новый текст',
                'slug': 'new-slug'
            }
        )
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_user_can_create_note(self):
        notes_count = Note.objects.count()
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(
            url,
            data={
                'title': 'Новый заголовок',
                'text': 'Новый текст',
                'slug': 'new-slug'
            }
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), notes_count + 1)

    def test_cant_create_duplicate_slug(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(
            url,
            data={
                'title': 'Новый заголовок',
                'text': 'Новый текст',
                'slug': self.note.slug
            }
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            f'{self.note.slug} - такой slug уже существует, '
            'придумайте уникальное значение!'
        )

    def test_empty_slug(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        title = 'Новый заголовок'
        response = self.client.post(
            url,
            data={
                'title': title,
                'text': 'Новый текст',
                'slug': ''
            }
        )
        self.assertRedirects(response, reverse('notes:success'))
        new_note = Note.objects.get(title=title)
        expected_slug = slugify(title)
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        new_title = 'Обновленный заголовок'
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(
            url,
            data={
                'title': new_title,
                'text': self.note.text,
                'slug': self.note.slug
            }
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, new_title)

    def test_other_user_cant_edit_note(self):
        new_title = 'Обновленный заголовок'
        self.client.force_login(self.reader)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(
            url,
            data={
                'title': new_title,
                'text': self.note.text,
                'slug': self.note.slug
            }
        )
        self.assertEqual(response.status_code, 404)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, new_title)

    def test_author_can_delete_note(self):
        notes_count = Note.objects.count()
        self.client.force_login(self.author)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), notes_count - 1)

    def test_other_user_cant_delete_note(self):
        notes_count = Note.objects.count()
        self.client.force_login(self.reader)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Note.objects.count(), notes_count)

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.user = User.objects.create(username='Noname')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст',
            slug='slug',
            author=cls.author
        )
        cls.url = reverse('notes:add')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Заметка',
            'text': 'Текст',
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_authorized_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

    def test_empty_slug_forms_from_title(self):
        self.auth_client.post(self.url, self.form_data)
        new_note = Note.objects.get(slug=slugify(self.form_data['title']))
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))

    def test_note_slug_cant_repeate(self):
        start_notes_count = Note.objects.count()
        self.form_data['slug'] = 'slug',
        response = self.auth_client.post(self.url, self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING),
        )
        final_notes_count = Note.objects.count()
        self.assertEqual(start_notes_count, final_notes_count)


class TestNoteEditDelete(TestCase):
    NEW_NOTE_TEXT = 'Измененный текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.user = User.objects.create(username='Noname')
        cls.author_note = Note.objects.create(
            title='Заметка',
            text='Текст',
            slug='slug',
            author=cls.author
        )
        cls.form_data = {
            'title': 'Заметка',
            'text': cls.NEW_NOTE_TEXT,
        }
        cls.edit_url = ('notes:edit', (cls.author_note.slug,))
        cls.delete_url = ('notes:delete', (cls.author_note.slug,))
        cls.success_url = reverse('notes:success')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

    def test_author_can_edit_note(self):
        name, args = self.edit_url
        url = reverse(name, args=args)
        response = self.author_client.post(
            url,
            data=self.form_data
        )
        self.assertRedirects(response, self.success_url)
        self.author_note.refresh_from_db()
        self.assertEqual(self.author_note.text, self.NEW_NOTE_TEXT)

    def test_author_can_delete_note(self):
        name, args = self.delete_url
        url = reverse(name, args=args)
        response = self.author_client.delete(url)
        self.assertRedirects(response, self.success_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def user_cant_delete_anothers_note(self):
        start_notes_count = Note.objects.count()
        name, args = self.delete_url
        url = reverse(name, args=args)
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        final_notes_count = Note.objects.count()
        self.assertEqual(start_notes_count, final_notes_count)

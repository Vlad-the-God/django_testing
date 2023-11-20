from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор Заметки')
        cls.user = User.objects.create(username='Просто Юзер')
        cls.note_author = Note.objects.create(
            title='Заметка_1',
            text='Текст',
            author=cls.author,
        )
        cls.note_user = Note.objects.create(
            title='Заметка_2',
            text='Текст',
            author=cls.user,
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.list_url = reverse('notes:list')

    def test_authorized_client_has_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note_author.slug,)),
        )
        for url, args in urls:
            with self.subTest(url=url, args=args):
                url_with_form = reverse(url, args=args)
                response = self.author_client.get(url_with_form)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_add_note_to_note_list(self):
        response = self.author_client.get(self.list_url)
        self.assertIn(self.note_author, response.context['object_list'])

    def test_author_can_see_only_his_own_notes(self):
        response = self.author_client.get(self.list_url)
        self.assertContains(response, self.note_author.title)
        self.assertNotContains(response, self.note_user.title)
        user_note = Note.objects.filter(author=self.user)
        self.assertNotIn(user_note, response.context['object_list'])

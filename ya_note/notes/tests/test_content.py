from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.list_url = reverse('notes:list')

#    def test_anonymous_client_has_no_note_list(self):
#        response = self.client.get(self.list_url)
#        self.assertEqual([], response.context['object_list'])

#    def test_anonymous_client_has_no_form(self):
#        response = self.client.get(self.add_url)
#        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)

    def test_add_note_to_note_list(self):
        self.author_client.force_login(self.author)
        response = self.author_client.get(self.list_url)
        self.assertIn(self.note_author, response.context['object_list'])

    def test_author_can_see_only_his_own_notes(self):
        self.author_client.force_login(self.author)
        response = self.author_client.get(self.list_url)
        self.assertContains(response, self.note_author.title)
        self.assertNotContains(response, self.note_user.title)

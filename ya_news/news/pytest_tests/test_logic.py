import pytest

from http import HTTPStatus

from pytest_django.asserts import assertFormError, assertRedirects

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, news_id, comment_form_data
):
    url = reverse('news:detail', args=(news_id))
    client.post(url, data=comment_form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_authorized_user_can_create_comment(
    author_client, news_id, comment_form_data
):
    url = reverse('news:detail', args=(news_id))
    response = author_client.post(url, data=comment_form_data)
    assertRedirects(response, f'{url}#comments')
    comment_count = Comment.objects.count()
    assert comment_count == 1
    comment = Comment.objects.get()
    assert comment.text == comment_form_data['text']


@pytest.mark.django_db
def test_user_cant_use_bad_words(news_url, comment_form_data, author_client):
    comment_form_data['text'] = BAD_WORDS[0]
    response = author_client.post(news_url, data=comment_form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)


def test_author_can_delete_comment(
    author_client, authors_comment_id, news_url
):
    delete_url = reverse('news:delete', args=(authors_comment_id,))
    response = author_client.delete(delete_url)
    assertRedirects(response, (news_url + '#comments'))
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(
    author_client, authors_comment_id,
    comment_form_data, news_url, authors_comment
):
    edit_url = reverse('news:edit', args=(authors_comment_id,))
    response = author_client.post(edit_url, data=comment_form_data)
    assertRedirects(response, (news_url + '#comments'))
    authors_comment.refresh_from_db()
    assert authors_comment.text == comment_form_data['text']


def test_user_cant_delete_comment_of_another_user(
    admin_client, authors_comment_id
):
    delete_url = reverse('news:delete', args=(authors_comment_id,))
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_user_cant_edit_comment_of_another_user(
    admin_client, authors_comment, authors_comment_id, comment_form_data
):
    edit_url = reverse('news:edit', args=(authors_comment_id,))
    response = admin_client.post(edit_url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    authors_comment.refresh_from_db()
    assert authors_comment.text != comment_form_data['text']

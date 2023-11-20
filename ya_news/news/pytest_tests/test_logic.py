from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, news_url, comment_form_data
):
    comments_count_start = Comment.objects.count()
    client.post(news_url, data=comment_form_data)
    comments_count_final = Comment.objects.count()
    assert comments_count_start == comments_count_final


@pytest.mark.django_db
def test_authorized_user_can_create_comment(
    author_client, news, author, news_url, comment_form_data
):
    comment_count_start = Comment.objects.count()
    response = author_client.post(news_url, data=comment_form_data)
    assertRedirects(response, f'{news_url}#comments')
    comment_count_final = Comment.objects.count()
    assert comment_count_final == comment_count_start + 1
    comment = Comment.objects.last()
    assert comment.text == comment_form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(news_url, comment_form_data, author_client):
    comment_form_data['text'] = BAD_WORDS[0]
    response = author_client.post(news_url, data=comment_form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)


def test_author_can_delete_comment(
    author_client, delete_comment_url, news_url
):
    comment_count_start = Comment.objects.count()
    response = author_client.delete(delete_comment_url)
    assertRedirects(response, (news_url + '#comments'))
    comments_count_final = Comment.objects.count()
    assert comments_count_final == comment_count_start - 1


def test_author_can_edit_comment(
    author, author_client, edit_comment_url,
    comment_form_data, news, news_url, authors_comment
):
    response = author_client.post(edit_comment_url, data=comment_form_data)
    assertRedirects(response, (news_url + '#comments'))
    authors_comment.refresh_from_db()
    assert authors_comment.text == comment_form_data['text']
    assert authors_comment.news == news
    assert authors_comment.author == author


def test_user_cant_delete_comment_of_another_user(
    admin_client, delete_comment_url
):
    response = admin_client.delete(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_user_cant_edit_comment_of_another_user(
    admin_client, authors_comment, edit_comment_url, comment_form_data
):
    original_comment = authors_comment
    response = admin_client.post(edit_comment_url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    authors_comment.refresh_from_db()
    final_comment = authors_comment
    assert original_comment.text == final_comment.text
    assert original_comment.news == final_comment.news
    assert original_comment.author == final_comment.author

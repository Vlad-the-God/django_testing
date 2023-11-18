import pytest

from http import HTTPStatus

from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_pages_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url',
    ('news:edit', 'news:delete'),
)
def test_availability_for_comment_edit_and_delete_author(
    author_client, authors_comment_id, url
):
    url = reverse(url, args=(authors_comment_id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url',
    ('news:edit', 'news:delete'),
)
def test_availability_for_comment_edit_and_delete_user(
    admin_client, authors_comment_id, url
):
    url = reverse(url, args=(authors_comment_id,))
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    ('news:edit', 'news:delete'),
)
def test_redirects(client, url, authors_comment_id):
    login_url = reverse('users:login')
    page_url = reverse(url, args=(authors_comment_id,))
    expected_url = f'{login_url}?next={page_url}'
    response = client.get(page_url)
    assertRedirects(response, expected_url)

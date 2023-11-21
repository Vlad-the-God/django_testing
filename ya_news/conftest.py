from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def news_id(news):
    return news.id,


@pytest.fixture
def news_url(news, news_id):
    return reverse('news:detail', args=(news_id))


@pytest.fixture
def authors_comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст'
    )
    return comment


@pytest.fixture
def authors_comment_id(authors_comment):
    return authors_comment.id


@pytest.fixture
def news_11():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def few_comments(news, author):
    now = timezone.now()
    for index in range(6):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def comment_form_data():
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def delete_comment_url(authors_comment_id):
    return reverse('news:delete', args=(authors_comment_id,))


@pytest.fixture
def edit_comment_url(authors_comment_id):
    return reverse('news:edit', args=(authors_comment_id,))

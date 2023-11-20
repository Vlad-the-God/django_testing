import pytest

from django.conf import settings

from news.forms import CommentForm
from news.pytest_tests.constants import HOMEPAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('news_11')
def test_news_count(client):
    response = client.get(HOMEPAGE)
    news_list = response.context['object_list']
    news_count = len(news_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('news_11')
def test_news_order(client):
    response = client.get(HOMEPAGE)
    news_list = response.context['object_list']
    all_dates = [news.date for news in news_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.usefixtures('news', 'few_comments')
def test_comments_order(client, news_url):
    response = client.get(news_url)
    one_news = response.context['news']
    comments = one_news.comment_set.all()
    all_comments = [comment.created for comment in comments]
    sorted_comments = sorted(all_comments)
    assert all_comments == sorted_comments


@pytest.mark.django_db
@pytest.mark.usefixtures('news')
def test_authorized_user_has_comment_form(admin_client, news_url):
    response = admin_client.get(news_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
@pytest.mark.usefixtures('news')
def test_anonymous_user_has_no_comment_form(client, news_url):
    response = client.get(news_url)
    assert 'form' not in response.context

import pytest

from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.usefixtures('news_11')
def test_news_count(client):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('news_11')
def test_news_order(client):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.usefixtures('news', 'few_comments')
def test_comments_order(client, news_id):
    response = client.get(reverse('news:detail', args=(news_id)))
    one_news = response.context['news']
    all_comments = one_news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.usefixtures('news')
def test_authorized_user_has_comment_form(admin_client, news_id):
    url = reverse('news:detail', args=(news_id))
    response = admin_client.get(url)
    assert 'form' in response.context


@pytest.mark.django_db
@pytest.mark.usefixtures('news')
def test_anonymous_user_has_no_comment_form(client, news_id):
    url = reverse('news:detail', args=(news_id))
    response = client.get(url)
    assert 'form' not in response.context

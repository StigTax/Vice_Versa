import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_index_news_limit(client, news_list):
    """Проверяем, что на главной странице отображается не более 10 новостей."""
    response = client.get(reverse('news:home'))
    news_from_context = response.context['news_feed']
    assert len(news_from_context) == 10


@pytest.mark.django_db
def test_news_order(client, news_list):
    response = client.get(reverse('news:home'))
    dates = [news.date for news in response.context['news_feed']]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(client, news, comment_list):
    response = client.get(reverse('news:detail', args=[news.id]))
    news_obj = response.context['object']
    assert news_obj.comment_set.count() == 5


@pytest.mark.django_db
@pytest.mark.parametrize(
    'is_authenticated, expected_form',
    [
        (False, False),
        (True, True),
    ]
)
def test_comment_form_visibility(
    client,
    news,
    author,
    is_authenticated,
    expected_form
):
    """Форма комментария доступна только авторизованному пользователю"""
    if is_authenticated:
        client.force_login(author)

    response = client.get(reverse('news:detail', args=[news.id]))

    if expected_form:
        assert 'form' in response.context
    else:
        assert 'form' not in response.context

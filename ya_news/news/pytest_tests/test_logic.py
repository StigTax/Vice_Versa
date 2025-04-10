import pytest
from http import HTTPStatus
from django.urls import reverse
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_cannot_post_comment(client, news):
    initial_count = Comment.objects.count()
    url = reverse('news:detail', args=[news.id])
    response = client.post(url, data={'text': 'Комментарий'})
    assert response.status_code == HTTPStatus.FOUND
    assert reverse('users:login') in response.url
    assert Comment.objects.count() == initial_count


@pytest.mark.django_db
def test_authorized_can_post_comment(client, author, news):
    initial_count = Comment.objects.count()
    client.force_login(author)
    url = reverse('news:detail', args=[news.id])
    response = client.post(
        url,
        data={'text': 'Комментарий'},
        follow=True
    )
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == initial_count + 1
    new_comment = Comment.objects.last()
    assert new_comment.text == 'Комментарий'
    assert new_comment.author == author
    assert new_comment.news == news
    assert response.redirect_chain[-1][0] == url + '#comments'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'text, should_create, expected_status',
    [
        ('нормальный комментарий', True, HTTPStatus.FOUND),
        ('редиска', False, HTTPStatus.OK),
        ('Негодяй!', False, HTTPStatus.OK),
    ]
)
def test_comment_creation(
    client,
    author,
    news,
    text,
    should_create,
    expected_status
):
    client.force_login(author)
    initial_count = Comment.objects.count()

    response = client.post(
        reverse('news:detail', args=[news.id]),
        data={'text': text},
        follow=False
    )
    assert response.status_code == expected_status
    assert Comment.objects.count() == initial_count + (
        1 if should_create else 0
    )
    if expected_status == HTTPStatus.OK:
        assert 'form' in response.context
        assert 'text' in response.context['form'].errors


@pytest.mark.django_db
def test_author_can_edit_comment(client, author, comment):
    client.force_login(author)
    new_text = 'Обновлённый комментарий'
    url = reverse('news:edit', args=[comment.id])
    response = client.post(url, data={'text': new_text}, follow=True)
    assert response.status_code == HTTPStatus.OK
    comment.refresh_from_db()
    assert comment.text == new_text
    assert response.redirect_chain[-1][0] == reverse(
        'news:detail', args=[comment.news.id]
    ) + '#comments'


@pytest.mark.django_db
def test_author_can_delete_comment(client, author, comment):
    comment_id = comment.id
    client.force_login(author)
    url = reverse('news:delete', args=[comment.id])
    response = client.post(url, follow=True)
    assert response.status_code == HTTPStatus.OK
    assert not Comment.objects.filter(id=comment_id).exists()
    assert response.redirect_chain[-1][0] == reverse(
        'news:detail', args=[comment.news.id]
    ) + '#comments'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'view_name',
    ['news:edit', 'news:delete'],
    ids=['edit', 'delete']
)
def test_user_cannot_edit_delete_foreign_comment(
    client, user, comment, view_name
):
    original_text = comment.text
    client.force_login(user)
    url = reverse(view_name, args=[comment.id])
    response = client.post(url, data={'text': 'Хакерство'})
    assert response.status_code in [HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND]
    comment.refresh_from_db()
    assert comment.text == original_text

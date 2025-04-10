import pytest
from http import HTTPStatus

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home',)
)
def test_index_available_for_anonymous(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_available_for_anonymous(client, news):
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, method, expected_status',
    [
        ('news:edit', 'get', HTTPStatus.OK),
        ('news:delete', 'get', HTTPStatus.OK),
        ('news:edit', 'post', HTTPStatus.FOUND),
        ('news:delete', 'post', HTTPStatus.FOUND),
    ],
    ids=[
        'edit_get',
        'delete_get',
        'edit_post',
        'delete_post',
    ]
)
def test_edit_delete_available_for_author(
    client, comment, author, name, method, expected_status
):
    client.force_login(author)
    url = reverse(name, args=[comment.id])
    if method == 'get':
        response = client.get(url)
    else:
        response = client.post(url, data={'text': 'Updated text'})
    assert response.status_code == expected_status
    if method == 'post' and expected_status == HTTPStatus.FOUND:
        assert response.url == reverse(
            'news:detail', args=[comment.news.id]
        ) + '#comments'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, method',
    [
        ('news:edit', 'get'),
        ('news:delete', 'get'),
    ]
)
def test_edit_delete_redirect_for_anonymous(client, comment, name, method):
    url = reverse(name, args=[comment.id])
    if method == 'get':
        response = client.get(url)
    else:
        response = client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert reverse('users:login') in response.url


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, method',
    [
        ('news:edit', 'get'),
        ('news:delete', 'get'),
        ('news:edit', 'post'),
        ('news:delete', 'post'),
    ]
)
def test_edit_delete_404_for_not_author(client, user, comment, name, method):
    client.force_login(user)
    url = reverse(name, args=[comment.id])
    if method == 'get':
        response = client.get(url)
    else:
        response = client.post(url, data={'text': 'Updated text'})
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    [
        'users:signup',
        'users:login',
        'users:logout'
    ]
)
def test_auth_pages_accessible_for_anonymous(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

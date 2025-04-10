import pytest
from django.contrib.auth.models import User

from news.models import News, Comment

from django.utils import timezone
from datetime import timedelta


@pytest.fixture
def author(db):
    return User.objects.create_user(
        username='author',
        password='password'
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='user',
        password='password'
    )


@pytest.fixture
def news(db):
    return News.objects.create(
        title='Новость',
        text='Текст',
        date=timezone.now()
    )


@pytest.fixture
def news_list(db):
    now = timezone.now()
    return [
        News.objects.create(
            title=f'Новость {i}',
            text='Текст',
            date=now - timedelta(days=i)
        )
        for i in range(10)
    ]


@pytest.fixture
def comment(db, news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Комментарий'
    )


@pytest.fixture
def comment_list(db, news, author):
    now = timezone.now()
    comments = []
    for i in range(5):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}'
        )
        comment.created_at = now + timedelta(minutes=i)
        comment.save()
        comments.append(comment)
    return comments

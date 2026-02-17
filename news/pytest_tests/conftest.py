from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse

import pytest

from news.models import News, Comment


@pytest.fixture(autouse=True)
def _enable_db_access_for_all_tests(db):
    """Автоматически предоставляет доступ к базе данных для всех тестов."""
    pass


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Олег')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='НеОлег')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст новости',)


@pytest.fixture
def all_news():
    today = datetime.today()
    news_objects = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]

    News.objects.bulk_create(news_objects)
    return News.objects.all()


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news, author=author, text='Текст комментария',
    )

@pytest.fixture
def get_url():
    """Фабрика для получения URL."""
    def _get_url(name, obj=None):
        if obj:
            return reverse(name, args=(obj.id,))
        return reverse(name)
    return _get_url


@pytest.fixture
def home_url(get_url):
    """URL главной страницы."""
    return get_url('news:home')


@pytest.fixture
def login_url(get_url):
    """URL страницы входа."""
    return get_url('users:login')


@pytest.fixture
def logout_url(get_url):
    """URL страницы выхода."""
    return get_url('users:logout')


@pytest.fixture
def signup_url(get_url):
    """URL страницы регистрации."""
    return get_url('users:signup')


@pytest.fixture
def detail_url(news, get_url):
    """URL детальной страницы новости."""
    return get_url('news:detail', news)


@pytest.fixture
def edit_url(comment, get_url):
    """URL редактирования комментария."""
    return get_url('news:edit', comment)


@pytest.fixture
def delete_url(comment, get_url):
    """URL удаления комментария."""
    return get_url('news:delete', comment)

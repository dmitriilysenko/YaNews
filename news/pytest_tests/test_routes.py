from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf
import pytest

PUBLIC_PAGES = [
    'news:home',
    'users:login',
    'users:signup',
    'users:logout',
]

COMMENT_PAGES = ['news:edit', 'news:delete']


def test_anonymous_user_access(client, get_url, news):
    for name in PUBLIC_PAGES:
        url = get_url(name)
        response = (
            client.post(url)
            if name == 'users:logout'
            else client.get(url)
        )
        assert response.status_code == HTTPStatus.OK
    detail_url = get_url('news:detail', news)
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('name', COMMENT_PAGES)
@pytest.mark.parametrize(
    'client_type, expected_status',
    [
        (lf('client'), HTTPStatus.FOUND),
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK),
    ]
)
def test_comment_pages_access(
    client_type, name, expected_status, get_url, comment
):
    url = get_url(name, comment)
    response = client_type.get(url)
    assert response.status_code == expected_status

    if expected_status == HTTPStatus.FOUND:
        login_url = get_url('users:login')
        expected_redirect_url = f'{login_url}?next={url}'
        assertRedirects(response, expected_redirect_url)

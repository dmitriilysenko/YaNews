from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf
import pytest


COMMENT_PAGES = ('news:edit', 'news:delete')


@pytest.mark.parametrize('url_fixture, page_name', [
    (lf('home_url'), 'home'),
    (lf('login_url'), 'login'),
    (lf('signup_url'), 'signup'),
    (lf('detail_url'), 'detail'),
    (lf('logout_url'), 'logout'),
])
def test_anonymous_user_access(client, url_fixture, page_name):

    if page_name == 'logout':
        response = client.post(url_fixture)
    else:
        response = client.get(url_fixture)

    assert response.status_code == HTTPStatus.OK, (
        f'Страница {page_name} недоступна'
    )


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
    client_type, name, expected_status, get_url, comment, login_url
):
    url = get_url(name, comment)
    response = client_type.get(url)
    assert response.status_code == expected_status

    if expected_status == HTTPStatus.FOUND:
        expected_redirect_url = f'{login_url}?next={url}'
        assertRedirects(response, expected_redirect_url)

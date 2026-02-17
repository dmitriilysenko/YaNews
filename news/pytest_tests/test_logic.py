from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError
from pytest_lazyfixture import lazy_fixture as lf
import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

from .assertions import assert_comment_unchanged
from .comments_data import COMMENT_TEXT


def test_user_can_create_comment(
        author_client, author, news, detail_url
):
    existing_ids = list(Comment.objects.values_list('id', flat=True))
    response = author_client.post(detail_url, data=COMMENT_TEXT)
    assertRedirects(response, f'{detail_url}#comments')
    new_comments = Comment.objects.exclude(id__in=existing_ids)
    assert new_comments.count() == 1, (
        f'Должен создаваться 1 комментарий, создано: {new_comments.count()}'
    )
    new_comment = new_comments.get()
    assert new_comment.text == COMMENT_TEXT['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, detail_url, login_url):
    comments_number = Comment.objects.count()
    response = client.post(detail_url, data=COMMENT_TEXT)
    assertRedirects(response, f'{login_url}?next={detail_url}')
    assert Comment.objects.count() == comments_number, (
        'Анонимный пользователь не должен иметь возможность '
        'оставить комментарий'
    )


def test_user_cant_use_bad_words(author_client, detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    form = response.context['form']
    assertFormError(
        form=form,
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
        author_client, detail_url, delete_url):
    comments_number = Comment.objects.count()
    response = author_client.delete(delete_url)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == comments_number - 1, (
        'Количество комментариев после удаления должно уменьшиться на 1'
    )
    assert response.status_code == HTTPStatus.FOUND


def test_author_can_edit_comment(
        author_client, detail_url, edit_url, comment):
    comments_number = Comment.objects.count()
    comment_before = comment
    response = author_client.post(edit_url, data=COMMENT_TEXT)
    assertRedirects(response, f'{detail_url}#comments')
    comment_after = Comment.objects.get(id=comment.id)
    assert Comment.objects.count() == comments_number
    assert comment_after.text == COMMENT_TEXT['text']
    assert comment_after.author == comment_before.author
    assert comment_after.news == comment_before.news
    assert comment_after.created == comment_before.created


@pytest.mark.parametrize('url_fixture, method', [
    (lf('delete_url'), 'delete'),
    (lf('edit_url'), 'post'),
])
def test_user_cant_modify_comment_of_another_user(
    not_author_client, url_fixture, method, comment
):
    comments_number = Comment.objects.count()
    comment_before = comment
    response = not_author_client.delete(url_fixture) if method == 'delete' \
        else not_author_client.post(url_fixture, data=COMMENT_TEXT)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_number
    comment_after = Comment.objects.get(id=comment.id)
    assert_comment_unchanged(comment_before, comment_after)

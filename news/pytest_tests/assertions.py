"""
Модуль с общими проверками (assertions) для тестов.

Содержит функции для проверки неизменности объектов и
других часто используемых утверждений.
"""


def assert_comment_unchanged(comment_before, comment_after):

    assert comment_after.id == comment_before.id
    assert comment_after.text == comment_before.text
    assert comment_after.author == comment_before.author
    assert comment_after.news == comment_before.news
    assert comment_after.created == comment_before.created
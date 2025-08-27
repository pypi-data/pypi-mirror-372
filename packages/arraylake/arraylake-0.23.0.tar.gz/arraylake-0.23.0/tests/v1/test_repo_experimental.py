import time

import pytest

from arraylake import experimental


def test_repo_experimental_search(new_sync_repo):
    assert hasattr(new_sync_repo, "filter_metadata")

    new_sync_repo.root_group.attrs["title"] = "root title"
    baz_group = new_sync_repo.root_group.create_group("foo/bar/baz")
    baz_group.attrs["title"] = "/foo/bar/baz title"
    spam_array = baz_group.create("spam", shape=100, chunks=10, dtype="<f4", fill_value=-1.0)
    spam_array.attrs["description"] = "spam array description"
    unicode_input_dtype = "<U2"
    new_sync_repo.root_group.create("/1/2/3/unicode_array", shape=10, chunks=10, dtype=unicode_input_dtype)

    # expression yields results that are at the group (title) and array (description) level
    expression = "title == '/foo/bar/baz title' || description == 'spam array description'"
    res = new_sync_repo.filter_metadata(expression)
    assert sorted(res) == sorted(["foo/bar/baz/spam", "foo/bar/baz"])

    # bad expr
    with pytest.raises(ValueError, match=r'invalid token: Parse error at column 9, token "10" \(NUMBER\), for expression'):
        expression = "title == 10"
        res = new_sync_repo.filter_metadata(expression)

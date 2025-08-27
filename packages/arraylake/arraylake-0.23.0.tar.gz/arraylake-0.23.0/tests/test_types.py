import uuid

import pytest

# DEPRECATED: V1 types import - pending removal
from arraylake.repos.v1.types import CollectionName
from arraylake.types import Author, NewBucket, Repo, utc_now


def test_collection_name_str_enum_fstring_format() -> None:
    """DEPRECATED: V1 CollectionName test - pending removal.
    V1 repositories are legacy and this test will be removed in a future version."""
    assert f"foo {CollectionName.metadata}" == "foo metadata"
    assert f"foo {CollectionName.chunks}" == "foo chunks"


def test_identities_to_author(test_user, test_api_token):
    user_author: Author = test_user.as_author()
    assert isinstance(user_author, Author)
    assert user_author.email == "abc@earthmover.io"
    assert user_author.name == "TestFirst TestFamily"

    api_author: Author = test_api_token.as_author()
    assert isinstance(api_author, Author)
    assert api_author.email == "svc-email@some-earthmover-org.service.earthmover.io"
    assert not api_author.name


def test_repo_repr():
    now = utc_now()
    user = uuid.uuid4()
    repo = Repo(
        id=b"123",
        org="foo",
        name="bar",
        description="baz",
        created=now,
        created_by=user,
        status=dict(mode="online", initiated_by={"system_id": "x"}),
    )
    assert repr(repo) == f"<Repo foo/bar created at {now} by {user}. Last updated at {now}>"

    repo = Repo(
        id=b"123", org="foo", name="bar", description="baz", created=now, status=dict(mode="online", initiated_by={"system_id": "x"})
    )
    assert repr(repo) == f"<Repo foo/bar created at {now} by None. Last updated at {now}>"


@pytest.mark.parametrize(
    "nickname, platform, prefix, name, extra_config",
    [
        ("foo-bar", "s3", "", "my-bucket-on-s3", {"region_name": "us-east-1"}),
        ("foo_bar", "s3-compatible", "foo", "my_bucket_on_s3", {"endpoint_url": "http://localhost:9000"}),
        ("foo-bar", "s3", "", "my-bucket-on-s3", {"region_name": "us-east-1"}),
        ("foo-bar", "s3", "foo/bar/spam", "my-bucket-on-s3", {"region_name": "us-east-1"}),
    ],
)
def test_bucket_name_validation(nickname, platform, prefix, name, extra_config):
    b = NewBucket(
        nickname=nickname, platform=platform, name=name, prefix=prefix, extra_config=extra_config, auth_config={"method": "anonymous"}
    )
    assert b.nickname == nickname
    assert b.platform == platform
    assert b.name == name
    assert b.prefix == prefix


@pytest.mark.parametrize(
    "nickname, platform, prefix, name, extra_config, err_msg",
    [
        ("fo", "s3", "", "my-bucket-on-s3", {"region_name": "us-east-1"}, "Bucket nickname must be at least 3 characters long."),
        ("foo-bar", "s3", "", "b", {"region_name": "us-east-1"}, "Bucket name must be at least 3 characters long."),
        ("foo-bar", "s3-compatible", "", "my bucket", {"endpoint_url": "http://localhost:9000"}, "Bucket name must not contain spaces."),
        (
            "foo-bar",
            "s3-compatible",
            "",
            "s3://my-arraylake-bucket",
            {"endpoint_url": "http://localhost:9000"},
            "Bucket name must not contain schemes.",
        ),
        ("foo-bar", "s3-compatible", "", "my-arraylake-bucket", {}, "S3-compatible buckets require an endpoint_url"),
        ("foo-bar", "s3", "", "my bucket", {"region_name": "us-east-1"}, "Bucket name must not contain spaces."),
        ("foo-bar", "s3", "/foo/", "my-bucket-on-s3", {"region_name": "us-east-1"}, "Bucket prefix must not start or end with a slash."),
        (
            "foo-bar",
            "s3",
            "/foo/bar/",
            "my-bucket-on-s3",
            {"region_name": "us-east-1"},
            "Bucket prefix must not start or end with a slash.",
        ),
        ("foo-bar", "s3", "foo bar", "my-bucket-on-s3", {"region_name": "us-east-1"}, "Bucket prefix must not contain spaces."),
    ],
)
def test_bucket_name_validation_error(nickname, platform, prefix, name, extra_config, err_msg):
    with pytest.raises(ValueError, match=err_msg):
        b = NewBucket(
            nickname=nickname,
            platform=platform,
            name=name,
            prefix=prefix,
            extra_config=extra_config,
            auth_config={"method": "anonymous"},
        )

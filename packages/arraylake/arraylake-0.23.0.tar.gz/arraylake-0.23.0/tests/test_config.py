import os

import arraylake


def test_config() -> None:
    # DEPRECATED: chunkstore.uri is V1-specific - pending removal
    expected_keys = ["chunkstore.uri", "service.uri"]
    for ek in expected_keys:
        assert arraylake.config.get(ek, "__REQUIRED__") != "__REQUIRED__"


def test_aws_config_path():
    assert os.environ["AWS_ACCESS_KEY_ID"] == "minio123"


def test_config_defaults_set():
    assert "uri" in arraylake.config.defaults[0]["service"]
    assert "ssl" in arraylake.config.defaults[0]["service"]
    assert "verify" in arraylake.config.defaults[0]["service"]["ssl"]
    # DEPRECATED: chunkstore config is V1-specific - pending removal
    assert "hash_method" in arraylake.config.defaults[0]["chunkstore"]
    assert "inline_threshold_bytes" in arraylake.config.defaults[0]["chunkstore"]
    assert "scatter_initial_credentials" in arraylake.config.defaults[0]["icechunk"]

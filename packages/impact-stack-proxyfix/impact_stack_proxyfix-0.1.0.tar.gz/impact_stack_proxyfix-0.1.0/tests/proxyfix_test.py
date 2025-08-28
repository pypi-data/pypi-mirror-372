"""Test the WSGI middlewares."""

from copy import copy
from unittest import mock

import pytest

from impact_stack import proxyfix


def create_config_getter(trusted: list[str]):
    """Create a config getter with a given PROXYFIX_TRUSTED list."""
    config = {"PROXYFIX_TRUSTED": trusted}
    return config.get


def copy_env(env):
    """Create a copy of a WSGI environment with the original values backed up."""
    new_env = copy(env)
    new_env["werkzeug.proxy_fix.orig_http_host"] = env["HTTP_HOST"]
    new_env["werkzeug.proxy_fix.orig_remote_addr"] = env["REMOTE_ADDR"]
    new_env["werkzeug.proxy_fix.orig_wsgi_url_scheme"] = env["wsgi.url_scheme"]
    return new_env


class ProxyFixTest:
    """Test the proxy fix middleware."""

    def test_one_forwarded_for_layer(self):
        """Test a single trusted reverse proxy."""
        fix = proxyfix.ProxyFix.from_config(create_config_getter(["127.0.0.1"]))
        env = {
            "REMOTE_ADDR": "127.0.0.1",
            "HTTP_HOST": "example.com",
            "wsgi.url_scheme": "http",
            "HTTP_X_FORWARDED_FOR": "8.8.8.8",
            "HTTP_X_FORWARDED_PROTO": "https",
        }
        expected_env = copy_env(env)
        expected_env["REMOTE_ADDR"] = "8.8.8.8"
        expected_env["wsgi.url_scheme"] = "https"
        app = mock.Mock()
        fix.wrap(app)(env, mock.Mock())
        assert app.mock_calls == [mock.call(expected_env, mock.ANY)]

    def test_no_trusted_layer(self):
        """Test request from an untrusted remote."""
        fix = proxyfix.ProxyFix.from_config(create_config_getter(["127.0.0.1"]))
        env = {
            "REMOTE_ADDR": "8.8.8.8",
            "HTTP_HOST": "example.com",
            "wsgi.url_scheme": "http",
            "HTTP_X_FORWARDED_FOR": "8.8.8.8",
            "HTTP_X_FORWARDED_HOST": "untrusted.com",
            "HTTP_X_FORWARDED_PROTO": "https",
        }
        expected_env = copy_env(env)
        fix.update_environ(env)
        assert env == expected_env

    def test_new_ip_equals_old_ip(self):
        """Test a local request with HTTPS."""
        fix = proxyfix.ProxyFix.from_config(create_config_getter(["127.0.0.1"]))
        env = {
            "REMOTE_ADDR": "127.0.0.1",
            "HTTP_HOST": "example.com",
            "wsgi.url_scheme": "http",
            "HTTP_X_FORWARDED_FOR": "127.0.0.1",
            "HTTP_X_FORWARDED_PROTO": "https",
        }
        expected_env = copy_env(env)
        expected_env["wsgi.url_scheme"] = "https"
        fix.update_environ(env)
        assert env == expected_env

    def test_no_proxy_works_transparently(self):
        """Test updating the environment without any reverse proxy."""
        fix = proxyfix.ProxyFix.from_config(create_config_getter(["127.0.0.1"]))
        env = {"REMOTE_ADDR": "127.0.0.1", "HTTP_HOST": "example.com", "wsgi.url_scheme": "http"}
        expected_env = copy_env(env)
        fix.update_environ(env)
        assert env == expected_env

    @pytest.mark.parametrize(
        "forwarded_for,expected",
        [
            (["8.8.8.8"], "8.8.8.8"),
            (["127.0.0.1"], "127.0.0.1"),
            (["127.0.0.1", "8.8.8.8"], "8.8.8.8"),
            (["8.8.8.8", "10.0.0.1", "127.0.0.1", "1.1.1.1"], "1.1.1.1"),
            (["no-ip", "127.0.0.1"], "127.0.0.1"),
        ],
    )
    def test_get_remote_addr(self, forwarded_for, expected):
        """Test getting the innermost non-trusted IP address."""
        fix = proxyfix.ProxyFix.from_config(create_config_getter(["127.0.0.1", "10.0.0.1"]))
        assert fix.get_remote_addr(forwarded_for) == expected

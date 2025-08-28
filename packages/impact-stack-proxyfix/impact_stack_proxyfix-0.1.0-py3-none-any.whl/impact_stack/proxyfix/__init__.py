"""WSGI ProxyFix middleware."""

import typing as t
from ipaddress import ip_address


def _split(string):
    return string.split(",") if string else []


class ProxyFix:
    """This is a slightly modified version of werkzeug's ProxyFix.

    Instead of using a fixed number of proxies it uses a list of trusted IP
    addresses.

    This middleware can be applied to add HTTP proxy support to an
    application that was not designed with HTTP proxies in mind.  It
    sets `REMOTE_ADDR`, `HTTP_HOST` from `X-Forwarded` headers.

    The original values of `REMOTE_ADDR` and `HTTP_HOST` are stored in
    the WSGI environment as `werkzeug.proxy_fix.orig_remote_addr` and
    `werkzeug.proxy_fix.orig_http_host`.

    Args:
        proxies: List of IP-addreses which’s X-Forwarded headers should be trusted.
    """

    @classmethod
    def from_config(cls, config_getter: t.Callable[[str, t.Any], t.Any]):
        """Create a new instance from a config getter function."""
        return cls(config_getter("PROXYFIX_TRUSTED", ["127.0.0.1"]))

    def __init__(self, proxies: t.Iterable[str]):
        """Create a new instance by passing the list of trusted proxies."""
        self.trusted = frozenset(ip_address(p.strip()) for p in proxies)

    def get_remote_addr(self, forwarded_for: list[str]):
        """Select the first “untrusted” remote addr.

        Values to X-Forwarded-For are expected to be appended so the inner proxy layers are to the
        right. The innermost untrusted IP is returned.
        """
        previous = None
        for ip_str in reversed(forwarded_for):
            ip_str = ip_str.strip()
            try:
                if ip_address(ip_str) not in self.trusted:
                    return ip_str
            except ValueError:
                return previous
            previous = ip_str
        return previous

    def update_environ(self, environ):
        """Update the WSGI environment according to the headers."""
        env = environ.get
        remote_addr = env("REMOTE_ADDR")
        if not remote_addr:
            return

        try:
            remote_addr_ip = ip_address(remote_addr)
        except ValueError:
            remote_addr_ip = ip_address("127.0.0.1")

        environ.update(
            {
                "werkzeug.proxy_fix.orig_wsgi_url_scheme": env("wsgi.url_scheme"),
                "werkzeug.proxy_fix.orig_remote_addr": env("REMOTE_ADDR"),
                "werkzeug.proxy_fix.orig_http_host": env("HTTP_HOST"),
            }
        )

        if remote_addr_ip in self.trusted:
            if forwarded_host := env("HTTP_X_FORWARDED_HOST", ""):
                environ["HTTP_HOST"] = forwarded_host
            if forwarded_proto := env("HTTP_X_FORWARDED_PROTO", ""):
                https = "https" in forwarded_proto.lower()
                environ["wsgi.url_scheme"] = "https" if https else "http"
            forwarded_for = _split(env("HTTP_X_FORWARDED_FOR", ""))
            if remote_addr := self.get_remote_addr(forwarded_for):
                environ["REMOTE_ADDR"] = remote_addr

    def wrap(self, wsgi_app):
        """Wrap a wsgi app with this middleware."""

        def wrapped(environ, start_response):
            self.update_environ(environ)
            return wsgi_app(environ, start_response)

        return wrapped

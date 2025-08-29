#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

from xenoslib.extend import YamlConfig

from requests_mock.mocker import _original_send, _set_method, Mocker
from requests_mock import adapter, exceptions


# Doc reference: https://requests-mock.readthedocs.io/en/latest/

logger = logging.getLogger(__name__)


class RequestsMocker(Mocker):
    def __init__(self, **kwargs):
        """Create a new mocker adapter.

        :param str kw: Pass the mock object through to the decorated function
            as this named keyword argument, rather than a positional argument.
        :param bool real_http: True to send the request to the real requested
            uri if there is not a mock installed for it. Defaults to False.
        """
        super().__init__(**kwargs)
        self._config = YamlConfig("mock.yml")
        for url, value in self._config.items():
            method, text = value
            # logger.
            self._adapter.register_uri(method, url, text=text)

    def start(self):
        """Start mocking requests.

        Install the adapter and the wrappers required to intercept requests.
        """
        if self._last_send:
            raise RuntimeError("Mocker has already been started")

        # backup last `send` for restoration on `self.stop`
        self._last_send = self._mock_target.send
        self._last_get_adapter = self._mock_target.get_adapter

        def _fake_get_adapter(session, url):
            return self._adapter

        def _fake_send(session, request, **kwargs):
            # mock get_adapter
            _set_method(session, "get_adapter", _fake_get_adapter)

            # NOTE(jamielennox): self._last_send vs _original_send. Whilst it
            # seems like here we would use _last_send there is the possibility
            # that the user has messed up and is somehow nesting their mockers.
            # If we call last_send at this point then we end up calling this
            # function again and the outer level adapter ends up winning.
            # All we really care about here is that our adapter is in place
            # before calling send so we always jump directly to the real
            # function so that our most recently patched send call ends up
            # putting in the most recent adapter. It feels funny, but it works.

            try:
                return _original_send(session, request, **kwargs)
            except exceptions.NoMockAddress:
                if not self.real_http:
                    raise
            except adapter._RunRealHTTP:
                # this mocker wants you to run the request through the real
                # requests library rather than the mocking. Let it.
                pass
            finally:
                # restore get_adapter
                _set_method(session, "get_adapter", self._last_get_adapter)

            # if we are here it means we must run the real http request
            # Or, with nested mocks, to the parent mock, that is why we use
            # _last_send here instead of _original_send
            if isinstance(self._mock_target, type):
                response = self._last_send(session, request, **kwargs)
                self._config[request.url] = [request.method, response.text]
                self._config.save()
                self._adapter.register_uri(request.method, request.url, text=response.text)
                return response
            else:
                return self._last_send(request, **kwargs)

        _set_method(self._mock_target, "send", _fake_send)

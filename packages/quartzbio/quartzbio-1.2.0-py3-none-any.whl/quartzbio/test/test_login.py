# -*- coding: utf-8 -*-
from __future__ import absolute_import

import contextlib
import sys
import unittest
import quartzbio
import quartzbio.cli.auth as auth


@contextlib.contextmanager
def nostdout():
    savestderr = sys.stdout

    class Devnull(object):
        def write(self, _):
            pass

    sys.stdout = Devnull()
    try:
        yield
    finally:
        sys.stdout = savestderr


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.api_host = quartzbio.get_api_host()
        # temporarily replace with dummy methods for testing
        self.delete_credentials = auth.delete_credentials
        auth.delete_credentials = lambda: None

    def tearDown(self):
        quartzbio.client._host = self.api_host
        auth.delete_credentials = self.delete_credentials

    def test_bad_login(self):
        with nostdout():
            self.assertEqual(auth.login_and_save_credentials(), None, "Invalid login")

            # Test invalid host
            quartzbio.client._host = "https://some.fake.domain.foobar"
            self.assertEqual(auth.login_and_save_credentials(), None, "Invalid login")

    def test_init_login(self):
        from quartzbio import login
        from quartzbio.client import client

        _auth = client._auth

        client._auth = None
        login(api_key="TEST_KEY")
        self.assertEqual(client._auth.token, "TEST_KEY")

        # Reset the key
        client._auth = _auth

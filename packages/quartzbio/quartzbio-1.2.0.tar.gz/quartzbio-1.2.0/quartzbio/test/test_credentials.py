# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import shutil
import sys
import unittest
import quartzbio
import quartzbio.cli.credentials as creds
import contextlib


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


class TestCredentials(unittest.TestCase):
    def setUp(self):
        self.quartzbiodir = os.path.join(
            os.path.dirname(__file__), "data", ".quartzbio"
        )
        self.api_host = quartzbio.get_api_host()
        quartzbio.client._host = "https://api.quartzbio.com"

    def tearDown(self):
        quartzbio.client._host = self.api_host
        if os.path.isdir(self.quartzbiodir):
            shutil.rmtree(self.quartzbiodir)

    def test_credentials(self):
        datadir = os.path.join(os.path.dirname(__file__), "data")
        os.environ["HOME"] = datadir

        # Make sure we don't have have the test quartzbio directory
        if os.path.isdir(self.quartzbiodir):
            shutil.rmtree(self.quartzbiodir)

        cred_file = creds.netrc.path()
        self.assertTrue(
            os.path.exists(cred_file), "cred file created when it doesn't exist first"
        )

        self.assertEqual(creds.get_credentials(), None, "Should not find credentials")

        test_credentials_file = os.path.join(datadir, "test_creds")
        shutil.copy(test_credentials_file, cred_file)

        auths = creds.get_credentials()
        self.assertTrue(auths is not None, "Should find credentials")

        quartzbio.client._host = "https://example.com"

        auths = creds.get_credentials()
        self.assertEqual(
            auths,
            None,
            f"Should not find credentials for host {quartzbio.get_api_host()}",
        )

        quartzbio.client._host = "https://api.quartzbio.com"
        creds.delete_credentials()
        auths = creds.get_credentials()
        self.assertEqual(
            auths,
            None,
            f"Should not find removed credentials for host {quartzbio.get_api_host()}",
        )

        pair = (
            "testagain@quartzbio.com",
            "b00b00",
        )
        creds.save_credentials(*pair)
        auths = creds.get_credentials()
        self.assertTrue(
            auths is not None,
            "Should get newly set credentials for " "host {0}".format(
                quartzbio.get_api_host()
            ),
        )

        expected = (quartzbio.get_api_host(), pair[0], "Token", pair[1])
        self.assertEqual(auths, expected, "Should get back creds we saved")

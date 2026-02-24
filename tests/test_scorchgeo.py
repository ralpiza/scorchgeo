#!/usr/bin/env python

"""Tests for `scorchgeo` package."""

import unittest

import scorchgeo


class TestScorchgeo(unittest.TestCase):
    """Tests for `scorchgeo` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        pass

    def tearDown(self):
        """Tear down test fixtures, if any."""
        pass

    def test_000_something(self):
        """Test that a Map instance can be created."""
        m = scorchgeo.Map()
        self.assertIsInstance(m, scorchgeo.Map)

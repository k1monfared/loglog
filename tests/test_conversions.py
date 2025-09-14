#!/usr/bin/env python3
"""
Pytest-compatible tests using the new test framework.
This file integrates the test_framework.py with pytest for CI/CD compatibility.
"""

import pytest
from test_framework import TestFramework


class TestLogLogConversions:
    """Test class for LogLog conversions using the new framework"""

    @classmethod
    def setup_class(cls):
        """Set up the test framework"""
        cls.framework = TestFramework()
        cls.framework.clean_temp_files()

    def test_md_to_log_conversions(self):
        """Test all markdown to log conversions"""
        assert self.framework.run_md_to_log_tests(), "MD to Log tests failed"

    def test_log_to_md_conversions(self):
        """Test all log to markdown conversions"""
        assert self.framework.run_log_to_md_tests(), "Log to MD tests failed"

    def test_roundtrip_conversions(self):
        """Test all roundtrip conversions"""
        assert self.framework.run_roundtrip_tests(), "Roundtrip tests failed"

    @classmethod
    def teardown_class(cls):
        """Clean up after tests"""
        cls.framework.clean_temp_files()


if __name__ == "__main__":
    # Allow running this file directly
    import sys
    framework = TestFramework()
    success = framework.run_all_tests()
    sys.exit(0 if success else 1)
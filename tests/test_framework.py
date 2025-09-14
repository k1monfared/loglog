#!/usr/bin/env python3
"""
Test framework for LogLog conversions with auditable input/output files.

This framework:
- Reads test cases from test_manifest.yaml
- Uses organized input/output files in tests/data/
- Creates temporary files for actual outputs (not overwriting expected ones)
- Provides clear comparison and diff capabilities
- Allows users to audit and adjust test expectations
"""

import os
import sys
import yaml
import tempfile
from pathlib import Path
from difflib import unified_diff

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from loglog import from_md, build_tree_from_text


class TestFramework:
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.data_dir = self.test_dir / 'data'
        self.temp_dir = self.data_dir / 'temp'
        self.manifest_file = self.data_dir / 'test_manifest.yaml'

        # Ensure temp directory exists
        self.temp_dir.mkdir(exist_ok=True)

        # Load test manifest
        with open(self.manifest_file, 'r') as f:
            self.manifest = yaml.safe_load(f)

    def run_md_to_log_tests(self):
        """Run all markdown to log conversion tests"""
        print("=" * 60)
        print("MARKDOWN TO LOG CONVERSION TESTS")
        print("=" * 60)

        tests = self.manifest.get('md_to_log_tests', [])
        passed = 0
        failed = 0

        for test_case in tests:
            print(f"\nRunning: {test_case['name']} - {test_case['description']}")

            # Read input file
            input_path = self.data_dir / test_case['input_file']
            expected_output_path = self.data_dir / test_case['expected_output']
            temp_output_path = self.temp_dir / f"{test_case['name']}_actual.log"

            with open(input_path, 'r') as f:
                input_content = f.read()

            # Perform conversion
            actual_output = from_md(input_content)

            # Write to temporary file
            with open(temp_output_path, 'w') as f:
                f.write(actual_output)

            # Read expected output
            with open(expected_output_path, 'r') as f:
                expected_output = f.read()

            # Compare
            if self._compare_outputs(expected_output, actual_output, test_case['name']):
                print(f"✓ PASSED: {test_case['name']}")
                passed += 1
            else:
                print(f"✗ FAILED: {test_case['name']}")
                print(f"  Expected: {expected_output_path}")
                print(f"  Actual: {temp_output_path}")
                failed += 1

        print(f"\nMD to Log Tests: {passed} passed, {failed} failed")
        return failed == 0

    def run_log_to_md_tests(self):
        """Run all log to markdown conversion tests"""
        print("\n" + "=" * 60)
        print("LOG TO MARKDOWN CONVERSION TESTS")
        print("=" * 60)

        tests = self.manifest.get('log_to_md_tests', [])
        passed = 0
        failed = 0

        for test_case in tests:
            print(f"\nRunning: {test_case['name']} - {test_case['description']}")

            # Read input file
            input_path = self.data_dir / test_case['input_file']
            expected_output_path = self.data_dir / test_case['expected_output']
            temp_output_path = self.temp_dir / f"{test_case['name']}_actual.md"

            with open(input_path, 'r') as f:
                input_content = f.read()

            # Perform conversion
            tree = build_tree_from_text(input_content)
            actual_output = tree.to_md()

            # Write to temporary file
            with open(temp_output_path, 'w') as f:
                f.write(actual_output)

            # Read expected output
            with open(expected_output_path, 'r') as f:
                expected_output = f.read()

            # Compare
            if self._compare_outputs(expected_output, actual_output, test_case['name']):
                print(f"✓ PASSED: {test_case['name']}")
                passed += 1
            else:
                print(f"✗ FAILED: {test_case['name']}")
                print(f"  Expected: {expected_output_path}")
                print(f"  Actual: {temp_output_path}")
                failed += 1

        print(f"\nLog to MD Tests: {passed} passed, {failed} failed")
        return failed == 0

    def run_roundtrip_tests(self):
        """Run all roundtrip conversion tests"""
        print("\n" + "=" * 60)
        print("ROUNDTRIP CONVERSION TESTS")
        print("=" * 60)

        tests = self.manifest.get('roundtrip_tests', [])
        passed = 0
        failed = 0

        for test_case in tests:
            print(f"\nRunning: {test_case['name']} - {test_case['description']}")

            input_path = self.data_dir / test_case['input_file']
            expected_output_path = self.data_dir / test_case['expected_output']
            temp_output_path = self.temp_dir / f"{test_case['name']}_actual_final.{expected_output_path.suffix[1:]}"

            with open(input_path, 'r') as f:
                input_content = f.read()

            # Perform roundtrip conversion
            if test_case['test_type'] == 'md_to_log_to_md':
                # MD -> Log -> MD
                log_intermediate = from_md(input_content)
                tree = build_tree_from_text(log_intermediate)
                actual_output = tree.to_md()
            else:  # log_to_md_to_log
                # Log -> MD -> Log
                tree = build_tree_from_text(input_content)
                md_intermediate = tree.to_md()
                actual_output = from_md(md_intermediate)

            # Write to temporary file
            with open(temp_output_path, 'w') as f:
                f.write(actual_output)

            # Read expected output
            with open(expected_output_path, 'r') as f:
                expected_output = f.read()

            # Compare
            if self._compare_outputs(expected_output, actual_output, test_case['name']):
                print(f"✓ PASSED: {test_case['name']}")
                passed += 1
            else:
                print(f"✗ FAILED: {test_case['name']}")
                print(f"  Expected: {expected_output_path}")
                print(f"  Actual: {temp_output_path}")
                failed += 1

        print(f"\nRoundtrip Tests: {passed} passed, {failed} failed")
        return failed == 0

    def _compare_outputs(self, expected, actual, test_name):
        """Compare expected and actual outputs, show diff if different"""
        if expected == actual:
            return True

        print(f"  DIFF for {test_name}:")
        diff_lines = list(unified_diff(
            expected.splitlines(keepends=True),
            actual.splitlines(keepends=True),
            fromfile='expected',
            tofile='actual',
            lineterm=''
        ))

        for line in diff_lines[:20]:  # Show first 20 diff lines
            print(f"    {line.rstrip()}")

        if len(diff_lines) > 20:
            print(f"    ... ({len(diff_lines) - 20} more diff lines)")

        return False

    def run_all_tests(self):
        """Run all test suites"""
        print("LogLog Test Framework")
        print("=" * 60)

        md_to_log_success = self.run_md_to_log_tests()
        log_to_md_success = self.run_log_to_md_tests()
        roundtrip_success = self.run_roundtrip_tests()

        print("\n" + "=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)

        if md_to_log_success and log_to_md_success and roundtrip_success:
            print("✓ ALL TESTS PASSED")
            return True
        else:
            print("✗ SOME TESTS FAILED")
            if not md_to_log_success:
                print("  - MD to Log tests had failures")
            if not log_to_md_success:
                print("  - Log to MD tests had failures")
            if not roundtrip_success:
                print("  - Roundtrip tests had failures")
            return False

    def clean_temp_files(self):
        """Clean up temporary test files"""
        import glob
        temp_files = glob.glob(str(self.temp_dir / "*"))
        for temp_file in temp_files:
            if os.path.isfile(temp_file):
                os.remove(temp_file)
        print(f"Cleaned {len(temp_files)} temporary files")


if __name__ == "__main__":
    framework = TestFramework()

    # Clean temp files first
    framework.clean_temp_files()

    # Run tests
    success = framework.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)
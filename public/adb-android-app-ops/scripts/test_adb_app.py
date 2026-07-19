import os
import sys
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import adb_app  # noqa: E402


class EncodeInputTextTest(unittest.TestCase):
    def test_replaces_spaces(self) -> None:
        self.assertEqual(adb_app.encode_input_text("hello world"), "hello%sworld")

    def test_escapes_shell_metacharacters(self) -> None:
        self.assertEqual(adb_app.encode_input_text("a&b"), r"a\&b")
        self.assertEqual(adb_app.encode_input_text("a|b"), r"a\|b")
        self.assertEqual(adb_app.encode_input_text("a'b"), r"a\'b")
        self.assertEqual(adb_app.encode_input_text('a"b'), r'a\"b')

    def test_newlines_become_space(self) -> None:
        self.assertEqual(adb_app.encode_input_text("a\nb"), "a b")


class ParseDevicesOutputTest(unittest.TestCase):
    def test_parses_devices(self) -> None:
        sample = """List of devices attached
emulator-5554 device product:sdk model:sdk device:generic transport_id:1
ABCDEF0123456789 unauthorized usb:1-1
ZYX987 offline
"""
        devices = adb_app.parse_devices_output(sample)
        self.assertEqual(len(devices), 3)
        self.assertEqual(devices[0]["serial"], "emulator-5554")
        self.assertEqual(devices[0]["state"], "device")
        self.assertIn("product:sdk", devices[0]["details"])
        self.assertEqual(devices[1]["state"], "unauthorized")
        self.assertEqual(devices[2]["state"], "offline")


class ParsePidofOutputTest(unittest.TestCase):
    def test_parses_single_pid(self) -> None:
        self.assertEqual(adb_app.parse_pidof_output("1234\n"), [1234])

    def test_parses_multiple_pids(self) -> None:
        self.assertEqual(adb_app.parse_pidof_output("1234 5678\n"), [1234, 5678])


class ParseCurrentActivityTest(unittest.TestCase):
    def test_parses_resumed_activity(self) -> None:
        sample = "mResumedActivity: ActivityRecord{abcd u0 com.example/.MainActivity t42}\n"
        parsed = adb_app.parse_resumed_activity(sample)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["package"], "com.example")
        self.assertEqual(parsed["activity"], ".MainActivity")

    def test_parses_current_focus(self) -> None:
        sample = "mCurrentFocus=Window{abcd u0 com.example/com.example.MainActivity}\n"
        parsed = adb_app.parse_current_focus(sample)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["package"], "com.example")
        self.assertEqual(parsed["activity"], "com.example.MainActivity")


if __name__ == "__main__":
    unittest.main()


#!/usr/bin/env python3
"""
adb_app.py

A small, bounded wrapper around adb (Android Debug Bridge) for common Android app
operations. Prefer commands that terminate (e.g., logcat dumps or time-bounded
logcat follow) to avoid hanging automation.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional


class UsageError(RuntimeError):
    pass


class AdbCommandError(RuntimeError):
    pass


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _format_cmd(cmd: List[str]) -> str:
    return " ".join(shlex.quote(x) for x in cmd)


def resolve_adb_path(adb_arg: Optional[str]) -> str:
    adb = adb_arg or os.environ.get("ADB_PATH") or "adb"
    if os.path.sep in adb:
        p = Path(adb)
        if not p.exists():
            raise UsageError(f"adb not found at: {adb}. Set --adb or ADB_PATH.")
        return str(p)
    resolved = shutil.which(adb)
    if not resolved:
        raise UsageError("adb not found in PATH. Install Android Platform Tools or set --adb/ADB_PATH.")
    return resolved


def run_cmd(
    cmd: List[str],
    *,
    timeout_s: Optional[float],
    text: bool,
) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_s,
            text=text,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise AdbCommandError(f"Command timed out after {timeout_s}s: {_format_cmd(cmd)}") from e
    except OSError as e:
        raise AdbCommandError(f"Failed to run command: {_format_cmd(cmd)} ({e})") from e


def parse_devices_output(output: str) -> List[Dict[str, str]]:
    devices: List[Dict[str, str]] = []
    for raw in output.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.lower().startswith("list of devices attached"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        serial = parts[0]
        state = parts[1]
        details = " ".join(parts[2:]) if len(parts) > 2 else ""
        devices.append({"serial": serial, "state": state, "details": details})
    return devices


def list_devices(adb_path: str, *, timeout_s: float) -> List[Dict[str, str]]:
    cp = run_cmd([adb_path, "devices", "-l"], timeout_s=timeout_s, text=True)
    if cp.returncode != 0:
        raise AdbCommandError(
            f"adb devices failed (exit={cp.returncode}): {cp.stderr.strip() or cp.stdout.strip()}"
        )
    return parse_devices_output(cp.stdout)


def resolve_serial(adb_path: str, serial_arg: Optional[str], *, timeout_s: float) -> str:
    if serial_arg:
        return serial_arg
    env_serial = os.environ.get("ANDROID_SERIAL")
    if env_serial:
        return env_serial

    devices = list_devices(adb_path, timeout_s=timeout_s)
    online = [d for d in devices if d["state"] == "device"]
    if len(online) == 1:
        return online[0]["serial"]

    if not online:
        raise UsageError(
            "No online adb devices found. Connect a device/emulator and re-run, or pass --serial."
        )

    serials = ", ".join(d["serial"] for d in online)
    raise UsageError(
        f"Multiple adb devices are attached ({serials}). Pass --serial or set ANDROID_SERIAL."
    )


def adb_base(adb_path: str, serial: Optional[str]) -> List[str]:
    cmd = [adb_path]
    if serial:
        cmd += ["-s", serial]
    return cmd


def run_adb_text(
    adb_path: str,
    serial: str,
    adb_args: List[str],
    *,
    timeout_s: float,
) -> str:
    cmd = adb_base(adb_path, serial) + adb_args
    cp = run_cmd(cmd, timeout_s=timeout_s, text=True)
    if cp.returncode != 0:
        raise AdbCommandError(
            f"adb failed (exit={cp.returncode}): {_format_cmd(cmd)}\n{cp.stderr.strip() or cp.stdout.strip()}"
        )
    return cp.stdout


def run_adb_bytes(
    adb_path: str,
    serial: str,
    adb_args: List[str],
    *,
    timeout_s: float,
) -> bytes:
    cmd = adb_base(adb_path, serial) + adb_args
    cp = run_cmd(cmd, timeout_s=timeout_s, text=False)
    if cp.returncode != 0:
        stderr = (cp.stderr or b"").decode("utf-8", errors="replace").strip()
        stdout = (cp.stdout or b"").decode("utf-8", errors="replace").strip()
        raise AdbCommandError(f"adb failed (exit={cp.returncode}): {_format_cmd(cmd)}\n{stderr or stdout}")
    return cp.stdout


_TEXT_ESCAPE_CHARS = set("&|;<>()$`\\\"'")


def encode_input_text(text: str) -> str:
    # adb shell input text treats whitespace and some shell metacharacters specially.
    # This encoding is intentionally conservative; if it fails on a specific device,
    # use --raw and pass a device-specific encoding.
    out: List[str] = []
    for ch in text:
        if ch == " ":
            out.append("%s")
            continue
        if ch in _TEXT_ESCAPE_CHARS:
            out.append("\\" + ch)
            continue
        if ch in ("\n", "\r", "\t"):
            # Newlines/tabs are not representable in a single `input text` call.
            out.append(" ")
            continue
        out.append(ch)
    return "".join(out)


def parse_pidof_output(output: str) -> List[int]:
    pids: List[int] = []
    for part in output.split():
        if part.isdigit():
            pids.append(int(part))
    return pids


def get_pid(
    adb_path: str,
    serial: str,
    package: str,
    *,
    timeout_s: float,
) -> List[int]:
    out = run_adb_text(adb_path, serial, ["shell", "pidof", package], timeout_s=timeout_s)
    pids = parse_pidof_output(out)
    if not pids:
        raise AdbCommandError(f"No PID found for package: {package} (is the app running?)")
    return pids


def parse_resumed_activity(dumpsys_activity: str) -> Optional[Dict[str, str]]:
    # Best-effort parsing across Android versions/OEMs.
    patterns = [
        r"mResumedActivity:.*?\s([\w\._]+)/([\w\._$]+)",
        r"ResumedActivity:.*?\s([\w\._]+)/([\w\._$]+)",
        r"mFocusedActivity:.*?\s([\w\._]+)/([\w\._$]+)",
    ]
    for pat in patterns:
        m = re.search(pat, dumpsys_activity)
        if m:
            return {"package": m.group(1), "activity": m.group(2), "source": "dumpsys_activity"}
    return None


def parse_current_focus(dumpsys_window: str) -> Optional[Dict[str, str]]:
    patterns = [
        r"mCurrentFocus=.*?\s([\w\._]+)/([\w\._$]+)",
        r"mFocusedApp=.*?\s([\w\._]+)/([\w\._$]+)",
    ]
    for pat in patterns:
        m = re.search(pat, dumpsys_window)
        if m:
            return {"package": m.group(1), "activity": m.group(2), "source": "dumpsys_window"}
    return None


def emit_ok(args: argparse.Namespace, payload: Any) -> None:
    if args.json:
        if isinstance(payload, dict):
            out = {"ok": True, **payload}
        else:
            out = {"ok": True, "result": payload}
        print(_json_dumps(out))
        return

    if isinstance(payload, str):
        sys.stdout.write(payload)
        if payload and not payload.endswith("\n"):
            sys.stdout.write("\n")
        return

    print(payload)


def emit_error(args: argparse.Namespace, message: str, *, code: int) -> None:
    if args.json:
        print(_json_dumps({"ok": False, "error": message, "code": code}))
    else:
        print(message, file=sys.stderr)


def require_serial(args: argparse.Namespace, adb_path: str) -> str:
    return resolve_serial(adb_path, args.serial, timeout_s=args.timeout)


def cmd_devices(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    cp = run_cmd([adb_path, "devices", "-l"], timeout_s=args.timeout, text=True)
    if cp.returncode != 0:
        raise AdbCommandError(f"adb devices failed (exit={cp.returncode}): {cp.stderr.strip()}")
    devices = parse_devices_output(cp.stdout)
    if args.json:
        emit_ok(args, {"devices": devices})
    else:
        emit_ok(args, cp.stdout.strip())
    return 0


def cmd_shell(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)
    if not args.shell_args:
        raise UsageError("shell requires args after '--', e.g.: shell -- getprop ro.build.version.release")
    out = run_adb_text(adb_path, serial, ["shell", *args.shell_args], timeout_s=args.timeout)
    emit_ok(args, out.strip())
    return 0


def cmd_pidof(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)
    pids = get_pid(adb_path, serial, args.package, timeout_s=args.timeout)
    if args.all:
        if args.json:
            emit_ok(args, {"package": args.package, "pids": pids})
        else:
            emit_ok(args, " ".join(str(p) for p in pids))
    else:
        if args.json:
            emit_ok(args, {"package": args.package, "pid": pids[0]})
        else:
            emit_ok(args, str(pids[0]))
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)

    apk = Path(args.apk)
    if not apk.exists():
        raise UsageError(f"APK not found: {apk}")
    cmd = ["install"]
    if not args.no_replace:
        cmd.append("-r")
    out = run_adb_text(adb_path, serial, [*cmd, str(apk)], timeout_s=max(args.timeout, 60.0))
    emit_ok(args, out.strip())
    return 0


def cmd_uninstall(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)

    if not args.yes:
        raise UsageError("uninstall is destructive. Re-run with --yes.")
    out = run_adb_text(adb_path, serial, ["uninstall", args.package], timeout_s=max(args.timeout, 30.0))
    emit_ok(args, out.strip())
    return 0


def cmd_start(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)

    if args.activity:
        if "/" in args.activity:
            component = args.activity
        else:
            component = f"{args.package}/{args.activity}"
        cmd = ["shell", "am", "start"]
        if args.wait:
            cmd.append("-W")
        cmd += ["-n", component]
        out = run_adb_text(adb_path, serial, cmd, timeout_s=max(args.timeout, 30.0))
        emit_ok(args, out.strip())
        return 0

    out = run_adb_text(
        adb_path,
        serial,
        [
            "shell",
            "monkey",
            "-p",
            args.package,
            "-c",
            "android.intent.category.LAUNCHER",
            "1",
        ],
        timeout_s=max(args.timeout, 30.0),
    )
    emit_ok(args, out.strip())
    return 0


def cmd_stop(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)
    out = run_adb_text(adb_path, serial, ["shell", "am", "force-stop", args.package], timeout_s=args.timeout)
    emit_ok(args, out.strip())
    return 0


def cmd_clear(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)
    if not args.yes:
        raise UsageError("clear is destructive (pm clear). Re-run with --yes.")
    out = run_adb_text(adb_path, serial, ["shell", "pm", "clear", args.package], timeout_s=max(args.timeout, 30.0))
    emit_ok(args, out.strip())
    return 0


def cmd_grant(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)
    out = run_adb_text(
        adb_path, serial, ["shell", "pm", "grant", args.package, args.permission], timeout_s=args.timeout
    )
    emit_ok(args, out.strip())
    return 0


def cmd_revoke(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)
    out = run_adb_text(
        adb_path, serial, ["shell", "pm", "revoke", args.package, args.permission], timeout_s=args.timeout
    )
    emit_ok(args, out.strip())
    return 0


def cmd_deeplink(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)

    cmd = [
        "shell",
        "am",
        "start",
        "-a",
        "android.intent.action.VIEW",
        "-d",
        args.url,
    ]
    if args.package:
        cmd += ["-p", args.package]
    out = run_adb_text(adb_path, serial, cmd, timeout_s=max(args.timeout, 30.0))
    emit_ok(args, out.strip())
    return 0


def cmd_tap(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)
    out = run_adb_text(
        adb_path, serial, ["shell", "input", "tap", str(args.x), str(args.y)], timeout_s=args.timeout
    )
    emit_ok(args, out.strip())
    return 0


def cmd_swipe(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)
    cmd = [
        "shell",
        "input",
        "swipe",
        str(args.x1),
        str(args.y1),
        str(args.x2),
        str(args.y2),
    ]
    if args.duration_ms is not None:
        cmd.append(str(args.duration_ms))
    out = run_adb_text(adb_path, serial, cmd, timeout_s=args.timeout)
    emit_ok(args, out.strip())
    return 0


def cmd_text(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)
    text = args.text if args.raw else encode_input_text(args.text)
    out = run_adb_text(adb_path, serial, ["shell", "input", "text", text], timeout_s=args.timeout)
    emit_ok(args, out.strip())
    return 0


def cmd_keyevent(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)
    out = run_adb_text(adb_path, serial, ["shell", "input", "keyevent", args.key], timeout_s=args.timeout)
    emit_ok(args, out.strip())
    return 0


def _ensure_parent_dir(path: Path) -> None:
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def cmd_screenshot(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)

    out_path = Path(args.out)
    _ensure_parent_dir(out_path)

    data = run_adb_bytes(adb_path, serial, ["exec-out", "screencap", "-p"], timeout_s=max(args.timeout, 30.0))
    out_path.write_bytes(data)
    if args.json:
        emit_ok(args, {"out": str(out_path)})
    else:
        emit_ok(args, str(out_path))
    return 0


def cmd_screenrecord(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)

    if args.seconds <= 0:
        raise UsageError("--seconds must be > 0")
    if args.seconds > 180:
        raise UsageError("--seconds must be <= 180 (screenrecord time limit)")

    out_path = Path(args.out)
    _ensure_parent_dir(out_path)

    remote = f"/sdcard/codex_record_{uuid.uuid4().hex}.mp4"
    run_adb_text(
        adb_path,
        serial,
        ["shell", "screenrecord", "--time-limit", str(args.seconds), remote],
        timeout_s=max(args.timeout, float(args.seconds) + 15.0),
    )
    run_adb_text(adb_path, serial, ["pull", remote, str(out_path)], timeout_s=max(args.timeout, 60.0))

    cleanup_error: Optional[str] = None
    try:
        run_adb_text(adb_path, serial, ["shell", "rm", "-f", remote], timeout_s=max(args.timeout, 10.0))
    except AdbCommandError as e:
        cleanup_error = str(e)
        print(f"Warning: failed to cleanup remote file: {remote}\n{e}", file=sys.stderr)

    payload: Dict[str, Any] = {"out": str(out_path)}
    if cleanup_error:
        payload["cleanup_error"] = cleanup_error
    if args.json:
        emit_ok(args, payload)
    else:
        emit_ok(args, str(out_path))
    return 0


def cmd_uidump(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)

    out_path = Path(args.out)
    _ensure_parent_dir(out_path)

    remote = f"/sdcard/codex_uidump_{uuid.uuid4().hex}.xml"
    run_adb_text(adb_path, serial, ["shell", "uiautomator", "dump", remote], timeout_s=max(args.timeout, 30.0))
    run_adb_text(adb_path, serial, ["pull", remote, str(out_path)], timeout_s=max(args.timeout, 30.0))

    cleanup_error: Optional[str] = None
    try:
        run_adb_text(adb_path, serial, ["shell", "rm", "-f", remote], timeout_s=max(args.timeout, 10.0))
    except AdbCommandError as e:
        cleanup_error = str(e)
        print(f"Warning: failed to cleanup remote file: {remote}\n{e}", file=sys.stderr)

    payload: Dict[str, Any] = {"out": str(out_path)}
    if cleanup_error:
        payload["cleanup_error"] = cleanup_error
    if args.json:
        emit_ok(args, payload)
    else:
        emit_ok(args, str(out_path))
    return 0


def _resolve_pid_filter(
    adb_path: str,
    serial: str,
    *,
    package: Optional[str],
    pid: Optional[int],
    allow_missing_pid: bool,
    timeout_s: float,
) -> Optional[int]:
    if pid is not None:
        return pid
    if not package:
        return None
    try:
        pids = get_pid(adb_path, serial, package, timeout_s=timeout_s)
        return pids[0]
    except AdbCommandError:
        if allow_missing_pid:
            return None
        raise


def cmd_logcat_dump(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)

    if args.clear:
        run_adb_text(adb_path, serial, ["logcat", "-c"], timeout_s=max(args.timeout, 10.0))

    pid = _resolve_pid_filter(
        adb_path,
        serial,
        package=args.package,
        pid=args.pid,
        allow_missing_pid=args.allow_missing_pid,
        timeout_s=max(args.timeout, 10.0),
    )

    cmd = ["logcat", "-d", "-v", args.format]
    if args.buffer:
        cmd += ["-b", args.buffer]
    if args.since:
        cmd += ["-T", args.since]
    if pid is not None:
        cmd.append(f"--pid={pid}")

    out = run_adb_text(adb_path, serial, cmd, timeout_s=max(args.timeout, 30.0))
    text = out

    if args.max_lines is not None and args.max_lines > 0:
        lines = text.splitlines()
        text = "\n".join(lines[-args.max_lines :]) + ("\n" if lines else "")

    if args.out:
        out_path = Path(args.out)
        _ensure_parent_dir(out_path)
        out_path.write_text(text, encoding="utf-8")
        if args.json:
            emit_ok(args, {"out": str(out_path)})
        else:
            emit_ok(args, str(out_path))
        return 0

    emit_ok(args, text.rstrip("\n"))
    return 0


def cmd_logcat_follow(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)

    if args.seconds <= 0:
        raise UsageError("--seconds must be > 0")

    if args.clear:
        run_adb_text(adb_path, serial, ["logcat", "-c"], timeout_s=max(args.timeout, 10.0))

    pid = _resolve_pid_filter(
        adb_path,
        serial,
        package=args.package,
        pid=args.pid,
        allow_missing_pid=args.allow_missing_pid,
        timeout_s=max(args.timeout, 10.0),
    )

    cmd = ["logcat", "-v", args.format]
    if args.buffer:
        cmd += ["-b", args.buffer]
    if args.since:
        cmd += ["-T", args.since]
    if pid is not None:
        cmd.append(f"--pid={pid}")

    full_cmd = adb_base(adb_path, serial) + cmd
    terminated_by_timeout = False
    try:
        proc = subprocess.Popen(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError as e:
        raise AdbCommandError(f"Failed to run command: {_format_cmd(full_cmd)} ({e})") from e

    try:
        out, err = proc.communicate(timeout=float(args.seconds))
    except subprocess.TimeoutExpired:
        terminated_by_timeout = True
        proc.terminate()
        try:
            out, err = proc.communicate(timeout=5.0)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()

    if not terminated_by_timeout and proc.returncode != 0:
        raise AdbCommandError(f"adb logcat failed (exit={proc.returncode}): {err.strip()}")

    text = out
    if args.max_lines is not None and args.max_lines > 0:
        lines = text.splitlines()
        text = "\n".join(lines[-args.max_lines :]) + ("\n" if lines else "")

    if args.out:
        out_path = Path(args.out)
        _ensure_parent_dir(out_path)
        out_path.write_text(text, encoding="utf-8")
        if args.json:
            emit_ok(args, {"out": str(out_path), "seconds": args.seconds})
        else:
            emit_ok(args, str(out_path))
        return 0

    emit_ok(args, text.rstrip("\n"))
    return 0


def cmd_meminfo(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)
    out = run_adb_text(adb_path, serial, ["shell", "dumpsys", "meminfo", args.package], timeout_s=max(args.timeout, 30.0))
    emit_ok(args, out.strip())
    return 0


def cmd_cpuinfo(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)
    out = run_adb_text(adb_path, serial, ["shell", "dumpsys", "cpuinfo"], timeout_s=max(args.timeout, 30.0))
    emit_ok(args, out.strip())
    return 0


def cmd_current_activity(args: argparse.Namespace) -> int:
    adb_path = resolve_adb_path(args.adb)
    serial = require_serial(args, adb_path)

    activity_raw = run_adb_text(
        adb_path, serial, ["shell", "dumpsys", "activity", "activities"], timeout_s=max(args.timeout, 30.0)
    )
    parsed = parse_resumed_activity(activity_raw)

    window_raw = ""
    if not parsed:
        window_raw = run_adb_text(
            adb_path, serial, ["shell", "dumpsys", "window", "windows"], timeout_s=max(args.timeout, 30.0)
        )
        parsed = parse_current_focus(window_raw)

    if not parsed:
        raise AdbCommandError("Failed to parse current activity/focus from dumpsys output.")

    if args.include_raw:
        parsed = dict(parsed)
        parsed["raw_activity"] = activity_raw
        if window_raw:
            parsed["raw_window"] = window_raw
    if args.json or args.include_raw:
        emit_ok(args, parsed)
    else:
        emit_ok(args, f'{parsed["package"]}/{parsed["activity"]} ({parsed["source"]})')
    return 0


def build_parser() -> argparse.ArgumentParser:
    def add_common_options(parser: argparse.ArgumentParser) -> None:
        # Add to both the top-level parser and subcommands so users can place these
        # options before or after the subcommand name.
        parser.add_argument("--adb", default=None, help="Path to adb binary (or set ADB_PATH)")
        parser.add_argument("--serial", default=None, help="Device serial (or set ANDROID_SERIAL)")
        parser.add_argument("--timeout", type=float, default=10.0, help="Default command timeout in seconds")
        parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output when supported")

    p = argparse.ArgumentParser(prog="adb_app.py")
    add_common_options(p)

    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("devices", help="List adb devices")
    add_common_options(sp)
    sp.set_defaults(func=cmd_devices)

    sp = sub.add_parser("shell", help="Run an adb shell command (args after '--')")
    add_common_options(sp)
    sp.add_argument("shell_args", nargs=argparse.REMAINDER, help="Shell args (must be after '--')")
    sp.set_defaults(func=cmd_shell)

    sp = sub.add_parser("pidof", help="Resolve PID(s) for a package via adb shell pidof")
    add_common_options(sp)
    sp.add_argument("--package", required=True)
    sp.add_argument("--all", action="store_true", help="Return all pids (default: first pid only)")
    sp.set_defaults(func=cmd_pidof)

    sp = sub.add_parser("install", help="Install an APK")
    add_common_options(sp)
    sp.add_argument("--apk", required=True, help="Path to APK")
    sp.add_argument("--no-replace", action="store_true", help="Do not pass -r (replace existing app)")
    sp.set_defaults(func=cmd_install)

    sp = sub.add_parser("uninstall", help="Uninstall a package (destructive)")
    add_common_options(sp)
    sp.add_argument("--package", required=True)
    sp.add_argument("--yes", action="store_true", help="Confirm destructive operation")
    sp.set_defaults(func=cmd_uninstall)

    sp = sub.add_parser("start", help="Start an app (monkey by default, or explicit component)")
    add_common_options(sp)
    sp.add_argument("--package", required=True)
    sp.add_argument("--activity", default=None, help="Activity name or full component (pkg/activity)")
    sp.add_argument("--wait", action="store_true", help="Wait for launch when using am start")
    sp.set_defaults(func=cmd_start)

    sp = sub.add_parser("stop", help="Force-stop an app")
    add_common_options(sp)
    sp.add_argument("--package", required=True)
    sp.set_defaults(func=cmd_stop)

    sp = sub.add_parser("clear", help="Clear app data (destructive)")
    add_common_options(sp)
    sp.add_argument("--package", required=True)
    sp.add_argument("--yes", action="store_true", help="Confirm destructive operation")
    sp.set_defaults(func=cmd_clear)

    sp = sub.add_parser("grant", help="Grant a runtime permission to a package")
    add_common_options(sp)
    sp.add_argument("--package", required=True)
    sp.add_argument("--permission", required=True)
    sp.set_defaults(func=cmd_grant)

    sp = sub.add_parser("revoke", help="Revoke a runtime permission from a package")
    add_common_options(sp)
    sp.add_argument("--package", required=True)
    sp.add_argument("--permission", required=True)
    sp.set_defaults(func=cmd_revoke)

    sp = sub.add_parser("deeplink", help="Open a deep link via am start VIEW")
    add_common_options(sp)
    sp.add_argument("--url", required=True)
    sp.add_argument("--package", default=None, help="Optional package constraint (-p)")
    sp.set_defaults(func=cmd_deeplink)

    sp = sub.add_parser("tap", help="Simulate a tap")
    add_common_options(sp)
    sp.add_argument("--x", type=int, required=True)
    sp.add_argument("--y", type=int, required=True)
    sp.set_defaults(func=cmd_tap)

    sp = sub.add_parser("swipe", help="Simulate a swipe")
    add_common_options(sp)
    sp.add_argument("--x1", type=int, required=True)
    sp.add_argument("--y1", type=int, required=True)
    sp.add_argument("--x2", type=int, required=True)
    sp.add_argument("--y2", type=int, required=True)
    sp.add_argument("--duration-ms", type=int, default=None)
    sp.set_defaults(func=cmd_swipe)

    sp = sub.add_parser("text", help="Input text")
    add_common_options(sp)
    sp.add_argument("--text", required=True)
    sp.add_argument("--raw", action="store_true", help="Do not apply conservative encoding")
    sp.set_defaults(func=cmd_text)

    sp = sub.add_parser("keyevent", help="Send a keyevent (e.g., KEYCODE_BACK)")
    add_common_options(sp)
    sp.add_argument("--key", required=True)
    sp.set_defaults(func=cmd_keyevent)

    sp = sub.add_parser("screenshot", help="Capture a screenshot to a local file")
    add_common_options(sp)
    sp.add_argument("--out", required=True)
    sp.set_defaults(func=cmd_screenshot)

    sp = sub.add_parser("screenrecord", help="Record screen to a local file (<= 180s)")
    add_common_options(sp)
    sp.add_argument("--out", required=True)
    sp.add_argument("--seconds", type=int, required=True)
    sp.set_defaults(func=cmd_screenrecord)

    sp = sub.add_parser("uidump", help="Dump UI hierarchy XML to a local file")
    add_common_options(sp)
    sp.add_argument("--out", required=True)
    sp.set_defaults(func=cmd_uidump)

    sp = sub.add_parser("logcat-dump", help="Dump logcat and exit (bounded)")
    add_common_options(sp)
    sp.add_argument("--package", default=None, help="Filter by package PID (best-effort)")
    sp.add_argument("--pid", type=int, default=None, help="Filter by PID")
    sp.add_argument("--allow-missing-pid", action="store_true", help="If --package PID not found, do not fail")
    sp.add_argument("--buffer", default=None, help="logcat buffer (e.g., main, system, crash)")
    sp.add_argument("--since", default=None, help="Pass-through for logcat -T (e.g., 2m, 10s)")
    sp.add_argument("--format", default="time", help="logcat -v format (default: time)")
    sp.add_argument("--clear", action="store_true", help="Clear logcat buffer before capture")
    sp.add_argument("--max-lines", type=int, default=None, help="Keep only the last N lines")
    sp.add_argument("--out", default=None, help="Write output to a file instead of stdout")
    sp.set_defaults(func=cmd_logcat_dump)

    sp = sub.add_parser("logcat-follow", help="Follow logcat for N seconds (bounded)")
    add_common_options(sp)
    sp.add_argument("--seconds", type=int, required=True, help="How long to follow before terminating")
    sp.add_argument("--package", default=None, help="Filter by package PID (best-effort)")
    sp.add_argument("--pid", type=int, default=None, help="Filter by PID")
    sp.add_argument("--allow-missing-pid", action="store_true", help="If --package PID not found, do not fail")
    sp.add_argument("--buffer", default=None, help="logcat buffer (e.g., main, system, crash)")
    sp.add_argument("--since", default=None, help="Pass-through for logcat -T (e.g., 2m, 10s)")
    sp.add_argument("--format", default="time", help="logcat -v format (default: time)")
    sp.add_argument("--clear", action="store_true", help="Clear logcat buffer before capture")
    sp.add_argument("--max-lines", type=int, default=None, help="Keep only the last N lines")
    sp.add_argument("--out", default=None, help="Write output to a file instead of stdout")
    sp.set_defaults(func=cmd_logcat_follow)

    sp = sub.add_parser("meminfo", help="Run dumpsys meminfo for a package")
    add_common_options(sp)
    sp.add_argument("--package", required=True)
    sp.set_defaults(func=cmd_meminfo)

    sp = sub.add_parser("cpuinfo", help="Run dumpsys cpuinfo")
    add_common_options(sp)
    sp.set_defaults(func=cmd_cpuinfo)

    sp = sub.add_parser("current-activity", help="Best-effort parse of current resumed activity")
    add_common_options(sp)
    sp.add_argument("--include-raw", action="store_true", help="Include raw dumpsys output (large)")
    sp.set_defaults(func=cmd_current_activity)

    return p


def main(argv: List[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except UsageError as e:
        emit_error(args, f"Usage error: {e}", code=2)
        return 2
    except AdbCommandError as e:
        emit_error(args, str(e), code=1)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

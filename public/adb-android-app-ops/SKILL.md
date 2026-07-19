---
name: adb-android-app-ops
description: "Operate and monitor Android apps/devices via adb (Android Debug Bridge): list/select devices, install/uninstall APKs, start/stop/clear apps, send intents/deep links, simulate input (tap/swipe/text/keyevent), capture screenshots/screen recordings, dump UI hierarchy, and collect diagnostics (logcat crash/ANR, dumpsys meminfo/cpu/activity). Use when a task needs adb commands or repeatable adb automation from the terminal."
---

# Adb Android App Ops

## Overview

Use adb to monitor and control Android apps from the terminal, with a preference for bounded, non-hanging commands.
Use the bundled `scripts/adb_app.py` wrapper for repeatable operations and optional JSON output.

## Quick Start

List connected devices:

```bash
python3 scripts/adb_app.py devices
python3 scripts/adb_app.py devices --json
```

Select a device (recommended whenever more than one device/emulator is attached):

```bash
export ANDROID_SERIAL="emulator-5554"
python3 scripts/adb_app.py --serial "emulator-5554" current-activity
```

Find the app package name (raw adb, since this depends on your naming convention):

```bash
adb shell pm list packages | rg -i "keyword"
```

Launch, collect logs, and capture artifacts:

```bash
python3 scripts/adb_app.py start --package "com.example.app"
python3 scripts/adb_app.py logcat-dump --package "com.example.app" --since 2m
python3 scripts/adb_app.py logcat-dump --buffer crash --since 10m
python3 scripts/adb_app.py screenshot --out "./screenshot.png"
python3 scripts/adb_app.py uidump --out "./uidump.xml"
```

## Monitoring / Diagnostics

Prefer bounded commands that return (avoid indefinite `adb logcat` streams):

```bash
python3 scripts/adb_app.py logcat-follow --seconds 15 --package "com.example.app"
python3 scripts/adb_app.py meminfo --package "com.example.app"
python3 scripts/adb_app.py cpuinfo
python3 scripts/adb_app.py current-activity
```

## App Control

App lifecycle:

```bash
python3 scripts/adb_app.py stop --package "com.example.app"
python3 scripts/adb_app.py clear --package "com.example.app" --yes
```

Deep links / intents:

```bash
python3 scripts/adb_app.py deeplink --url "myapp://path?x=1" --package "com.example.app"
```

Input simulation:

```bash
python3 scripts/adb_app.py tap --x 300 --y 800
python3 scripts/adb_app.py swipe --x1 100 --y1 800 --x2 100 --y2 200 --duration-ms 250
python3 scripts/adb_app.py text --text "hello world"
python3 scripts/adb_app.py keyevent --key "KEYCODE_BACK"
```

## Troubleshooting (adb)

If a device shows up as `unauthorized`, re-approve USB debugging on the device/emulator.

Restart adb server:

```bash
adb kill-server
adb start-server
```

If multiple devices/emulators are attached, always set `--serial` or `ANDROID_SERIAL` to avoid acting on the wrong device.

## References

- `references/adb-cheatsheet.md`

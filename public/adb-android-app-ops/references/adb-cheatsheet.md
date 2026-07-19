# ADB Cheatsheet (Android App Ops)

## Device selection (serial)

List devices:

```bash
adb devices -l
```

If more than one device/emulator is attached, prefer explicit selection:

```bash
export ANDROID_SERIAL="emulator-5554"
adb -s "emulator-5554" shell getprop ro.product.model
```

## Discover package name

List packages:

```bash
adb shell pm list packages
adb shell pm list packages | rg -i "keyword"
```

List installed packages matching a prefix:

```bash
adb shell pm list packages "com.example*"
```

## Launch / stop / clear (destructive)

Launch via launcher category:

```bash
adb shell monkey -p "com.example.app" -c android.intent.category.LAUNCHER 1
```

Force stop:

```bash
adb shell am force-stop "com.example.app"
```

Clear app data (destructive):

```bash
adb shell pm clear "com.example.app"
```

## Intents and deep links

Open a deep link:

```bash
adb shell am start -a android.intent.action.VIEW -d "myapp://path?x=1" -p "com.example.app"
```

## Logcat (bounded)

Dump recent logs:

```bash
adb logcat -d -v time -T 2m
```

Crash buffer:

```bash
adb logcat -d -b crash -v time -T 10m
```

Filter by PID (if supported by your adb/logcat):

```bash
adb logcat -d --pid=12345 -v time -T 2m
```

Find PID by package:

```bash
adb shell pidof "com.example.app"
```

## dumpsys snapshots

Current resumed activity (varies by Android version/OEM):

```bash
adb shell dumpsys activity activities
adb shell dumpsys window windows
```

Memory info:

```bash
adb shell dumpsys meminfo "com.example.app"
```

CPU info:

```bash
adb shell dumpsys cpuinfo
```

## UI hierarchy dump

Dump UI tree (writes an XML on device, then pull it):

```bash
adb shell uiautomator dump /sdcard/uidump.xml
adb pull /sdcard/uidump.xml ./uidump.xml
```

## Screenshots and recordings

Screenshot (PNG):

```bash
adb exec-out screencap -p > screenshot.png
```

Screen record (MP4):

```bash
adb shell screenrecord --time-limit 10 /sdcard/record.mp4
adb pull /sdcard/record.mp4 ./record.mp4
adb shell rm -f /sdcard/record.mp4
```

## Input simulation

Tap / swipe:

```bash
adb shell input tap 300 800
adb shell input swipe 100 800 100 200 250
```

Text input (space often needs special handling):

```bash
adb shell input text "hello%sworld"
```

Key events:

```bash
adb shell input keyevent KEYCODE_BACK
adb shell input keyevent KEYCODE_HOME
```

## Install / uninstall

Install:

```bash
adb install -r ./app-debug.apk
```

Uninstall:

```bash
adb uninstall "com.example.app"
```

## Troubleshooting

If a device is `unauthorized`, re-approve USB debugging and run:

```bash
adb kill-server
adb start-server
adb devices -l
```

If adb cannot see your physical device:

```bash
adb usb
adb devices -l
```


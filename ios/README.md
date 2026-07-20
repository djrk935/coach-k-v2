# Coach K for iOS

Native SwiftUI app (iOS 17+) over the same FastAPI backend. v1 scope: the
daily loop — Today's Workout with one-tap + voice set logging, streaming
chat with Coach K, settings, and a local morning check-in notification.

## Working on it

```bash
brew install xcodegen          # once
cd ios
xcodegen generate              # regenerates CoachK.xcodeproj from project.yml
open CoachK.xcodeproj          # then ⌘R on a simulator
```

The project file is generated — edit `project.yml`, not the xcodeproj.
Add new Swift files under `CoachK/` and rerun `xcodegen generate`.

If `xcodebuild` complains about Command Line Tools, either run
`sudo xcode-select -s /Applications/Xcode.app/Contents/Developer` once, or
prefix commands with `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`.

## CLI build + run (no Xcode UI)

```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
xcodebuild -project CoachK.xcodeproj -scheme CoachK \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  -derivedDataPath build build CODE_SIGNING_ALLOWED=NO
xcrun simctl boot "iPhone 17 Pro" || true
xcrun simctl install booted build/Build/Products/Debug-iphonesimulator/CoachK.app
xcrun simctl launch booted com.dayan.coachk
```

## Pointing at the backend

Defaults to `http://localhost:8000` (works in the simulator — it shares the
Mac's network). On a real device, set the server URL in Settings to your
Mac's LAN IP (`http://192.168.x.x:8000`) or the deployed HTTPS URL, plus the
app password if one is set. Real devices also need a paid-free Apple ID
"personal team" signature: open Xcode → Signing & Capabilities → pick your
team, then run to device.

## Phase 2 (on-device features, in priority order)

1. HealthKit read (sleep, HRV, resting HR) → auto-post readiness each morning
2. Home-screen widget: today's session at a glance (WidgetKit)
3. Live Activity rest timer between sets
4. Siri / App Intents: "log bench 225 for 5" without opening the app
5. APNs remote push (requires paid Apple Developer account) — replaces the
   local-notification nudge with the server's real proactive coaching

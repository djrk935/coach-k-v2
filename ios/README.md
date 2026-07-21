# Coach K for iOS

Native SwiftUI app (iOS 17+) over the same FastAPI backend.

## Tabs

| Tab | Features |
|-----|----------|
| **Today** | Workout logging, voice log, HealthKit readiness, check-in gate, soft-day adaptation, catch-up, exercise swaps, form cues, session debrief + share |
| **Chat** | Streaming Coach K chat |
| **Stats** | Progress (e1RM, ACWR, PRs) + share |
| **Week** | Mesocycle calendar + rest/travel/game markers |
| **Settings** | Server URL, app key, HealthKit, local morning reminder |

## Working on it

```bash
brew install xcodegen          # once
cd ios
xcodegen generate              # regenerates CoachK.xcodeproj from project.yml
open CoachK.xcodeproj          # then ⌘R on a simulator
```

The project file is generated — edit `project.yml`, not the xcodeproj.
Add new Swift files under `CoachK/` and rerun `xcodegen generate`.

## Pointing at the backend

Defaults to `http://localhost:8000` (simulator shares the Mac network). On a
real device, set the server URL in Settings to your Mac's LAN IP or the
deployed HTTPS URL, plus the app password if one is set.

## Still web-first / next

- Video form check, injury protocol cards, templates activate, PWA landing
- APNs remote push (paid Apple Developer) — web Push already works
- WidgetKit / Live Activity rest timer / Siri App Intents

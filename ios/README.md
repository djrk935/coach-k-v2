# Coach K for iOS

Native SwiftUI app (iOS 17+) over the same FastAPI backend.

## Tabs

| Tab | Features |
|-----|----------|
| **Today** | Logging, voice, HealthKit, check-in, adaptation, catch-up, swaps, injury protocols, video form check, debrief + share |
| **Chat** | Streaming Coach K chat |
| **Stats** | Progress (e1RM, ACWR, PRs) + share |
| **Week** | Mesocycle calendar + rest/travel/game markers |
| **Settings** | Server URL, app key, HealthKit, local reminder, APNs register |

## Working on it

```bash
brew install xcodegen
cd ios && xcodegen generate && open CoachK.xcodeproj
```

## Remote push (APNs)

1. Paid Apple Developer team + Push Notifications capability in Xcode
2. Create an APNs Auth Key (.p8) in the Apple developer portal
3. Set on the server: `APNS_KEY_ID`, `APNS_TEAM_ID`, `APNS_AUTH_KEY` (PEM or path), `APNS_BUNDLE_ID=com.dayan.coachk`
4. In the app: Settings → **Enable remote push (APNs)** (real device required for a token)

Simulator can still use the local 8:00 reminder.

## Pointing at the backend

Defaults to `http://localhost:8000`. On a device, set your LAN IP or HTTPS App Platform URL + `APP_PASSWORD`.

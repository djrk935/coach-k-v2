import SwiftUI
import UserNotifications

struct SettingsView: View {
    @AppStorage("baseURL") private var baseURL = "http://localhost:8000"
    @AppStorage("appKey") private var appKey = ""
    @AppStorage("dailyReminder") private var dailyReminder = false
    @AppStorage("healthConnected") private var healthConnected = false
    @State private var status = ""
    @State private var healthStatus = ""

    var body: some View {
        NavigationStack {
            Form {
                Section("Server") {
                    TextField("http://your-server", text: $baseURL)
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                        .keyboardType(.URL)
                    SecureField("App password (if set)", text: $appKey)
                    Button("Test Connection") {
                        Task {
                            do {
                                if appKey.isEmpty {
                                    let _: OkResult = try await API.get("/api/health")
                                    status = "✅ Server reachable (set app password if the API is locked)"
                                } else {
                                    let _: [ChatMeta] = try await API.get("/api/chats")
                                    status = "✅ Connected — password accepted"
                                }
                            } catch {
                                status = "⚠ \(error.localizedDescription)"
                            }
                        }
                    }
                    if !status.isEmpty {
                        Text(status).font(.caption).foregroundStyle(Color.mut)
                    }
                } footer: {
                    Text("Production: use your App Platform HTTPS URL (https://….ondigitalocean.app) and the same APP_PASSWORD you set on the server.")
                }

                Section {
                    Button(healthConnected ? "Re-sync Apple Health" : "Connect Apple Health") {
                        Task {
                            let ok = await HealthKitManager.shared.requestAuthorization()
                            healthConnected = ok
                            if ok {
                                let result = await HealthKitManager.shared.sync()
                                healthStatus = result == nil
                                    ? "Connected — no recovery data yet (needs an Apple Watch night)."
                                    : "Synced. Readiness score updated on Today."
                            } else {
                                healthStatus = "Health access denied — enable it in Settings › Health."
                            }
                        }
                    }
                    if !healthStatus.isEmpty {
                        Text(healthStatus).font(.caption).foregroundStyle(Color.mut)
                    }
                } header: {
                    Text("Apple Health")
                } footer: {
                    Text("Coach K reads last night's sleep, HRV, and resting heart rate to score your recovery and adjust training.")
                }

                Section {
                    Toggle("Morning check-in (8:00)", isOn: $dailyReminder)
                        .onChange(of: dailyReminder) { _, on in
                            Task { await Reminders.setDaily(enabled: on) }
                        }
                } header: {
                    Text("Coaching nudges")
                } footer: {
                    Text("A local reminder to log readiness and see today's session. No server required.")
                }

                Section("About") {
                    LabeledContent("App", value: "Coach K for iOS")
                    LabeledContent("Backend", value: baseURL)
                }
            }
            .scrollContentBackground(.hidden)
            .background(Color.ink)
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

enum Reminders {
    static func setDaily(enabled: Bool) async {
        let center = UNUserNotificationCenter.current()
        center.removePendingNotificationRequests(withIdentifiers: ["daily-checkin"])
        guard enabled else { return }
        let granted = (try? await center.requestAuthorization(options: [.alert, .sound, .badge])) ?? false
        guard granted else { return }

        let content = UNMutableNotificationContent()
        content.title = "Coach K"
        content.body = "Morning check-in: how'd you sleep? Today's session is loaded."
        content.sound = .default

        var date = DateComponents()
        date.hour = 8
        let trigger = UNCalendarNotificationTrigger(dateMatching: date, repeats: true)
        try? await center.add(
            UNNotificationRequest(identifier: "daily-checkin", content: content, trigger: trigger)
        )
    }
}

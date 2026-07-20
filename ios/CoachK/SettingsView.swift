import SwiftUI
import UserNotifications

struct SettingsView: View {
    @AppStorage("baseURL") private var baseURL = "http://localhost:8000"
    @AppStorage("appKey") private var appKey = ""
    @AppStorage("dailyReminder") private var dailyReminder = false
    @State private var status = ""

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
                                let _: OkResult = try await API.get("/api/health")
                                status = "✅ Connected"
                            } catch {
                                status = "⚠ \(error.localizedDescription)"
                            }
                        }
                    }
                    if !status.isEmpty {
                        Text(status).font(.caption).foregroundStyle(Color.mut)
                    }
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

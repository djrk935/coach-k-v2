import SwiftUI
import UIKit
import UserNotifications

final class AppDelegate: NSObject, UIApplicationDelegate, UNUserNotificationCenterDelegate {
    static var shared: AppDelegate?

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil
    ) -> Bool {
        Self.shared = self
        UNUserNotificationCenter.current().delegate = self
        return true
    }

    func application(
        _ application: UIApplication,
        didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
    ) {
        let hex = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
        UserDefaults.standard.set(hex, forKey: "apnsDeviceToken")
        NotificationCenter.default.post(name: .apnsTokenUpdated, object: hex)
        Task { await PushRegistration.upload(token: hex) }
    }

    func application(
        _ application: UIApplication,
        didFailToRegisterForRemoteNotificationsWithError error: Error
    ) {
        NotificationCenter.default.post(
            name: .apnsRegistrationFailed,
            object: error.localizedDescription
        )
    }
}

extension Notification.Name {
    static let apnsTokenUpdated = Notification.Name("apnsTokenUpdated")
    static let apnsRegistrationFailed = Notification.Name("apnsRegistrationFailed")
}

enum PushRegistration {
    static func requestAndRegister() async -> String {
        let center = UNUserNotificationCenter.current()
        let granted = (try? await center.requestAuthorization(options: [.alert, .sound, .badge])) ?? false
        guard granted else { return "Notifications denied — enable in iOS Settings." }
        await MainActor.run {
            UIApplication.shared.registerForRemoteNotifications()
        }
        if let existing = UserDefaults.standard.string(forKey: "apnsDeviceToken"), !existing.isEmpty {
            await upload(token: existing)
            return "Remote push enabled — token registered."
        }
        return "Permission granted — waiting for device token (needs a real device + APNs capability)."
    }

    static func upload(token: String) async {
        #if DEBUG
        let sandbox = true
        #else
        let sandbox = false
        #endif
        do {
            let _: OkResult = try await API.post(
                "/api/push/apns/register",
                body: ApnsRegisterBody(deviceToken: token, sandbox: sandbox)
            )
        } catch {
            // Server may not have APNs keys yet — token is still stored when API is up.
        }
    }
}

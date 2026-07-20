import SwiftUI

@main
struct CoachKApp: App {
    @State private var selectedTab = 0

    var body: some Scene {
        WindowGroup {
            TabView(selection: $selectedTab) {
                TodayView(selectedTab: $selectedTab)
                    .tabItem { Label("Today", systemImage: "flame.fill") }
                    .tag(0)
                ChatView()
                    .tabItem { Label("Chat", systemImage: "bubble.left.and.bubble.right.fill") }
                    .tag(1)
                SettingsView()
                    .tabItem { Label("Settings", systemImage: "gearshape.fill") }
                    .tag(2)
            }
            .tint(.brand)
            .preferredColorScheme(.dark)
        }
    }
}

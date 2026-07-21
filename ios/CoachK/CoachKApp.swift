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
                StatsView()
                    .tabItem { Label("Stats", systemImage: "chart.line.uptrend.xyaxis") }
                    .tag(2)
                WeekCalendarView()
                    .tabItem { Label("Week", systemImage: "calendar") }
                    .tag(3)
                SettingsView()
                    .tabItem { Label("Settings", systemImage: "gearshape.fill") }
                    .tag(4)
            }
            .tint(.brand)
            .preferredColorScheme(.dark)
        }
    }
}

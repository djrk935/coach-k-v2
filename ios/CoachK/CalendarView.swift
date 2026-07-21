import SwiftUI

@MainActor
@Observable
final class CalendarModel {
    var data: CalendarData?
    var weeks = 2
    var loading = true
    var error: String?
    var selected: CalendarDay?

    func load() async {
        loading = true
        do {
            data = try await API.get("/api/calendar?weeks=\(weeks)") as CalendarData
            error = nil
        } catch {
            self.error = error.localizedDescription
        }
        loading = false
    }

    func setMarker(kind: String?) async {
        guard let day = selected else { return }
        do {
            let _: OkResult = try await API.post(
                "/api/calendar/marker",
                body: CalendarMarkerBody(date: day.date, kind: kind, note: nil)
            )
            selected = nil
            await load()
        } catch {
            self.error = error.localizedDescription
        }
    }
}

struct WeekCalendarView: View {
    @State private var model = CalendarModel()

    var body: some View {
        NavigationStack {
            ZStack {
                Color.ink.ignoresSafeArea()
                content
            }
            .navigationTitle("Week")
            .navigationBarTitleDisplayMode(.inline)
            .sheet(item: $model.selected) { day in
                DaySheet(day: day, model: model)
                    .presentationDetents([.medium])
            }
        }
        .task { await model.load() }
        .onChange(of: model.weeks) { _, _ in
            Task { await model.load() }
        }
    }

    @ViewBuilder private var content: some View {
        if model.loading && model.data == nil {
            ProgressView().tint(.brand)
        } else if let err = model.error, model.data == nil {
            Text(err).foregroundStyle(Color.mut).padding()
        } else if let data = model.data {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    if let prog = data.program {
                        Text("\(prog.name ?? "Program") · \(prog.daysPerWeek ?? 0) days/wk")
                            .font(.subheadline)
                            .foregroundStyle(Color.mut)
                    } else {
                        Text("No active program — mark rest/travel anyway.")
                            .font(.subheadline)
                            .foregroundStyle(Color.mut)
                    }

                    Picker("Weeks", selection: $model.weeks) {
                        Text("1w").tag(1)
                        Text("2w").tag(2)
                        Text("4w").tag(4)
                    }
                    .pickerStyle(.segmented)

                    let weeks = stride(from: 0, to: data.days.count, by: 7).map { i in
                        Array(data.days[i..<min(i + 7, data.days.count)])
                    }

                    ForEach(Array(weeks.enumerated()), id: \.offset) { _, week in
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Week of \(week.first?.date ?? "")")
                                .font(.caption.bold())
                                .foregroundStyle(Color.mut)
                                .textCase(.uppercase)
                            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 6), count: 7), spacing: 6) {
                                ForEach(week) { day in
                                    Button {
                                        model.selected = day
                                    } label: {
                                        VStack(alignment: .leading, spacing: 4) {
                                            HStack {
                                                Text(day.weekday).font(.system(size: 9)).foregroundStyle(Color.mut)
                                                Spacer()
                                                Text(String(day.date.suffix(2)))
                                                    .font(.system(size: 10, weight: day.isToday ? .bold : .regular))
                                                    .foregroundStyle(day.isToday ? Color.brand : Color.mut)
                                            }
                                            Text(dayTitle(day))
                                                .font(.system(size: 10, weight: .semibold))
                                                .foregroundStyle(.white)
                                                .lineLimit(2)
                                                .multilineTextAlignment(.leading)
                                            if day.completed {
                                                Text("Done").font(.system(size: 9)).foregroundStyle(.green)
                                            }
                                        }
                                        .padding(6)
                                        .frame(minHeight: 72, alignment: .topLeading)
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                        .background(dayColor(day.kind), in: RoundedRectangle(cornerRadius: 10))
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 10)
                                                .stroke(day.isToday ? Color.brand : Color.line, lineWidth: day.isToday ? 1.5 : 1)
                                        )
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                        }
                    }
                }
                .padding()
            }
        }
    }

    private func dayTitle(_ day: CalendarDay) -> String {
        if let label = day.training?.dayLabel, !label.isEmpty {
            return label.replacingOccurrences(of: #"^Day\s*\d+\s*[—–-]?\s*"#, with: "", options: .regularExpression)
        }
        switch day.kind {
        case "rest": return "Rest"
        case "travel": return "Travel"
        case "game": return "Game"
        case "missed": return "Missed"
        case "completed": return "Logged"
        case "training": return "Train"
        default: return "—"
        }
    }

    private func dayColor(_ kind: String) -> Color {
        switch kind {
        case "training": return Color.brand.opacity(0.15)
        case "rest": return Color.panel.opacity(0.6)
        case "travel": return Color.cyan.opacity(0.12)
        case "game": return Color.orange.opacity(0.15)
        case "missed": return Color.ink.opacity(0.5)
        case "completed": return Color.green.opacity(0.12)
        default: return Color.clear
        }
    }
}

private struct DaySheet: View {
    let day: CalendarDay
    let model: CalendarModel

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("\(day.weekday) · \(day.date)")
                .font(.caption.bold())
                .foregroundStyle(Color.mut)
                .textCase(.uppercase)
            Text(day.training?.dayLabel ?? day.kind.capitalized)
                .font(.title3.bold())
                .foregroundStyle(.white)
            if let focus = day.training?.focus {
                Text(focus).font(.subheadline).foregroundStyle(Color.mut)
            }
            Text("Mark this day").font(.caption.bold()).foregroundStyle(Color.mut).textCase(.uppercase)
            HStack(spacing: 8) {
                ForEach([("rest", "Rest"), ("travel", "Travel"), ("game", "Game")], id: \.0) { kind, label in
                    Button(label) {
                        Task { await model.setMarker(kind: kind) }
                    }
                    .font(.caption.bold())
                    .padding(.horizontal, 12).padding(.vertical, 8)
                    .background(Color.panel, in: Capsule())
                    .foregroundStyle(.white)
                }
                Button("Clear") {
                    Task { await model.setMarker(kind: nil) }
                }
                .font(.caption.bold())
                .foregroundStyle(Color.mut)
            }
            Spacer()
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.ink)
    }
}

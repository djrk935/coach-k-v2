import SwiftUI
import Charts

@MainActor
@Observable
final class ProgressModel {
    var data: ProgressData?
    var days = 90
    var loading = true
    var error: String?
    var shareText = ""
    var showShare = false

    func load() async {
        loading = true
        do {
            data = try await API.get("/api/progress?days=\(days)") as ProgressData
            error = nil
        } catch {
            self.error = error.localizedDescription
        }
        loading = false
    }

    func share() {
        guard let data else { return }
        shareText = ShareText.progress(data)
        showShare = true
    }
}

struct StatsView: View {
    @State private var model = ProgressModel()

    var body: some View {
        NavigationStack {
            ZStack {
                Color.ink.ignoresSafeArea()
                content
            }
            .navigationTitle("Stats")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Share") { model.share() }
                        .disabled(model.data == nil)
                        .foregroundStyle(Color.brand)
                }
            }
            .sheet(isPresented: $model.showShare) {
                ShareSheet(items: [model.shareText])
            }
        }
        .task { await model.load() }
        .onChange(of: model.days) { _, _ in
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
                    Picker("Window", selection: $model.days) {
                        Text("30d").tag(30)
                        Text("90d").tag(90)
                        Text("180d").tag(180)
                    }
                    .pickerStyle(.segmented)

                    Text("\(data.sessions) sessions · last \(data.days) days")
                        .font(.subheadline)
                        .foregroundStyle(Color.mut)

                    if let acwr = data.loadSummary?.acwr {
                        statCard(
                            title: "ACWR",
                            value: String(format: "%.2f", acwr),
                            hint: "Training load ratio"
                        )
                    }

                    ForEach(Array(data.lifts.keys.sorted()), id: \.self) { key in
                        if let L = data.lifts[key] {
                            VStack(alignment: .leading, spacing: 8) {
                                HStack {
                                    Text(key.capitalized)
                                        .font(.caption.bold())
                                        .foregroundStyle(Color.mut)
                                        .textCase(.uppercase)
                                    Spacer()
                                    Text(String(format: "%.0f lbs", L.current))
                                        .font(.title3.bold())
                                        .foregroundStyle(.white)
                                }
                                Text(String(format: "%@%.0f lbs (%.1f%%)", L.delta >= 0 ? "+" : "", L.delta, L.deltaPct))
                                    .font(.caption)
                                    .foregroundStyle(L.delta >= 0 ? Color.green : Color.brand)

                                if L.points.count >= 2 {
                                    Chart(L.points, id: \.date) { p in
                                        LineMark(
                                            x: .value("Date", p.date),
                                            y: .value("e1RM", p.e1rm)
                                        )
                                        .foregroundStyle(Color.brand)
                                    }
                                    .chartXAxis(.hidden)
                                    .frame(height: 72)
                                }
                            }
                            .padding(14)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(Color.panel, in: RoundedRectangle(cornerRadius: 14))
                        }
                    }

                    if let prs = data.prs, !prs.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Recent PRs")
                                .font(.caption.bold())
                                .foregroundStyle(Color.mut)
                                .textCase(.uppercase)
                            ForEach(prs.prefix(8)) { p in
                                HStack {
                                    Text(p.exercise).foregroundStyle(.white)
                                    Spacer()
                                    Text("\(p.weightLbs.map { String(Int($0)) } ?? "—")×\(p.reps.map(String.init) ?? "—")")
                                        .foregroundStyle(Color.mut)
                                    Text(p.date).font(.caption2).foregroundStyle(Color.mut)
                                }
                                .font(.footnote)
                            }
                        }
                        .padding(14)
                        .background(Color.panel, in: RoundedRectangle(cornerRadius: 14))
                    }
                }
                .padding()
            }
        } else {
            Text("Log sessions to unlock your chart.")
                .foregroundStyle(Color.mut)
                .padding()
        }
    }

    private func statCard(title: String, value: String, hint: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title).font(.caption.bold()).foregroundStyle(Color.mut).textCase(.uppercase)
            Text(value).font(.title.bold()).foregroundStyle(.white)
            Text(hint).font(.caption).foregroundStyle(Color.mut)
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.panel, in: RoundedRectangle(cornerRadius: 14))
    }
}

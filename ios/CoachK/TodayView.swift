import SwiftUI

@MainActor
@Observable
final class TodayModel {
    var plan: TodayPlan?
    var loading = true
    var error: String?
    var finished = false
    var lastHeard = ""
    let voice = VoiceLogger()

    func load() async {
        do {
            plan = try await API.get("/api/today") as TodayPlan
            error = nil
        } catch {
            self.error = error.localizedDescription
        }
        loading = false
    }

    func logSet(slot: Int, exercise: String, weight: Double?, reps: Int?) async -> Bool {
        guard let plan, let pid = plan.programId, let day = plan.dayIndex else { return false }
        do {
            let result: LogSetResult = try await API.post(
                "/api/today/log-set",
                body: LogSetBody(
                    programId: pid, dayIndex: day, slotIndex: slot,
                    exercise: exercise, weightLbs: weight, reps: reps, rir: nil
                )
            )
            await load()
            return result.isPr
        } catch {
            self.error = error.localizedDescription
            return false
        }
    }

    func logVoice(_ text: String) async {
        guard let plan, let pid = plan.programId, let day = plan.dayIndex,
              let exercises = plan.exercises else { return }
        lastHeard = "🎤 \"\(text)\""
        do {
            let result: VoiceLogResult = try await API.post(
                "/api/today/log-voice",
                body: VoiceLogBody(
                    text: text, programId: pid, dayIndex: day,
                    exerciseNames: exercises.map(\.exercise)
                )
            )
            if result.matched {
                await load()
                if result.isPr == true { Haptics.pr() }
            } else {
                lastHeard = "Couldn't match \"\(text)\" to today's exercises."
            }
        } catch {
            lastHeard = "⚠ \(error.localizedDescription)"
        }
    }

    func finish() async {
        guard let plan, let pid = plan.programId, let day = plan.dayIndex else { return }
        do {
            let _: OkResult = try await API.post(
                "/api/today/finish", body: FinishBody(programId: pid, dayIndex: day, sessionRpe: nil)
            )
            finished = true
        } catch {
            self.error = error.localizedDescription
        }
    }
}

enum Haptics {
    static func pr() {
        UINotificationFeedbackGenerator().notificationOccurred(.success)
    }
    static func tap() {
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
    }
}

struct TodayView: View {
    @State private var model = TodayModel()
    @Binding var selectedTab: Int

    var body: some View {
        NavigationStack {
            ZStack {
                Color.ink.ignoresSafeArea()
                content
            }
            .navigationTitle(model.plan?.dayLabel ?? "Today")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) { micButton }
            }
        }
        .task { await model.load() }
    }

    @ViewBuilder private var content: some View {
        if model.loading {
            ProgressView().tint(.brand)
        } else if model.finished {
            finishedState
        } else if let plan = model.plan, plan.active, let exercises = plan.exercises {
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    if let focus = plan.focus {
                        Text(focus).font(.subheadline).foregroundStyle(Color.mut)
                    }
                    if !model.lastHeard.isEmpty {
                        Text(model.lastHeard).font(.caption).foregroundStyle(Color.mut)
                    }
                    if let err = model.error {
                        Text("⚠ \(err)").font(.caption).foregroundStyle(Color.brand)
                    }
                    ForEach(Array(exercises.enumerated()), id: \.offset) { i, ex in
                        ExerciseCard(ex: ex, slot: i, model: model)
                    }
                    Button {
                        Task { await model.finish() }
                    } label: {
                        Text("Finish Workout")
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                            .background(Color.brand, in: RoundedRectangle(cornerRadius: 14))
                            .foregroundStyle(.white)
                    }
                    .padding(.top, 6)
                }
                .padding()
            }
        } else {
            emptyState
        }
    }

    private var micButton: some View {
        Button {
            if model.voice.isListening {
                model.voice.stop()
            } else {
                Task {
                    await model.voice.start { text in
                        Task { await model.logVoice(text) }
                    }
                }
            }
        } label: {
            Image(systemName: model.voice.isListening ? "mic.fill" : "mic")
                .foregroundStyle(model.voice.isListening ? Color.brand : Color.mut)
                .symbolEffect(.pulse, isActive: model.voice.isListening)
        }
    }

    private var finishedState: some View {
        VStack(spacing: 12) {
            Text("✅").font(.system(size: 44))
            Text("Day complete — nice work.").font(.headline).foregroundStyle(.white)
            Button("See what's next →") {
                model.finished = false
                model.loading = true
                Task { await model.load() }
            }
            .foregroundStyle(Color.brand)
        }
    }

    private var emptyState: some View {
        VStack(spacing: 10) {
            Text("No active program yet.").font(.headline).foregroundStyle(.white)
            Text("Ask Coach K to build one in Chat.")
                .font(.subheadline).foregroundStyle(Color.mut)
            Button("Open Chat →") { selectedTab = 1 }
                .padding(.top, 4)
                .foregroundStyle(Color.brand)
        }
        .padding()
    }
}

struct ExerciseCard: View {
    let ex: TodayExercise
    let slot: Int
    let model: TodayModel

    @State private var weight: String
    @State private var reps: String
    @State private var busy = false

    init(ex: TodayExercise, slot: Int, model: TodayModel) {
        self.ex = ex
        self.slot = slot
        self.model = model
        _weight = State(initialValue: ex.suggestedWeightLbs.map { String(Int($0)) } ?? "")
        _reps = State(initialValue: ex.reps.firstMatch(of: /\d+/).map { String($0.output) } ?? "")
    }

    private var done: Int { ex.loggedSets.count }
    private var complete: Bool { done >= ex.sets }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .top, spacing: 10) {
                FlipImage(urls: ex.imageUrls)
                VStack(alignment: .leading, spacing: 2) {
                    HStack(spacing: 6) {
                        if let group = ex.supersetGroup {
                            Text(group)
                                .font(.caption2.bold())
                                .padding(.horizontal, 5).padding(.vertical, 2)
                                .background(Color.brand, in: RoundedRectangle(cornerRadius: 4))
                                .foregroundStyle(.white)
                        }
                        Text(ex.exercise).font(.headline).foregroundStyle(.white)
                        if ex.loggedSets.contains(where: \.isPr) {
                            Text("🎉").font(.caption)
                        }
                    }
                    Text("\(ex.sets) × \(ex.reps) · \(ex.intensity)")
                        .font(.caption).foregroundStyle(Color.mut)
                    if let notes = ex.notes {
                        Text(notes).font(.caption2).foregroundStyle(Color.mut).lineLimit(2)
                    }
                }
                Spacer()
                Text("\(done)/\(ex.sets)")
                    .font(.caption.bold())
                    .foregroundStyle(complete ? Color.green : Color.mut)
            }

            if !ex.loggedSets.isEmpty {
                HStack(spacing: 6) {
                    ForEach(ex.loggedSets, id: \.setIndex) { s in
                        Text("\(s.weightLbs.map { String(Int($0)) } ?? "—")×\(s.reps.map(String.init) ?? "—")")
                            .font(.caption2)
                            .padding(.horizontal, 8).padding(.vertical, 3)
                            .background(s.isPr ? Color.brand : Color.ink, in: Capsule())
                            .foregroundStyle(s.isPr ? .white : Color.mut)
                    }
                }
            }

            HStack(spacing: 8) {
                TextField("lbs", text: $weight)
                    .keyboardType(.decimalPad)
                    .fieldStyle()
                    .frame(width: 76)
                Text("×").foregroundStyle(Color.mut)
                TextField("reps", text: $reps)
                    .keyboardType(.numberPad)
                    .fieldStyle()
                    .frame(width: 64)
                Button {
                    busy = true
                    Haptics.tap()
                    Task {
                        let pr = await model.logSet(
                            slot: slot, exercise: ex.exercise,
                            weight: Double(weight), reps: Int(reps)
                        )
                        if pr { Haptics.pr() }
                        busy = false
                    }
                } label: {
                    Text(complete ? "✓ Done" : "Log Set")
                        .font(.subheadline.bold())
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(
                            complete ? Color.line : Color.brand,
                            in: RoundedRectangle(cornerRadius: 10)
                        )
                        .foregroundStyle(.white)
                }
                .disabled(busy || complete)
            }
        }
        .padding(12)
        .background(Color.panel, in: RoundedRectangle(cornerRadius: 14))
    }
}

struct FlipImage: View {
    let urls: [String]
    @State private var frame = 0
    private let timer = Timer.publish(every: 0.9, on: .main, in: .common).autoconnect()

    var body: some View {
        Group {
            if let path = urls[safe: frame] ?? urls.first, let url = API.imageURL(path) {
                AsyncImage(url: url) { image in
                    image.resizable().scaledToFill()
                } placeholder: {
                    Color.line
                }
                .frame(width: 44, height: 44)
                .clipShape(RoundedRectangle(cornerRadius: 8))
            } else {
                RoundedRectangle(cornerRadius: 8).fill(Color.line)
                    .frame(width: 44, height: 44)
            }
        }
        .onReceive(timer) { _ in
            if urls.count > 1 { frame = (frame + 1) % urls.count }
        }
    }
}

extension Collection {
    subscript(safe index: Index) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}

private extension View {
    func fieldStyle() -> some View {
        padding(.vertical, 8).padding(.horizontal, 10)
            .background(Color.ink, in: RoundedRectangle(cornerRadius: 10))
            .foregroundStyle(.white)
            .multilineTextAlignment(.center)
    }
}

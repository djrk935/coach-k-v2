import SwiftUI
import UniformTypeIdentifiers

@MainActor
@Observable
final class TodayModel {
    var plan: TodayPlan?
    var readiness: ReadinessToday?
    var loading = true
    var syncing = false
    var error: String?
    var finished = false
    var debrief: SessionDebrief?
    var lastHeard = ""
    var shareText = ""
    var showShare = false
    var checkinSleep = "7"
    var checkinSoreness = "3"
    var checkinStress = "3"
    let voice = VoiceLogger()

    func load() async {
        do {
            plan = try await API.get("/api/today") as TodayPlan
            error = nil
        } catch {
            self.error = error.localizedDescription
        }
        readiness = try? await API.get("/api/readiness/today") as ReadinessToday
        loading = false

        let connected = UserDefaults.standard.bool(forKey: "healthConnected")
        let lastSync = UserDefaults.standard.string(forKey: "lastHealthSync")
        if connected, lastSync != Self.todayKey {
            await syncHealth()
        }
    }

    static var todayKey: String {
        let f = DateFormatter(); f.dateFormat = "yyyy-MM-dd"
        return f.string(from: Date())
    }

    func syncHealth() async {
        guard !syncing else { return }
        syncing = true
        if let result = await HealthKitManager.shared.sync() {
            readiness = result
            UserDefaults.standard.set(Self.todayKey, forKey: "lastHealthSync")
            await load()
        }
        syncing = false
    }

    func submitCheckin() async {
        do {
            let _: OkResult = try await API.post(
                "/api/today/checkin",
                body: CheckinBody(
                    sleepH: Double(checkinSleep),
                    soreness: Int(checkinSoreness),
                    stress: Int(checkinStress)
                )
            )
            await load()
        } catch {
            self.error = error.localizedDescription
        }
    }

    func catchUp(_ action: String) async {
        guard let plan, let pid = plan.programId else { return }
        do {
            let _: OkResult = try await API.post(
                "/api/today/catch-up",
                body: CatchUpBody(programId: pid, action: action)
            )
            await load()
        } catch {
            self.error = error.localizedDescription
        }
    }

    func swap(slot: Int, to newExercise: String) async {
        guard let plan, let pid = plan.programId, let day = plan.dayIndex else { return }
        do {
            let _: OkResult = try await API.post(
                "/api/today/swap",
                body: SwapBody(programId: pid, dayIndex: day, slotIndex: slot, newExercise: newExercise)
            )
            await load()
        } catch {
            self.error = error.localizedDescription
        }
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
            let result: FinishResult = try await API.post(
                "/api/today/finish", body: FinishBody(programId: pid, dayIndex: day, sessionRpe: nil)
            )
            debrief = result.debrief
            finished = true
        } catch {
            // Older servers may return only {ok:true}
            finished = true
            self.error = error.localizedDescription
        }
    }

    func shareSession() {
        guard let plan else { return }
        shareText = ShareText.session(plan: plan, debrief: debrief)
        showShare = true
    }

    func logPain(region: String) async {
        do {
            let _: OkResult = try await API.post(
                "/api/today/pain",
                body: PainBody(region: region, severity: 5, context: nil)
            )
            await load()
        } catch {
            self.error = error.localizedDescription
        }
    }

    func applyProtocol(regionKey: String) async {
        guard let plan, let pid = plan.programId, let day = plan.dayIndex else { return }
        do {
            let _: OkResult = try await API.post(
                "/api/today/apply-protocol-swaps",
                body: ApplyProtocolBody(programId: pid, dayIndex: day, regionKey: regionKey)
            )
            await load()
        } catch {
            self.error = error.localizedDescription
        }
    }

    func formCheck(exercise: String, formCue: String?, videoURL: URL) async -> FormCheckAssessment? {
        do {
            let frames = try await FormCheckFrames.extract(from: videoURL)
            let result: FormCheckResult = try await API.post(
                "/api/form-check",
                body: FormCheckBody(
                    exercise: exercise,
                    images: frames,
                    note: nil,
                    formCue: formCue
                )
            )
            return result.assessment
        } catch {
            self.error = error.localizedDescription
            return nil
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
            .sheet(isPresented: $model.showShare) {
                ShareSheet(items: [model.shareText])
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
                    if plan.adaptation?.needsCheckin == true {
                        checkinCard
                    }
                    if let catchUp = plan.catchUp {
                        catchUpCard(catchUp)
                    }
                    if let r = model.readiness, r.readinessScore != nil || r.hrvMs != nil {
                        ReadinessBanner(readiness: r, syncing: model.syncing) {
                            Task { await model.syncHealth() }
                        }
                    }
                    if let adapt = plan.adaptation, adapt.needsCheckin != true {
                        adaptationBanner(adapt)
                    }
                    if let protocols = plan.injuryProtocols, !protocols.isEmpty {
                        ForEach(protocols) { p in
                            InjuryProtocolCard(item: p) {
                                Task { await model.applyProtocol(regionKey: p.regionKey) }
                            }
                        }
                    }
                    PainReportRow(options: plan.painRegionOptions ?? []) { key in
                        Task { await model.logPain(region: key) }
                    }
                    if let focus = plan.focus {
                        Text(focus).font(.subheadline).foregroundStyle(Color.mut)
                    }
                    if let mode = plan.goalMode {
                        Text("\(mode) mode")
                            .font(.caption.bold())
                            .foregroundStyle(Color.brand)
                            .textCase(.uppercase)
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

    private var checkinCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Check-in").font(.caption.bold()).foregroundStyle(Color.brand).textCase(.uppercase)
            Text("Quick readiness before you train — Coach K adapts the day.")
                .font(.caption).foregroundStyle(Color.mut)
            HStack(spacing: 8) {
                field("Sleep (h)", $model.checkinSleep)
                field("Soreness", $model.checkinSoreness)
                field("Stress", $model.checkinStress)
            }
            Button {
                Task { await model.submitCheckin() }
            } label: {
                Text("Set today's plan")
                    .font(.subheadline.bold())
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                    .background(Color.brand, in: RoundedRectangle(cornerRadius: 10))
                    .foregroundStyle(.white)
            }
        }
        .padding(14)
        .background(Color.panel, in: RoundedRectangle(cornerRadius: 14))
        .overlay(RoundedRectangle(cornerRadius: 14).stroke(Color.brand.opacity(0.4), lineWidth: 1))
    }

    private func field(_ label: String, _ value: Binding<String>) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label).font(.system(size: 9)).foregroundStyle(Color.mut)
            TextField("", text: value)
                .keyboardType(.decimalPad)
                .multilineTextAlignment(.center)
                .padding(8)
                .background(Color.ink, in: RoundedRectangle(cornerRadius: 8))
                .foregroundStyle(.white)
        }
    }

    private func catchUpCard(_ info: CatchUpInfo) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(info.message).font(.subheadline).foregroundStyle(.white)
            HStack(spacing: 8) {
                ForEach([("resume", "Resume"), ("repeat_last", "Repeat"), ("light_makeup", "Light")], id: \.0) { id, label in
                    Button(label) {
                        Task { await model.catchUp(id) }
                    }
                    .font(.caption.bold())
                    .padding(.horizontal, 10).padding(.vertical, 8)
                    .background(Color.ink, in: Capsule())
                    .foregroundStyle(.white)
                }
            }
        }
        .padding(14)
        .background(Color.panel, in: RoundedRectangle(cornerRadius: 14))
    }

    private func adaptationBanner(_ adapt: TodayAdaptation) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("Readiness: \(adapt.status)\(adapt.score.map { " · \($0)" } ?? "")\(adapt.softDay ? " · soft day" : "")")
                .font(.subheadline.bold())
                .foregroundStyle(.white)
            Text(adapt.intensityNote).font(.caption).foregroundStyle(Color.mut)
            if let reason = adapt.reasons.first {
                Text(reason).font(.caption2).foregroundStyle(Color.mut.opacity(0.8))
            }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            adapt.softDay ? Color.orange.opacity(0.12) : Color.panel,
            in: RoundedRectangle(cornerRadius: 12)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(adapt.softDay ? Color.orange.opacity(0.4) : Color.line, lineWidth: 1)
        )
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
            Text(model.debrief?.headline ?? "Day complete — nice work.")
                .font(.headline)
                .foregroundStyle(.white)
                .multilineTextAlignment(.center)
            if let msg = model.debrief?.message {
                Text(msg.replacingOccurrences(of: "**", with: ""))
                    .font(.subheadline)
                    .foregroundStyle(Color.mut)
                    .multilineTextAlignment(.leading)
            }
            Button("Share session") {
                model.shareSession()
            }
            .font(.subheadline.bold())
            .foregroundStyle(.white)
            .padding(.horizontal, 16).padding(.vertical, 10)
            .background(Color.brand, in: Capsule())
            Button("See what's next →") {
                model.finished = false
                model.debrief = nil
                model.loading = true
                Task { await model.load() }
            }
            .foregroundStyle(Color.brand)
        }
        .padding()
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

struct ReadinessBanner: View {
    let readiness: ReadinessToday
    let syncing: Bool
    let onSync: () -> Void

    private var statusColor: Color {
        switch readiness.readinessStatus {
        case "primed": return .green
        case "ready": return Color(red: 0.4, green: 0.8, blue: 0.4)
        case "moderate": return .yellow
        case "compromised": return .brand
        default: return .mut
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("Readiness").font(.caption.bold())
                    .foregroundStyle(Color.mut).textCase(.uppercase)
                Spacer()
                Button(action: onSync) {
                    if syncing {
                        ProgressView().controlSize(.mini).tint(.mut)
                    } else {
                        Image(systemName: "arrow.clockwise").font(.caption).foregroundStyle(Color.mut)
                    }
                }
            }
            HStack(alignment: .firstTextBaseline, spacing: 8) {
                if let score = readiness.readinessScore {
                    Text("\(score)").font(.system(size: 34, weight: .black)).foregroundStyle(.white)
                    Text(readiness.readinessStatus ?? "").font(.subheadline.bold())
                        .foregroundStyle(statusColor)
                } else {
                    Text("Synced").font(.headline).foregroundStyle(.white)
                }
            }
            HStack(spacing: 16) {
                metric("Sleep", readiness.sleepH.map { String(format: "%.1fh", $0) })
                metric("HRV", readiness.hrvMs.map { "\(Int($0)) ms" })
                metric("Rest HR", readiness.restingHr.map { "\($0) bpm" })
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.panel, in: RoundedRectangle(cornerRadius: 14))
        .overlay(alignment: .leading) {
            RoundedRectangle(cornerRadius: 2).fill(statusColor).frame(width: 4).padding(.vertical, 10)
        }
    }

    @ViewBuilder private func metric(_ label: String, _ value: String?) -> some View {
        if let value {
            VStack(alignment: .leading, spacing: 1) {
                Text(label).font(.caption2).foregroundStyle(Color.mut)
                Text(value).font(.footnote.bold()).foregroundStyle(.white)
            }
        }
    }
}

struct ExerciseCard: View {
    let ex: TodayExercise
    let slot: Int
    let model: TodayModel

    @State private var weight: String
    @State private var reps: String
    @State private var busy = false
    @State private var showPicker = false
    @State private var formBusy = false
    @State private var formError: String?
    @State private var formResult: FormCheckAssessment?

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
                        if ex.swapped == true {
                            Text("swap").font(.system(size: 9)).foregroundStyle(Color.brand)
                        }
                        if ex.adapted == true {
                            Text("adapted").font(.system(size: 9)).foregroundStyle(.orange)
                        }
                        if ex.loggedSets.contains(where: \.isPr) {
                            Text("PR").font(.caption.bold()).foregroundStyle(Color.brand)
                        }
                    }
                    Text("\(ex.sets) × \(ex.reps) · \(ex.intensity)")
                        .font(.caption).foregroundStyle(Color.mut)
                    if let cue = ex.formCue {
                        Text(cue).font(.caption2).foregroundStyle(Color.mut).lineLimit(3)
                    }
                    if let swap = ex.swapSuggestion {
                        Button("Swap → \(swap)") {
                            Task { await model.swap(slot: slot, to: swap) }
                        }
                        .font(.caption.bold())
                        .foregroundStyle(Color.brand)
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

            Button {
                showPicker = true
            } label: {
                Text(formBusy ? "Reading your set…" : "Check form (video)")
                    .font(.caption.bold())
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 8)
                    .background(Color.ink, in: RoundedRectangle(cornerRadius: 10))
                    .foregroundStyle(.white)
            }
            .disabled(formBusy)
            .fileImporter(
                isPresented: $showPicker,
                allowedContentTypes: [.movie],
                allowsMultipleSelection: false
            ) { result in
                guard case let .success(urls) = result, let url = urls.first else { return }
                formBusy = true
                formError = nil
                formResult = nil
                Task {
                    let access = url.startAccessingSecurityScopedResource()
                    defer {
                        if access { url.stopAccessingSecurityScopedResource() }
                        formBusy = false
                    }
                    formResult = await model.formCheck(
                        exercise: ex.exercise, formCue: ex.formCue, videoURL: url
                    )
                    if formResult == nil, let err = model.error {
                        formError = err
                    }
                }
            }

            if let formError {
                Text(formError).font(.caption2).foregroundStyle(.orange)
            }
            if let formResult {
                FormCheckResultView(assessment: formResult)
            }
        }
        .padding(12)
        .background(Color.panel, in: RoundedRectangle(cornerRadius: 14))
    }
}

struct InjuryProtocolCard: View {
    let item: InjuryProtocol
    let onApply: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Injury protocol")
                .font(.caption.bold())
                .foregroundStyle(Color.brand)
                .textCase(.uppercase)
            Text(item.region).font(.headline).foregroundStyle(.white)
            if let hint = item.volumeHint {
                Text(hint).font(.caption).foregroundStyle(Color.mut)
            }
            ForEach(item.steps, id: \.self) { step in
                HStack(alignment: .top, spacing: 6) {
                    Circle().fill(Color.orange).frame(width: 4, height: 4).padding(.top, 6)
                    Text(step).font(.caption).foregroundStyle(Color.mut)
                }
            }
            if !item.alternatives.isEmpty {
                Text("Prefer today")
                    .font(.caption2.bold())
                    .foregroundStyle(Color.mut)
                    .textCase(.uppercase)
                Text(item.alternatives.joined(separator: " · "))
                    .font(.caption2)
                    .foregroundStyle(.white)
            }
            Button("Apply suggested swaps", action: onApply)
                .font(.caption.bold())
                .frame(maxWidth: .infinity)
                .padding(.vertical, 8)
                .background(Color.ink, in: RoundedRectangle(cornerRadius: 10))
                .foregroundStyle(.white)
        }
        .padding(14)
        .background(Color.orange.opacity(0.12), in: RoundedRectangle(cornerRadius: 14))
        .overlay(RoundedRectangle(cornerRadius: 14).stroke(Color.orange.opacity(0.35), lineWidth: 1))
    }
}

struct PainReportRow: View {
    let options: [PainRegionOption]
    let onPick: (String) -> Void
    @State private var open = false

    var body: some View {
        if options.isEmpty {
            EmptyView()
        } else if !open {
            Button("Something hurts? Flag a region") { open = true }
                .font(.caption.bold())
                .foregroundStyle(Color.mut)
        } else {
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text("Where's the pain?").font(.caption.bold()).foregroundStyle(.white)
                    Spacer()
                    Button("Cancel") { open = false }.font(.caption).foregroundStyle(Color.mut)
                }
                FlowChips(options: options, onPick: onPick)
                Text("Sharp joint pain = stop. This opens a protocol and suggests swaps.")
                    .font(.caption2)
                    .foregroundStyle(Color.mut)
            }
            .padding(12)
            .background(Color.panel, in: RoundedRectangle(cornerRadius: 12))
        }
    }
}

struct FlowChips: View {
    let options: [PainRegionOption]
    let onPick: (String) -> Void

    var body: some View {
        FlexibleChips(options: options, onPick: onPick)
    }
}

/// Simple wrapping chip row without a third-party layout package.
struct FlexibleChips: View {
    let options: [PainRegionOption]
    let onPick: (String) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            ForEach(chunked(options, size: 4), id: \.first?.key) { row in
                HStack(spacing: 6) {
                    ForEach(row, id: \.key) { o in
                        Button(o.label) { onPick(o.key) }
                            .font(.caption.bold())
                            .padding(.horizontal, 10).padding(.vertical, 6)
                            .background(Color.ink, in: Capsule())
                            .foregroundStyle(.white)
                    }
                }
            }
        }
    }

    private func chunked(_ items: [PainRegionOption], size: Int) -> [[PainRegionOption]] {
        stride(from: 0, to: items.count, by: size).map {
            Array(items[$0..<min($0 + size, items.count)])
        }
    }
}

struct FormCheckResultView: View {
    let assessment: FormCheckAssessment

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Form check").font(.caption.bold()).foregroundStyle(Color.brand).textCase(.uppercase)
            Text(assessment.summary).font(.caption).foregroundStyle(.white)
            if !assessment.lookingGood.isEmpty {
                Text("Looking good").font(.caption2.bold()).foregroundStyle(.green).textCase(.uppercase)
                ForEach(assessment.lookingGood, id: \.self) { g in
                    Text("· \(g)").font(.caption2).foregroundStyle(Color.mut)
                }
            }
            if !assessment.cues.isEmpty {
                Text("Next-set cues").font(.caption2.bold()).foregroundStyle(Color.brand).textCase(.uppercase)
                ForEach(assessment.cues, id: \.self) { c in
                    Text("· \(c)").font(.caption2).foregroundStyle(Color.mut)
                }
            }
            if !assessment.safetyFlags.isEmpty {
                Text("Watch").font(.caption2.bold()).foregroundStyle(.orange).textCase(.uppercase)
                ForEach(assessment.safetyFlags, id: \.self) { f in
                    Text("· \(f)").font(.caption2).foregroundStyle(.orange)
                }
            }
            if assessment.unclear {
                Text("Film was unclear — try a side angle with the full bar path in frame.")
                    .font(.caption2)
                    .foregroundStyle(Color.mut)
            }
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.ink, in: RoundedRectangle(cornerRadius: 10))
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

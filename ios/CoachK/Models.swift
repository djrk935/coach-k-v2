import Foundation

// Mirrors the FastAPI contracts. JSON is snake_case; decoding converts.

struct LoggedSet: Codable, Hashable {
    let exercise: String
    let setIndex: Int
    let weightLbs: Double?
    let reps: Int?
    let rir: Double?
    let isPr: Bool
    let slotIndex: Int?
}

struct WarmupSet: Codable, Hashable {
    let weightLbs: Double?
    let reps: Int
    let pct: Double?
    let label: String
}

struct TodayExercise: Codable, Hashable {
    let exercise: String
    let sets: Int
    let reps: String
    let intensity: String
    let tempo: String?
    let restS: Int?
    let notes: String?
    let setType: String?
    let supersetGroup: String?
    let suggestedWeightLbs: Double?
    let loggedSets: [LoggedSet]
    let imageUrls: [String]
    let formCue: String?
    let swapSuggestion: String?
    let adapted: Bool?
    let swapped: Bool?
    let warmupSets: [WarmupSet]?
}

struct TodayAdaptation: Codable, Hashable {
    let score: Int?
    let status: String
    let volumeScale: Double
    let softDay: Bool
    let intensityNote: String
    let reasons: [String]
    let needsCheckin: Bool
}

struct CatchUpInfo: Codable, Hashable {
    let daysMissed: Int
    let options: [String]
    let message: String
}

struct SessionDebrief: Codable, Hashable {
    let headline: String
    let message: String
    let completionPct: Double?
    let prs: [String]?
}

struct TodayPlan: Codable {
    let active: Bool
    let programId: String?
    let programName: String?
    let dayIndex: Int?
    let cycleCount: Int?
    let dayLabel: String?
    let focus: String?
    let exercises: [TodayExercise]?
    let adaptation: TodayAdaptation?
    let catchUp: CatchUpInfo?
    let goalMode: String?
    let painRegions: [String]?
    let injuryProtocols: [InjuryProtocol]?
    let painRegionOptions: [PainRegionOption]?
}

struct LogSetBody: Codable {
    let programId: String
    let dayIndex: Int
    let slotIndex: Int
    let exercise: String
    let weightLbs: Double?
    let reps: Int?
    let rir: Double?
}

struct LogSetResult: Codable {
    let workoutId: String
    let setIndex: Int
    let isPr: Bool
}

struct VoiceLogBody: Codable {
    let text: String
    let programId: String
    let dayIndex: Int
    let exerciseNames: [String]
}

struct VoiceLogResult: Codable {
    let matched: Bool
    let isPr: Bool?
}

struct FinishBody: Codable {
    let programId: String
    let dayIndex: Int
    let sessionRpe: Double?
}

struct FinishResult: Codable {
    let ok: Bool?
    let debrief: SessionDebrief?
}

struct CheckinBody: Encodable {
    let sleepH: Double?
    let soreness: Int?
    let stress: Int?

    enum CodingKeys: String, CodingKey {
        case sleepH = "sleep_h"
        case soreness = "soreness_0_10"
        case stress = "stress_0_10"
    }
}

struct SwapBody: Codable {
    let programId: String
    let dayIndex: Int
    let slotIndex: Int
    let newExercise: String
}

struct CatchUpBody: Codable {
    let programId: String
    let action: String
}

struct InjuryProtocol: Codable, Identifiable, Hashable {
    var id: String { regionKey }
    let region: String
    let regionKey: String
    let steps: [String]
    let alternatives: [String]
    let volumeHint: String?
}

struct PainRegionOption: Codable, Hashable {
    let key: String
    let label: String
}

struct PainBody: Codable {
    let region: String
    let severity: Int
    let context: String?
}

struct ApplyProtocolBody: Codable {
    let programId: String
    let dayIndex: Int
    let regionKey: String?
}

struct FormCheckBody: Codable {
    let exercise: String
    let images: [String]
    let note: String?
    let formCue: String?
}

struct FormCheckAssessment: Codable, Hashable {
    let summary: String
    let lookingGood: [String]
    let cues: [String]
    let safetyFlags: [String]
    let unclear: Bool
}

struct FormCheckResult: Codable {
    let ok: Bool?
    let exercise: String?
    let assessment: FormCheckAssessment?
}

struct ApnsRegisterBody: Codable {
    let deviceToken: String
    let sandbox: Bool
}

struct ReadinessBody: Codable {
    let sleepH: Double?
    let hrvMs: Double?
    let restingHr: Int?
}

struct ReadinessToday: Codable {
    let readinessScore: Int?
    let readinessStatus: String?
    let sleepH: Double?
    let hrvMs: Double?
    let restingHr: Int?
    let source: String?
}

struct ChatMeta: Codable, Identifiable {
    let id: String
    let title: String
}

struct ChatMessage: Codable, Identifiable, Hashable {
    var id = UUID()
    let role: String
    var text: String

    enum CodingKeys: String, CodingKey { case role, text }
}

struct ChatEvent: Codable {
    let type: String
    let text: String?
    let chatId: String?
    let programId: String?
}

struct OkResult: Codable { let ok: Bool }

// ===== Progress =====

struct LiftSeries: Codable {
    let points: [E1RMPoint]
    let current: Double
    let delta: Double
    let deltaPct: Double
}

struct E1RMPoint: Codable {
    let date: String
    let e1rm: Double
}

struct ProgressPR: Codable, Identifiable {
    var id: String { "\(date)-\(exercise)-\(weightLbs ?? 0)" }
    let date: String
    let exercise: String
    let weightLbs: Double?
    let reps: Int?
}

struct ProgressData: Codable {
    let days: Int
    let lifts: [String: LiftSeries]
    let sessions: Int
    let loadSummary: LoadSummary?
    let prs: [ProgressPR]?
    let goalMode: String?
}

struct LoadSummary: Codable {
    let acwr: Double?
    let sessions28d: Int?
}

// ===== Calendar =====

struct CalendarTraining: Codable, Hashable {
    let programDayIndex: Int
    let dayLabel: String?
    let focus: String?
    let exercises: Int?
}

struct CalendarDay: Codable, Identifiable, Hashable {
    var id: String { date }
    let date: String
    let weekday: String
    let isToday: Bool
    let kind: String
    let note: String?
    let training: CalendarTraining?
    let completed: Bool
}

struct CalendarProgram: Codable {
    let id: String
    let name: String?
    let daysPerWeek: Int?
    let dayIndex: Int?
    let cycleCount: Int?
}

struct CalendarData: Codable {
    let start: String
    let end: String
    let weeks: Int
    let program: CalendarProgram?
    let days: [CalendarDay]
}

struct CalendarMarkerBody: Codable {
    let date: String
    let kind: String?
    let note: String?
}

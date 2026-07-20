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

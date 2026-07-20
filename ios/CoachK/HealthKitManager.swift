import Foundation
import HealthKit

// Reads objective recovery signals from HealthKit (populated by an Apple Watch)
// and posts them to /api/readiness, which derives the readiness score. Queries
// return nil gracefully when a signal has no data (e.g. simulator, no Watch).

@MainActor
@Observable
final class HealthKitManager {
    static let shared = HealthKitManager()

    let store = HKHealthStore()
    var available: Bool { HKHealthStore.isHealthDataAvailable() }

    private var readTypes: Set<HKObjectType> {
        var types: Set<HKObjectType> = []
        if let sleep = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) { types.insert(sleep) }
        if let hrv = HKObjectType.quantityType(forIdentifier: .heartRateVariabilitySDNN) { types.insert(hrv) }
        if let rhr = HKObjectType.quantityType(forIdentifier: .restingHeartRate) { types.insert(rhr) }
        return types
    }

    /// Prompt for read access. No-op if already determined (no repeat UI).
    func requestAuthorization() async -> Bool {
        guard available else { return false }
        return await withCheckedContinuation { cont in
            store.requestAuthorization(toShare: [], read: readTypes) { ok, _ in
                cont.resume(returning: ok)
            }
        }
    }

    /// Query last night's metrics and POST them. Returns the server's derived
    /// readiness, or nil if HealthKit yielded nothing to send.
    func sync() async -> ReadinessToday? {
        guard available else { return nil }
        _ = await requestAuthorization()

        async let sleep = lastNightSleepHours()
        async let hrv = mostRecent(.heartRateVariabilitySDNN, unit: .secondUnit(with: .milli))
        async let rhr = mostRecent(.restingHeartRate, unit: HKUnit.count().unitDivided(by: .minute()))

        let body = ReadinessBody(sleepH: await sleep, hrvMs: await hrv, restingHr: (await rhr).map { Int($0.rounded()) })
        guard body.sleepH != nil || body.hrvMs != nil || body.restingHr != nil else { return nil }

        return try? await API.post("/api/readiness", body: body)
    }

    // MARK: - Queries

    private func mostRecent(_ id: HKQuantityTypeIdentifier, unit: HKUnit) async -> Double? {
        guard let type = HKObjectType.quantityType(forIdentifier: id) else { return nil }
        let sort = NSSortDescriptor(key: HKSampleSortIdentifierEndDate, ascending: false)
        // Last 3 days — HRV/RHR are usually captured overnight.
        let start = Calendar.current.date(byAdding: .day, value: -3, to: Date())
        let predicate = HKQuery.predicateForSamples(withStart: start, end: Date())
        return await withCheckedContinuation { cont in
            let q = HKSampleQuery(sampleType: type, predicate: predicate, limit: 1, sortDescriptors: [sort]) { _, samples, _ in
                let value = (samples?.first as? HKQuantitySample)?.quantity.doubleValue(for: unit)
                cont.resume(returning: value)
            }
            store.execute(q)
        }
    }

    private func lastNightSleepHours() async -> Double? {
        guard let type = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) else { return nil }
        // Window: yesterday 18:00 → now, so a single night's sleep is captured.
        let start = Calendar.current.date(byAdding: .hour, value: -18, to: Date())
        let predicate = HKQuery.predicateForSamples(withStart: start, end: Date())
        return await withCheckedContinuation { cont in
            let q = HKSampleQuery(sampleType: type, predicate: predicate, limit: HKObjectQueryNoLimit, sortDescriptors: nil) { _, samples, _ in
                let asleep: Set<Int> = [
                    HKCategoryValueSleepAnalysis.asleepUnspecified.rawValue,
                    HKCategoryValueSleepAnalysis.asleepCore.rawValue,
                    HKCategoryValueSleepAnalysis.asleepDeep.rawValue,
                    HKCategoryValueSleepAnalysis.asleepREM.rawValue,
                ]
                let seconds = (samples as? [HKCategorySample] ?? [])
                    .filter { asleep.contains($0.value) }
                    .reduce(0.0) { $0 + $1.endDate.timeIntervalSince($1.startDate) }
                cont.resume(returning: seconds > 0 ? round(seconds / 360) / 10 : nil)
            }
            store.execute(q)
        }
    }
}

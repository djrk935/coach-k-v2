import SwiftUI
import UIKit

/// Native share sheet for session / progress text.
struct ShareSheet: UIViewControllerRepresentable {
    let items: [Any]

    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: items, applicationActivities: nil)
    }

    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {}
}

enum ShareText {
    static func session(plan: TodayPlan, debrief: SessionDebrief?) -> String {
        var lines: [String] = []
        lines.append(plan.dayLabel ?? "Coach K session")
        if let name = plan.programName { lines.append(name) }
        if let focus = plan.focus { lines.append(focus) }
        lines.append("")
        for ex in plan.exercises ?? [] {
            guard !ex.loggedSets.isEmpty else { continue }
            let sets = ex.loggedSets.map { s in
                let w = s.weightLbs.map { String(Int($0)) } ?? "—"
                let r = s.reps.map(String.init) ?? "—"
                return "\(w)×\(r)\(s.isPr ? " PR" : "")"
            }.joined(separator: ", ")
            lines.append("\(ex.exercise): \(sets)")
        }
        if let d = debrief {
            lines.append("")
            lines.append(d.headline)
            lines.append(d.message.replacingOccurrences(of: "**", with: ""))
            if let prs = d.prs, !prs.isEmpty {
                lines.append("PRs: \(prs.joined(separator: ", "))")
            }
        }
        lines.append("")
        lines.append("— Coach K")
        return lines.joined(separator: "\n")
    }

    static func progress(_ data: ProgressData) -> String {
        var lines = ["Coach K progress · last \(data.days) days"]
        if let mode = data.goalMode { lines.append("Mode: \(mode)") }
        lines.append("Sessions: \(data.sessions)")
        if let acwr = data.loadSummary?.acwr {
            lines.append(String(format: "ACWR: %.2f", acwr))
        }
        lines.append("")
        for (k, L) in data.lifts.sorted(by: { $0.key < $1.key }) {
            let sign = L.delta >= 0 ? "+" : ""
            lines.append(String(
                format: "%@: %.0f lbs e1RM (%@%.0f / %@%.1f%%)",
                k, L.current, sign, L.delta, sign, L.deltaPct
            ))
        }
        if let prs = data.prs?.prefix(5), !prs.isEmpty {
            lines.append("")
            lines.append("Recent PRs:")
            for p in prs {
                let w = p.weightLbs.map { String(Int($0)) } ?? "—"
                let r = p.reps.map(String.init) ?? "—"
                lines.append("· \(p.date) \(p.exercise) \(w)×\(r)")
            }
        }
        lines.append("")
        lines.append("— Coach K")
        return lines.joined(separator: "\n")
    }
}

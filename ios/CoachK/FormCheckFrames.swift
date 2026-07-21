import AVFoundation
import Foundation
import UIKit

/// Sample JPEG keyframes from a short gym clip for POST /api/form-check.
enum FormCheckFrames {
    static func extract(
        from url: URL,
        maxFrames: Int = 5,
        maxDim: CGFloat = 960
    ) async throws -> [String] {
        let asset = AVURLAsset(url: url)
        let duration = try await asset.load(.duration)
        let seconds = min(CMTimeGetSeconds(duration), 20)
        guard seconds > 0, seconds.isFinite else {
            throw NSError(domain: "FormCheck", code: 1, userInfo: [
                NSLocalizedDescriptionKey: "Couldn't read that video",
            ])
        }

        let generator = AVAssetImageGenerator(asset: asset)
        generator.appliesPreferredTrackTransform = true
        generator.maximumSize = CGSize(width: maxDim, height: maxDim)

        var stamps: [Double] = []
        if maxFrames <= 1 {
            stamps = [min(0.05, seconds * 0.5)]
        } else {
            for i in 0..<maxFrames {
                let t = (Double(i) / Double(maxFrames - 1)) * max(seconds - 0.05, 0)
                stamps.append(max(0, t))
            }
        }

        var out: [String] = []
        for t in stamps {
            let time = CMTime(seconds: t, preferredTimescale: 600)
            let cg = try generator.copyCGImage(at: time, actualTime: nil)
            let image = UIImage(cgImage: cg)
            guard let data = image.jpegData(compressionQuality: 0.8) else { continue }
            out.append("data:image/jpeg;base64," + data.base64EncodedString())
        }
        if out.isEmpty {
            throw NSError(domain: "FormCheck", code: 2, userInfo: [
                NSLocalizedDescriptionKey: "Couldn't pull frames from that clip",
            ])
        }
        return out
    }
}

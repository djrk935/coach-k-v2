import AVFoundation
import Foundation
import Speech

// One-shot speech capture: start(), speak "bench 225 for 5", stop() (or
// silence-end) -> transcript handed to the caller for /api/today/log-voice.

@MainActor
@Observable
final class VoiceLogger {
    var isListening = false
    var transcript = ""

    private let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    private let audioEngine = AVAudioEngine()
    private var request: SFSpeechAudioBufferRecognitionRequest?
    private var task: SFSpeechRecognitionTask?
    private var onFinal: ((String) -> Void)?

    func start(onFinal: @escaping (String) -> Void) async {
        guard !isListening else { return }
        self.onFinal = onFinal
        transcript = ""

        let speechAuth = await withCheckedContinuation { cont in
            SFSpeechRecognizer.requestAuthorization { cont.resume(returning: $0) }
        }
        guard speechAuth == .authorized else { return }
        guard await AVAudioApplication.requestRecordPermission() else { return }

        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.record, mode: .measurement, options: .duckOthers)
            try session.setActive(true, options: .notifyOthersOnDeactivation)

            let req = SFSpeechAudioBufferRecognitionRequest()
            req.shouldReportPartialResults = true
            request = req

            let input = audioEngine.inputNode
            let format = input.outputFormat(forBus: 0)
            input.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in
                req.append(buffer)
            }
            audioEngine.prepare()
            try audioEngine.start()
            isListening = true

            task = recognizer?.recognitionTask(with: req) { [weak self] result, error in
                Task { @MainActor in
                    guard let self else { return }
                    if let result {
                        self.transcript = result.bestTranscription.formattedString
                        if result.isFinal { self.finish() }
                    }
                    if error != nil { self.finish() }
                }
            }
        } catch {
            stopEngine()
        }
    }

    /// User taps the mic again to end capture.
    func stop() {
        request?.endAudio()
        // finish() arrives via the recognition callback's isFinal; if the
        // recognizer never finalizes (e.g. no speech), force it.
        Task { @MainActor in
            try? await Task.sleep(for: .seconds(1.5))
            if self.isListening { self.finish() }
        }
    }

    private func finish() {
        guard isListening else { return }
        stopEngine()
        isListening = false
        let text = transcript.trimmingCharacters(in: .whitespacesAndNewlines)
        if !text.isEmpty { onFinal?(text) }
        onFinal = nil
    }

    private func stopEngine() {
        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)
        task?.cancel()
        task = nil
        request = nil
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
    }
}

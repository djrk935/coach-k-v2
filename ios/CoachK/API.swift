import Foundation

// Thin client over the Coach K backend. Server URL + app password live in
// UserDefaults (editable in Settings); every request carries x-app-key.

enum APIError: LocalizedError {
    case badURL
    case http(Int, String)

    var errorDescription: String? {
        switch self {
        case .badURL: return "Invalid server URL — check Settings."
        case let .http(code, body): return "Server error \(code): \(body.prefix(140))"
        }
    }
}

enum API {
    static var baseURL: String {
        UserDefaults.standard.string(forKey: "baseURL") ?? "http://localhost:8000"
    }

    static var appKey: String {
        UserDefaults.standard.string(forKey: "appKey") ?? ""
    }

    static let decoder: JSONDecoder = {
        let d = JSONDecoder()
        d.keyDecodingStrategy = .convertFromSnakeCase
        return d
    }()

    static let encoder: JSONEncoder = {
        let e = JSONEncoder()
        e.keyEncodingStrategy = .convertToSnakeCase
        return e
    }()

    static func url(_ path: String) throws -> URL {
        guard let u = URL(string: baseURL + path) else { throw APIError.badURL }
        return u
    }

    static func request(_ path: String, method: String = "GET", body: Data? = nil) throws -> URLRequest {
        var req = URLRequest(url: try url(path))
        req.httpMethod = method
        req.setValue(appKey, forHTTPHeaderField: "x-app-key")
        if let body {
            req.httpBody = body
            req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        }
        return req
    }

    static func get<T: Decodable>(_ path: String) async throws -> T {
        let (data, resp) = try await URLSession.shared.data(for: request(path))
        try check(resp, data)
        return try decoder.decode(T.self, from: data)
    }

    static func post<T: Decodable>(_ path: String, body: some Encodable) async throws -> T {
        let req = try request(path, method: "POST", body: encoder.encode(body))
        let (data, resp) = try await URLSession.shared.data(for: req)
        try check(resp, data)
        return try decoder.decode(T.self, from: data)
    }

    static func check(_ resp: URLResponse, _ data: Data) throws {
        guard let http = resp as? HTTPURLResponse else { return }
        guard (200 ..< 300).contains(http.statusCode) else {
            throw APIError.http(http.statusCode, String(data: data, encoding: .utf8) ?? "")
        }
    }

    /// POST /api/chat and stream SSE events.
    static func streamChat(
        message: String, chatId: String?, onEvent: @escaping @MainActor (ChatEvent) -> Void
    ) async throws {
        struct Body: Codable {
            let message: String
            let chatId: String?
        }
        let req = try request("/api/chat", method: "POST", body: encoder.encode(Body(message: message, chatId: chatId)))
        let (bytes, resp) = try await URLSession.shared.bytes(for: req)
        try check(resp, Data())
        for try await line in bytes.lines {
            guard line.hasPrefix("data: "),
                  let data = line.dropFirst(6).data(using: .utf8),
                  let event = try? decoder.decode(ChatEvent.self, from: data)
            else { continue }
            await onEvent(event)
        }
    }

    static func imageURL(_ path: String) -> URL? {
        URL(string: baseURL + path)
    }
}

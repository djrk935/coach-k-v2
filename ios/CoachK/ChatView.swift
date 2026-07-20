import SwiftUI

@MainActor
@Observable
final class ChatModel {
    var messages: [ChatMessage] = []
    var input = ""
    var busy = false

    private var chatId: String? {
        get { UserDefaults.standard.string(forKey: "chatId") }
        set { UserDefaults.standard.set(newValue, forKey: "chatId") }
    }

    func loadHistory() async {
        guard let id = chatId else { return }
        if let history: [ChatMessage] = try? await API.get("/api/chats/\(id)/messages") {
            messages = history
        }
    }

    func newChat() {
        chatId = nil
        messages = []
    }

    func send() async {
        let text = input.trimmingCharacters(in: .whitespaces)
        guard !text.isEmpty, !busy else { return }
        input = ""
        busy = true
        messages.append(ChatMessage(role: "user", text: text))
        messages.append(ChatMessage(role: "assistant", text: ""))

        do {
            try await API.streamChat(message: text, chatId: chatId) { [weak self] event in
                guard let self else { return }
                switch event.type {
                case "token", "error":
                    let add = event.type == "error" ? "⚠ \(event.text ?? "")" : (event.text ?? "")
                    if let last = self.messages.indices.last {
                        self.messages[last].text += add
                    }
                case "done":
                    if let id = event.chatId { self.chatId = id }
                default:
                    break
                }
            }
        } catch {
            if let last = messages.indices.last {
                messages[last].text += "⚠ \(error.localizedDescription)"
            }
        }
        busy = false
    }
}

struct ChatView: View {
    @State private var model = ChatModel()
    @FocusState private var focused: Bool

    var body: some View {
        NavigationStack {
            ZStack {
                Color.ink.ignoresSafeArea()
                VStack(spacing: 0) {
                    messagesList
                    inputBar
                }
            }
            .navigationTitle("Coach K")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        model.newChat()
                    } label: {
                        Image(systemName: "square.and.pencil").foregroundStyle(Color.mut)
                    }
                }
            }
        }
        .task { await model.loadHistory() }
    }

    private var messagesList: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(spacing: 10) {
                    if model.messages.isEmpty {
                        VStack(spacing: 6) {
                            Text("What are we training for?")
                                .font(.headline).foregroundStyle(Color.mut)
                            Text("Ask for a program, log a session, or check in.")
                                .font(.caption).foregroundStyle(Color.mut)
                        }
                        .padding(.top, 120)
                    }
                    ForEach(model.messages) { msg in
                        bubble(msg).id(msg.id)
                    }
                }
                .padding()
            }
            .onChange(of: model.messages.last?.text) {
                if let last = model.messages.last {
                    proxy.scrollTo(last.id, anchor: .bottom)
                }
            }
        }
    }

    @ViewBuilder private func bubble(_ msg: ChatMessage) -> some View {
        let isUser = msg.role == "user"
        HStack {
            if isUser { Spacer(minLength: 48) }
            Text(rendered(msg.text.isEmpty && model.busy ? "…" : msg.text))
                .font(.subheadline)
                .padding(.horizontal, 14).padding(.vertical, 10)
                .background(
                    isUser ? Color.brand.opacity(0.92) : Color.panel,
                    in: RoundedRectangle(cornerRadius: 16)
                )
                .foregroundStyle(.white)
                .tint(Color.brand)
            if !isUser { Spacer(minLength: 48) }
        }
    }

    private func rendered(_ text: String) -> AttributedString {
        (try? AttributedString(
            markdown: text,
            options: .init(interpretedSyntax: .inlineOnlyPreservingWhitespace)
        )) ?? AttributedString(text)
    }

    private var inputBar: some View {
        HStack(spacing: 8) {
            TextField("Log a session, ask for a program…", text: $model.input, axis: .vertical)
                .lineLimit(1 ... 4)
                .focused($focused)
                .padding(.horizontal, 14).padding(.vertical, 10)
                .background(Color.panel, in: RoundedRectangle(cornerRadius: 14))
                .foregroundStyle(.white)
            Button {
                focused = false
                Task { await model.send() }
            } label: {
                Image(systemName: "arrow.up.circle.fill")
                    .font(.system(size: 30))
                    .foregroundStyle(model.busy ? Color.mut : Color.brand)
            }
            .disabled(model.busy)
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(Color.ink)
    }
}

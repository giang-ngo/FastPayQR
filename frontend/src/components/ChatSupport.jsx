import {useState, useEffect, useRef} from "react";
import axios from "axios";

const ChatSupport = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const ws = useRef(null);
    const [role, setRole] = useState("guest");
    const [userId, setUserId] = useState(null);
    const [toUser, setToUser] = useState("");
    const [onlineUsers, setOnlineUsers] = useState([]);
    const [typingStatus, setTypingStatus] = useState({});
    const messagesEndRef = useRef(null);
    const typingTimeout = useRef(null);

    useEffect(() => {
        const token = localStorage.getItem("accessToken");
        if (token) {
            axios
                .get("http://localhost:8000/auth/me", {headers: {Authorization: `Bearer ${token}`}})
                .then((res) => {
                    const roleFromApi = res.data.is_admin ? "admin" : "user";
                    setRole(roleFromApi);
                    setUserId(res.data.id);
                    connectWebSocket(token, res.data.id);
                })
                .catch(() => {
                    const guestId = "guest-" + Date.now();
                    setRole("guest");
                    setUserId(guestId);
                    connectWebSocket(null, guestId);
                });
        } else {
            const guestId = "guest-" + Date.now();
            setRole("guest");
            setUserId(guestId);
            connectWebSocket(null, guestId);
        }

        return () => {
            if (ws.current) ws.current.close();
        };
    }, []);

    const connectWebSocket = (token, userIdParam) => {
        const url = token
            ? `ws://127.0.0.1:8000/ws/support/chat?token=${token}`
            : `ws://127.0.0.1:8000/ws/support/chat?guest_id=${userIdParam}`;

        ws.current = new WebSocket(url);

        ws.current.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("data.type", data.type)

                if (data.type === "online_users") {
                    setOnlineUsers(data.users || []);
                } else if (data.type === "typing") {
                    setTypingStatus((prev) => ({...prev, [data.from]: data.typing}));
                } else if (data.type === "notification") {
                    setMessages((prev) => [
                        ...prev,
                        {
                            text: data.message,
                            timestamp: Date.now(),
                            system: true,
                        },
                    ]);
                } else {
                    setMessages((prev) => {
                        const exists = prev.some(
                            (msg) =>
                                msg.timestamp === data.timestamp &&
                                msg.from === data.from &&
                                msg.text === data.text
                        );
                        if (exists) return prev;
                        return [...prev, data];
                    });
                }
            } catch (error) {
                console.error("Invalid WS message", error);
            }
        };

        ws.current.onopen = () => console.log("WebSocket connected");
        ws.current.onclose = () => console.log("WebSocket disconnected");
        ws.current.onerror = (e) => console.error("WebSocket error", e);
    };

    const sendTypingStatus = (isTyping) => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(
                JSON.stringify({
                    type: "typing",
                    from: userId,
                    typing: isTyping,
                })
            );
        }
    };

    const sendMessage = () => {
        if (!input.trim()) return;

        const message = {
            from: userId,
            text: input.trim(),
            timestamp: Date.now(),
            to: toUser.trim(),
        };

        if (role === "admin") {
            if (!toUser.trim()) {
                alert("Vui lòng nhập User ID để gửi tin");
                return;
            }
        }

        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify(message));
            setInput("");
            sendTypingStatus(false);
        } else {
            alert("WebSocket chưa kết nối hoặc đã đóng");
        }
    };

    useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({behavior: "smooth"});
        }
    }, [messages]);

    return (
        <div
            style={{
                position: "fixed",
                bottom: 20,
                right: 20,
                width: 350,
                height: 500,
                border: "1px solid #ccc",
                background: "#fefefe",
                borderRadius: 12,
                boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                display: "flex",
                flexDirection: "column",
                fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                zIndex: 9999,
            }}
        >
            <div
                style={{
                    padding: "12px 16px",
                    borderBottom: "1px solid #eee",
                    backgroundColor: "#0078d4",
                    color: "white",
                    fontWeight: "600",
                    fontSize: 18,
                    textAlign: "center",
                    borderTopLeftRadius: 12,
                    borderTopRightRadius: 12,
                }}
            >
                Hỗ trợ trực tuyến
            </div>

            {role === "admin" && (
                <div
                    style={{
                        backgroundColor: "#f1f1f1",
                        padding: "8px 12px",
                        fontSize: 13,
                        color: "#333",
                        borderBottom: "1px solid #ddd",
                    }}
                >

                    🟢 Online: {onlineUsers.length} người (user {onlineUsers.join(", ") || "Không có ai"})
                </div>
            )}

            <div
                style={{
                    flex: 1,
                    overflowY: "auto",
                    padding: "12px 16px",
                    backgroundColor: "#fafafa",
                    display: "flex",
                    flexDirection: "column",
                    gap: 8,
                }}
            >
                {messages.length === 0 && (
                    <div style={{color: "#999", fontStyle: "italic", textAlign: "center"}}>
                        Chưa có tin nhắn nào
                    </div>
                )}

                {role === "admin" && (
                    <input
                        type="text"
                        placeholder="Nhập userId nhận tin"
                        value={toUser}
                        onChange={(e) => setToUser(e.target.value)}
                        style={{
                            marginBottom: 8,
                            padding: "8px 12px",
                            borderRadius: 8,
                            border: "1px solid #ccc",
                            fontSize: 14,
                        }}
                    />
                )}

                {messages.map((msg, i) => {
                    if (!msg.text || !msg.text.trim()) return null;
                    if (msg.system) {
                        return (
                            <div
                                key={i}
                                style={{
                                    textAlign: "center",
                                    fontSize: 12,
                                    fontStyle: "italic",
                                    color: "#888",
                                }}
                            >
                                {msg.text}
                            </div>
                        );
                    }

                    const isMe = String(msg.from) === String(userId);
                    let senderLabel = "";

                    if (isMe) {
                        if (role === "admin" && msg.to && msg.to !== "admin") {
                            senderLabel = `Admin → ${msg.to}`;
                        } else if (role === "admin") {
                            senderLabel = "Bạn (Admin)";
                        } else {
                            senderLabel = "Bạn";
                        }
                    } else {
                        if (role === "admin") {
                            if (msg.from === "admin") {
                                senderLabel = "Admin";
                            } else if (typeof msg.from === "string" && msg.from.startsWith("guest-")) {
                                senderLabel = "Khách";
                            } else {
                                senderLabel = `User ${msg.from}`;
                            }
                        } else {
                            if (msg.from === "admin") {
                                senderLabel = "Admin";
                            } else if (typeof msg.from === "string" && msg.from.startsWith("guest-")) {
                                senderLabel = "Khách";
                            } else {
                                senderLabel = `User ${msg.from}`;
                            }
                        }
                    }

                    const timeString = new Date(msg.timestamp).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                    });

                    return (
                        <div
                            key={i}
                            style={{
                                maxWidth: "75%",
                                alignSelf: isMe ? "flex-end" : "flex-start",
                                backgroundColor: isMe ? "#0078d4" : "#e1e1e1",
                                color: isMe ? "white" : "#333",
                                padding: "8px 12px",
                                borderRadius: 16,
                                wordBreak: "break-word",
                                whiteSpace: "pre-wrap",
                                boxShadow: isMe ? "0 1px 3px rgba(0,0,0,0.3)" : "none",
                                fontSize: 14,
                                lineHeight: "1.4",
                                marginBottom: 6,
                                display: "flex",
                                flexDirection: "column",
                                gap: 4,
                            }}
                            title={new Date(msg.timestamp).toLocaleString()}
                        >
                            <small style={{fontWeight: "600", opacity: 0.75, fontSize: 12}}>
                                {senderLabel}
                            </small>
                            <span>{msg.text}</span>
                            {msg.to && (
                                <small
                                    style={{
                                        fontSize: 10,
                                        opacity: 0.6,
                                        alignSelf: "flex-start",
                                        marginTop: 2,
                                        fontStyle: "italic",
                                    }}
                                >
                                    → To: {msg.to}
                                </small>
                            )}
                            <small style={{fontSize: 10, opacity: 0.6, alignSelf: "flex-end"}}>
                                {timeString}
                            </small>
                        </div>
                    );
                })}

                <div ref={messagesEndRef}/>
            </div>

            {/* Hiển thị đang gõ ngay trên input */}
            <div
                style={{
                    minHeight: 20,
                    padding: "0 16px",
                    fontStyle: "italic",
                    fontSize: 12,
                    color: "#666",
                }}
            >
                {Object.entries(typingStatus).map(
                    ([uid, typing]) =>
                        typing &&
                        uid !== userId && (
                            <div key={uid}>
                                {role === "admin" ? `User ${uid} đang gõ...` : "Admin đang gõ..."}
                            </div>
                        )
                )}
            </div>

            <div
                style={{borderTop: "1px solid #ddd", padding: 12, display: "flex", gap: 8}}
            >
                <input
                    type="text"
                    value={input}
                    onChange={(e) => {
                        setInput(e.target.value);
                        sendTypingStatus(true);
                        clearTimeout(typingTimeout.current);
                        typingTimeout.current = setTimeout(() => sendTypingStatus(false), 2000);
                    }}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") sendMessage();
                    }}
                    placeholder="Nhập tin nhắn..."
                    style={{
                        flex: 1,
                        padding: "8px 12px",
                        borderRadius: 20,
                        border: "1px solid #ccc",
                        outline: "none",
                        fontSize: 14,
                    }}
                />

                <button
                    onClick={sendMessage}
                    style={{
                        backgroundColor: "#0078d4",
                        color: "white",
                        border: "none",
                        padding: "8px 16px",
                        borderRadius: 20,
                        cursor: "pointer",
                        fontWeight: "600",
                        fontSize: 14,
                    }}
                >
                    Gửi
                </button>
            </div>
        </div>
    );
};

export default ChatSupport;
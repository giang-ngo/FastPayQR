import { useParams } from "react-router-dom";
import { useEffect, useState, useRef } from "react";
import axios from "axios";

const PayPage = () => {
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
    const WS_BASE = import.meta.env.VITE_WS_URL || "ws://localhost:8000";
    const { orderId } = useParams();
    const [order, setOrder] = useState(null);
    const [error, setError] = useState(null);
    const [paid, setPaid] = useState(false);
    const wsRef = useRef(null);

    useEffect(() => {
        const fetchOrder = async () => {
            try {
                const accessToken = localStorage.getItem("accessToken");
                const res = await axios.get(`${BACKEND_URL}/orders/${orderId}/qr`, {
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                });
                setOrder(res.data);
                if (res.data.status.toLowerCase() === "paid") setPaid(true);
            } catch {
                setError("Order not found");
            }
        };

        fetchOrder();
        console.log("Connecting WebSocket with orderId:", orderId);
        const ws = new WebSocket(`${WS_BASE}/ws/orders/${orderId}`);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log("WebSocket connected");
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("WebSocket message:", data);
            if (data.status.toLowerCase() === "paid") {
                setPaid(true);
                setOrder((prev) => ({ ...prev, status: "paid" }));
            }
        };

        ws.onerror = (error) => {
            console.error("WebSocket error", error);
        };

        ws.onclose = () => {
            console.log("WebSocket closed");
        };

        return () => {
            if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
                ws.close();
            }
        };
    }, [orderId]);

    const handlePayment = async () => {
        try {
            const accessToken = localStorage.getItem("accessToken");
            await axios.post(`${BACKEND_URL}/payment/pay/internal/${orderId}`, null, {
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                },
            });
        } catch (err) {
            setError(err.response?.data?.detail || "Payment failed");
        }
    };

    if (error) return <p className="text-red-600">{error}</p>;
    if (!order) return <p>Loading order...</p>;

    return (
        <div className="max-w-md mx-auto mt-10 p-6 border rounded shadow-md bg-white">
            <h2 className="text-2xl font-semibold mb-4">Payment for Order</h2>
            <p><strong>Customer:</strong> {order.customer_name}</p>
            <p><strong>Amount:</strong> {order.amount.toLocaleString()} VND</p>
            <p><strong>Status:</strong> {paid ? "Paid" : order.status}</p>

            {!paid && (
                <button
                    onClick={handlePayment}
                    className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                >
                    Pay with Wallet
                </button>
            )}

            {paid && <p className="mt-4 text-green-600">✅ Payment successful!</p>}
        </div>
    );
};

export default PayPage;
import {useState} from "react";
import axios from "axios";

const OrderQRInfo = () => {
        const [orderId, setOrderId] = useState("");
        const [orderData, setOrderData] = useState(null);
        const [loading, setLoading] = useState(false);
        const [error, setError] = useState(null);

        const handleFetchOrder = async () => {
            if (!orderId.trim()) {
                alert("Vui lòng nhập order_id");
                return;
            }
            setLoading(true);
            setError(null);
            setOrderData(null);
            try {
                const res = await axios.get(`http://192.168.1.6:8000/orders/${orderId}/qr`);
                setOrderData(res.data);
            } catch (err) {
                if (err.response) {
                    setError(`Lỗi server: ${err.response.status} - ${err.response.data.detail || err.response.statusText}`);
                    console.error(err.response);
                } else if (err.request) {
                    setError("Không nhận được phản hồi từ server.");
                    console.error(err.request);
                } else {
                    setError("Lỗi khi lấy dữ liệu đơn hàng.");
                    console.error("Error", err.message);
                }
            } finally {
                setLoading(false);
            }
        };

        return (
            <div className="container">
                <h2 className="title">Thông tin đơn hàng và mã QR</h2>

                <div className="form-group">
                    <input
                        type="text"
                        placeholder="Nhập order_id..."
                        value={orderId}
                        onChange={(e) => setOrderId(e.target.value)}
                        className="input"
                        disabled={loading}
                    />
                    <button onClick={handleFetchOrder} disabled={loading} className="button">
                        {loading ? "Đang tải..." : "Lấy thông tin"}
                    </button>
                </div>

                {error && <p className="error-text">{error}</p>}

                {orderData && (
                    <div className="order-info">
                        <div className="qr-container">
                            <img src={orderData.image_url} alt="QR Code" className="qr-image"/>
                        </div>

                        <div className="details">
                            <p><strong>Order ID:</strong> {orderData.order_id}</p>
                            <p><strong>Khách hàng:</strong> {orderData.customer_name}</p>
                            <p><strong>Tổng tiền:</strong> {orderData.amount.toLocaleString()} VND</p>
                            <p><strong>Trạng thái:</strong> {orderData.status}</p>

                            {Array.isArray(orderData.items) && orderData.items.length > 0 && (
                                <div className="mt-4">
                                    <h4 className="font-semibold">Sản phẩm:</h4>
                                    <ul className="list-disc pl-5">
                                        {orderData.items.map((item, index) => (
                                            <li key={index}>
                                                {item.name} - {item.quantity} x {item.price.toLocaleString()} VND
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            <a
                                href={orderData.qr_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="button pay-button"
                            >
                                Thanh toán đơn hàng
                            </a>
                        </div>
                    </div>
                )}

            </div>
        );
    }
;

export default OrderQRInfo;

import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import axios from "axios";

const OrderQRInfo = () => {
  const [orderId, setOrderId] = useState("");
  const [orderData, setOrderData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    if (!token) {
      navigate("/login");
    }
  }, [navigate]);

  const handleFetchOrder = async () => {
    if (!orderId.trim()) {
      alert("Vui lòng nhập order_id");
      return;
    }

    setLoading(true);
    setError(null);
    setOrderData(null);

    try {
      const accessToken = localStorage.getItem("accessToken");
      const res = await axios.get(`http://127.0.0.1:8000/orders/${orderId}/qr`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      setOrderData(res.data);
    } catch (err) {
      setError("Không thể lấy thông tin đơn hàng.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container p-4">
      <h2 className="text-xl font-bold mb-4">Thông tin đơn hàng và mã QR</h2>
      <div className="mb-4">
        <input
          type="text"
          placeholder="Nhập order_id..."
          value={orderId}
          onChange={(e) => setOrderId(e.target.value)}
          className="border px-3 py-2 mr-2"
          disabled={loading}
        />
        <button
          onClick={handleFetchOrder}
          disabled={loading}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          {loading ? "Đang tải..." : "Lấy thông tin"}
        </button>
      </div>

      {error && <p className="text-red-600">{error}</p>}

      {orderData && (
        <div className="border p-4 rounded bg-white shadow">
          <img src={orderData.image_url} alt="QR Code" className="w-40 mb-4" />
          <p><strong>Order ID:</strong> {orderData.order_id}</p>
          <p><strong>Khách hàng:</strong> {orderData.customer_name}</p>
          <p><strong>Tổng tiền:</strong> {orderData.amount.toLocaleString()} VND</p>
          <p><strong>Trạng thái:</strong> {orderData.status}</p>

          {orderData.items?.length > 0 && (
            <>
              <h4 className="mt-4 font-semibold">Sản phẩm:</h4>
              <ul className="list-disc pl-5">
                {orderData.items.map((item, i) => (
                  <li key={i}>
                    {item.name} - {item.quantity} x {item.price.toLocaleString()} VND
                  </li>
                ))}
              </ul>
            </>
          )}

          <button
              onClick={() => navigate(`/payment/pay/${orderData.order_id}`)}
              className="inline-block mt-4 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Thanh toán đơn hàng
          </button>
        </div>
      )}
    </div>
  );
};

export default OrderQRInfo;

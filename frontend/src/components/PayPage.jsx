import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";

const PayPage = () => {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [error, setError] = useState(null);
  const [paid, setPaid] = useState(false);

  useEffect(() => {
    const fetchOrder = async () => {
      try {
        const accessToken = localStorage.getItem("accessToken");
        console.log("AccessToken:", accessToken);

        // Lấy thông tin order
        const res = await axios.get(`http://192.168.1.4:8000/orders/${orderId}/qr`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        setOrder(res.data);
      } catch {
        setError("Order not found");
      }
    };
    fetchOrder();
  }, [orderId]);

  const handlePayment = async () => {
    try {
      const accessToken = localStorage.getItem("accessToken");
      await axios.post(`http://192.168.1.4:8000/pay/internal/${orderId}`, null, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      setPaid(true);

      // Reload lại thông tin order sau khi thanh toán
      const res = await axios.get(`http://192.168.1.4:8000/orders/${orderId}/qr`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      setOrder(res.data);
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

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginForm from "./components/LoginForm";
import OrderQRInfo from "./components/OrderQRInfo";
import PayPage from "./components/PayPage";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginForm />} />
        <Route path="/" element={<OrderQRInfo />} />
        <Route path="/payment/pay/:orderId" element={<PayPage />} />
      </Routes>
    </Router>
  );
};

export default App;

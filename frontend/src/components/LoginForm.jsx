import {useNavigate} from "react-router-dom";
import {useState} from "react";
import axios from "axios";

const LoginForm = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError(null);
        try {
            const res = await axios.post("http://127.0.0.1:8000/auth/login", {
                email,
                password,
            });

            const {access_token, refresh_token} = res.data;
            localStorage.setItem("accessToken", access_token);
            localStorage.setItem("refreshToken", refresh_token);

            navigate("/");
        } catch (err) {
            setError(err.response?.data?.detail || "Đăng nhập thất bại");
        }
    };

    return (
        <div className="max-w-sm mx-auto mt-20 p-6 border bg-white rounded shadow">
            <h2 className="text-xl font-semibold mb-4 text-center">Đăng nhập</h2>
            {error && <p className="text-red-600 mb-4">{error}</p>}

            <form onSubmit={handleLogin}>
                <div className="mb-4">
                    <label className="block mb-1">Email</label>
                    <input
                        type="email"
                        className="w-full px-3 py-2 border rounded"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div className="mb-6">
                    <label className="block mb-1">Mật khẩu</label>
                    <input
                        type="password"
                        className="w-full px-3 py-2 border rounded"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button
                    type="submit"
                    className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
                >
                    Đăng nhập
                </button>
            </form>
        </div>
    );
};

export default LoginForm;

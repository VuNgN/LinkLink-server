import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../styles/App.css";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      // Gửi request login
      const res = await fetch("/api/v1/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (res.status === 401 || res.status === 403) {
        setError("Sai tài khoản hoặc mật khẩu!");
        return;
      }
      if (!res.ok) throw new Error("Lỗi đăng nhập");
      const data = await res.json();
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      localStorage.setItem("username", data.username);
      navigate("/");
    } catch {
      setError("Lỗi đăng nhập!");
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100%",
        maxWidth: "100vw",
        boxSizing: "border-box",
        background: "var(--color-background, #fff)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 0,
        margin: 0,
        overflowX: "hidden",
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          background: "var(--color-surface)",
          padding: 32,
          borderRadius: 16,
          boxShadow: "0 2px 16px #7C4DFF22",
          width: "100%",
          maxWidth: 400,
          margin: "0 8px",
        }}
      >
        <h2
          style={{
            color: "var(--color-primary)",
            marginBottom: 16,
            textAlign: "center",
          }}
        >
          Đăng nhập
        </h2>
        <div style={{ marginBottom: 16 }}>
          <input
            type="text"
            placeholder="Tên đăng nhập"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={{
              width: "100%",
              padding: 12,
              borderRadius: 8,
              border: "1px solid #eee",
              marginBottom: 8,
            }}
          />
          <input
            type="password"
            placeholder="Mật khẩu"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{
              width: "100%",
              padding: 12,
              borderRadius: 8,
              border: "1px solid #eee",
            }}
          />
        </div>
        {error && (
          <div
            style={{
              color: "var(--color-error)",
              marginBottom: 12,
              textAlign: "center",
            }}
          >
            {error}
          </div>
        )}
        <button
          type="submit"
          style={{
            width: "100%",
            background: "var(--color-primary)",
            color: "var(--color-on-primary)",
            padding: 12,
            border: "none",
            borderRadius: 8,
            fontWeight: 600,
            fontSize: 16,
            cursor: "pointer",
            marginBottom: 8,
          }}
        >
          Đăng nhập
        </button>
        <div style={{ textAlign: "center", fontSize: 14 }}>
          Chưa có tài khoản?{" "}
          <Link
            to="/register"
            style={{
              color: "var(--color-primary)",
              textDecoration: "underline",
            }}
          >
            Đăng ký
          </Link>
        </div>
      </form>
    </div>
  );
}

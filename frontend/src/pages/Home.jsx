import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import fetchWithAuth from "../utils/fetchWithAuth";
import PostItem from "../components/PostItem";
import PostDetail from "../components/PostDetail";
import Modal from "../components/Modal";

export default function Home() {
  const navigate = useNavigate();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [formImage, setFormImage] = useState(null);
  const [formImageUrl, setFormImageUrl] = useState("");
  const [formMessage, setFormMessage] = useState("");
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState("");
  const [formPrivacy, setFormPrivacy] = useState("public");
  const [selectedPost, setSelectedPost] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }
    fetchWithAuth("/api/v1/posters/", {}, navigate)
      .then(async (res) => {
        if (!res.ok) throw new Error("Lỗi tải danh sách bài viết");
        const data = await res.json();
        setPosts(data);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [navigate, formLoading]);

  // Xử lý chọn ảnh
  function handleImageChange(e) {
    const file = e.target.files[0];
    setFormImage(file);
    if (file) {
      const url = URL.createObjectURL(file);
      setFormImageUrl(url);
    } else {
      setFormImageUrl("");
    }
  }

  // Xử lý đăng bài
  async function handleSubmit(e) {
    e.preventDefault();
    setFormError("");
    if (!formImage) {
      setFormError("Vui lòng chọn ảnh!");
      return;
    }
    if (!formMessage.trim()) {
      setFormError("Vui lòng nhập lời nhắn!");
      return;
    }
    setFormLoading(true);
    try {
      const formData = new FormData();
      formData.append("image", formImage);
      formData.append("message", formMessage);
      formData.append("privacy", formPrivacy);
      const res = await fetchWithAuth(
        "/api/v1/posters/",
        {
          method: "POST",
          body: formData,
        },
        navigate,
      );
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Lỗi đăng bài");
      }
      setShowForm(false);
      setFormImage(null);
      setFormImageUrl("");
      setFormMessage("");
      setFormPrivacy("private");
      setFormLoading(false);
    } catch (e) {
      setFormError(e.message);
      setFormLoading(false);
    }
  }

  if (loading)
    return (
      <div style={{ textAlign: "center", marginTop: 40 }}>Đang tải...</div>
    );
  if (error)
    return (
      <div
        style={{
          color: "var(--color-on-background, #222)",
          textAlign: "center",
          marginTop: 40,
        }}
      >
        {error}
      </div>
    );

  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100%",
        boxSizing: "border-box",
        background: "var(--color-background, #fff)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: 0,
        margin: 0,
        overflowX: "hidden",
        color: "var(--color-on-background, #222)",
      }}
    >
      {/* Nút Đăng xuất + Đăng bài */}
      <div
        style={{
          width: "100%",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: 16,
        }}
      >
        <button
          onClick={async () => {
            const refresh = localStorage.getItem("refresh_token");
            if (refresh) {
              try {
                await fetch("/api/v1/logout", {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("access_token")}`,
                  },
                  body: JSON.stringify({ refresh_token: refresh }),
                });
              } catch {
                /* ignore */
              }
            }
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            navigate("/login");
          }}
          style={{
            background: "var(--color-primary, #7C4DFF)",
            color: "#fff",
            border: "none",
            borderRadius: 6,
            padding: "8px 20px",
            fontSize: 16,
            cursor: "pointer",
            fontWeight: 500,
          }}
        >
          Đăng xuất
        </button>
        <button
          onClick={() => setShowForm(true)}
          style={{
            background: "var(--color-secondary, #00BFAE)",
            color: "#fff",
            border: "none",
            borderRadius: 6,
            padding: "8px 20px",
            fontSize: 16,
            cursor: "pointer",
            fontWeight: 500,
          }}
        >
          Đăng bài viết
        </button>
      </div>
      {/* Form đăng bài */}
      {showForm && (
        <form
          onSubmit={handleSubmit}
          style={{
            background: "#fff",
            border: "1px solid #eee",
            borderRadius: 12,
            boxShadow: "0 2px 8px #7C4DFF11",
            padding: 24,
            marginBottom: 32,
            width: "100%",
            maxWidth: 500,
            display: "flex",
            flexDirection: "column",
            gap: 16,
            position: "relative",
          }}
        >
          <div
            style={{
              fontWeight: 600,
              fontSize: 20,
              marginBottom: 8,
              color: "var(--color-on-background, #222)",
            }}
          >
            Đăng bài viết mới
          </div>
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            disabled={formLoading}
          />
          {formImageUrl && (
            <img
              src={formImageUrl}
              alt="Preview"
              style={{
                width: "100%",
                maxHeight: 300,
                objectFit: "cover",
                borderRadius: 8,
              }}
            />
          )}
          <textarea
            placeholder="Nhập lời nhắn..."
            value={formMessage}
            onChange={(e) => setFormMessage(e.target.value)}
            rows={3}
            style={{
              padding: 16,
              borderRadius: 8,
              border: "2px solid #bdbdbd",
              fontSize: 16,
              resize: "vertical",
              color: "var(--color-on-background, #222)",
              background: "#fff",
              outline: "none",
              boxShadow: "0 1px 4px #0001",
              transition: "border 0.2s",
            }}
            onFocus={(e) => (e.target.style.border = "2px solid #7c4dff")}
            onBlur={(e) => (e.target.style.border = "2px solid #bdbdbd")}
            disabled={formLoading}
          />
          {/* Chọn privacy */}
          <div
            style={{
              display: "flex",
              gap: 16,
              alignItems: "center",
              color: "var(--color-on-background, #222)",
            }}
          >
            <span>Quyền riêng tư:</span>
            <label
              style={{
                display: "flex",
                alignItems: "center",
                gap: 4,
                background: "#e3f2fd",
                color: "#1565c0",
                borderRadius: 8,
                padding: "2px 10px",
                fontWeight: 500,
              }}
            >
              <input
                type="radio"
                name="privacy"
                value="public"
                checked={formPrivacy === "public"}
                onChange={() => setFormPrivacy("public")}
                disabled={formLoading}
                style={{ accentColor: "#1565c0" }}
              />
              Công khai
            </label>
            <label
              style={{
                display: "flex",
                alignItems: "center",
                gap: 4,
                background: "#e8f5e9",
                color: "#388e3c",
                borderRadius: 8,
                padding: "2px 10px",
                fontWeight: 500,
              }}
            >
              <input
                type="radio"
                name="privacy"
                value="community"
                checked={formPrivacy === "community"}
                onChange={() => setFormPrivacy("community")}
                disabled={formLoading}
                style={{ accentColor: "#388e3c" }}
              />
              Cộng đồng
            </label>
            <label
              style={{
                display: "flex",
                alignItems: "center",
                gap: 4,
                background: "#ffebee",
                color: "#b71c1c",
                borderRadius: 8,
                padding: "2px 10px",
                fontWeight: 500,
              }}
            >
              <input
                type="radio"
                name="privacy"
                value="private"
                checked={formPrivacy === "private"}
                onChange={() => setFormPrivacy("private")}
                disabled={formLoading}
                style={{ accentColor: "#b71c1c" }}
              />
              Riêng tư
            </label>
          </div>
          {formError && (
            <div style={{ color: "var(--color-error)", marginBottom: 8 }}>
              {formError}
            </div>
          )}
          <div style={{ display: "flex", gap: 12 }}>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              style={{
                background: "#eee",
                color: "var(--color-on-background, #222)",
                border: "none",
                borderRadius: 6,
                padding: "8px 20px",
                fontSize: 16,
                cursor: "pointer",
              }}
              disabled={formLoading}
            >
              Huỷ
            </button>
            <button
              type="submit"
              style={{
                background: "var(--color-primary,#7C4DFF)",
                color: "#fff",
                border: "none",
                borderRadius: 6,
                padding: "8px 20px",
                fontSize: 16,
                cursor: "pointer",
                fontWeight: 500,
              }}
              disabled={formLoading}
            >
              {formLoading ? "Đang đăng..." : "Đăng bài"}
            </button>
          </div>
        </form>
      )}
      <div style={{ width: "100%" }}>
        {posts.length === 0 && <div>Chưa có bài viết nào.</div>}
        {posts.map((post) => (
          <PostItem
            key={post.id}
            post={post}
            onClick={() => setSelectedPost(post)}
          />
        ))}
        <Modal open={!!selectedPost} onClose={() => setSelectedPost(null)}>
          {selectedPost && <PostDetail post={selectedPost} />}
        </Modal>
      </div>
    </div>
  );
}

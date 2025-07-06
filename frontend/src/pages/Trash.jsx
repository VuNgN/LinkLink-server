import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../utils/api";
import PostItem from "../components/PostItem";
import Modal from "../components/Modal";

export default function Trash() {
  const navigate = useNavigate();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showConfirm, setShowConfirm] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  const [showConfirmAll, setShowConfirmAll] = useState(false);

  async function reload() {
    setLoading(true);
    setError("");
    try {
      const res = await api.get("/api/v1/posters/deleted");
      if (!res.ok) throw new Error("Lỗi tải thùng rác");
      const data = await res.json();
      setPosts(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    reload();
  }, []);

  async function handleHardDelete(id) {
    setError("");
    try {
      const res = await api.delete(`/api/v1/posters/${id}/hard`);
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Lỗi xoá vĩnh viễn");
      }
      reload();
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleHardDeleteAll() {
    setError("");
    try {
      const res = await api.delete(`/api/v1/posters/deleted/hard`);
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Lỗi xoá tất cả vĩnh viễn");
      }
      reload();
    } catch (e) {
      setError(e.message);
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
          color: "var(--color-error)",
          textAlign: "center",
          marginTop: 40,
        }}
      >
        {error}
      </div>
    );

  return (
    <div style={{ minHeight: "100vh", background: "#fff", padding: 24 }}>
      <div style={{ maxWidth: 700, margin: "0 auto" }}>
        <h2 style={{ fontWeight: 700, fontSize: 28, marginBottom: 24 }}>
          Thùng rác
        </h2>
        <button
          onClick={() => navigate("/")}
          style={{
            marginBottom: 24,
            background: "#eee",
            color: "#222",
            border: "none",
            borderRadius: 6,
            padding: "8px 20px",
            fontSize: 16,
            cursor: "pointer",
          }}
        >
          Quay lại trang chủ
        </button>
        {posts.length === 0 && <div>Thùng rác trống.</div>}
        {posts.length > 0 && (
          <div style={{ marginBottom: 24 }}>
            <button
              onClick={() => setShowConfirmAll(true)}
              style={{
                background: "#ff5252",
                color: "#fff",
                border: "none",
                borderRadius: 6,
                padding: "8px 20px",
                fontSize: 16,
                cursor: "pointer",
                fontWeight: 500,
              }}
            >
              Xoá tất cả vĩnh viễn
            </button>
          </div>
        )}
        <div style={{ width: "100%" }}>
          {posts.map((post) => (
            <div
              key={post.id}
              style={{ marginBottom: 16, position: "relative" }}
            >
              <PostItem post={post} />
              <button
                onClick={() => {
                  setDeleteId(post.id);
                  setShowConfirm(true);
                }}
                style={{
                  position: "absolute",
                  top: 8,
                  right: 8,
                  background: "#ff5252",
                  color: "#fff",
                  border: "none",
                  borderRadius: 6,
                  padding: "6px 16px",
                  fontSize: 14,
                  cursor: "pointer",
                  fontWeight: 500,
                }}
              >
                Xoá vĩnh viễn
              </button>
            </div>
          ))}
        </div>
      </div>
      {/* Confirm single delete */}
      {showConfirm && (
        <Modal open={showConfirm} onClose={() => setShowConfirm(false)}>
          <div style={{ padding: 24, maxWidth: 400 }}>
            <div style={{ fontWeight: 600, fontSize: 18, marginBottom: 16 }}>
              Xác nhận xoá vĩnh viễn
            </div>
            <div style={{ marginBottom: 24 }}>
              Bạn có chắc chắn muốn xoá vĩnh viễn bài viết này? Hành động này
              không thể hoàn tác.
            </div>
            <div style={{ display: "flex", gap: 12 }}>
              <button
                onClick={() => setShowConfirm(false)}
                style={{
                  background: "#eee",
                  color: "#222",
                  border: "none",
                  borderRadius: 6,
                  padding: "8px 20px",
                  fontSize: 16,
                  cursor: "pointer",
                }}
              >
                Huỷ
              </button>
              <button
                onClick={() => {
                  handleHardDelete(deleteId);
                  setShowConfirm(false);
                }}
                style={{
                  background: "#ff5252",
                  color: "#fff",
                  border: "none",
                  borderRadius: 6,
                  padding: "8px 20px",
                  fontSize: 16,
                  cursor: "pointer",
                  fontWeight: 500,
                }}
              >
                Xoá vĩnh viễn
              </button>
            </div>
          </div>
        </Modal>
      )}
      {/* Confirm all delete */}
      {showConfirmAll && (
        <Modal open={showConfirmAll} onClose={() => setShowConfirmAll(false)}>
          <div style={{ padding: 24, maxWidth: 400 }}>
            <div style={{ fontWeight: 600, fontSize: 18, marginBottom: 16 }}>
              Xác nhận xoá tất cả vĩnh viễn
            </div>
            <div style={{ marginBottom: 24 }}>
              Bạn có chắc chắn muốn xoá vĩnh viễn tất cả bài viết trong thùng
              rác? Hành động này không thể hoàn tác.
            </div>
            <div style={{ display: "flex", gap: 12 }}>
              <button
                onClick={() => setShowConfirmAll(false)}
                style={{
                  background: "#eee",
                  color: "#222",
                  border: "none",
                  borderRadius: 6,
                  padding: "8px 20px",
                  fontSize: 16,
                  cursor: "pointer",
                }}
              >
                Huỷ
              </button>
              <button
                onClick={() => {
                  handleHardDeleteAll();
                  setShowConfirmAll(false);
                }}
                style={{
                  background: "#ff5252",
                  color: "#fff",
                  border: "none",
                  borderRadius: 6,
                  padding: "8px 20px",
                  fontSize: 16,
                  cursor: "pointer",
                  fontWeight: 500,
                }}
              >
                Xoá tất cả vĩnh viễn
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import PostDetail from "../components/PostDetail";
import { api } from "../utils/api";
import PostFormModal from "../components/PostFormModal";
import Modal from "../components/Modal";

export default function PostDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showEdit, setShowEdit] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError("");
    api
      .get(`/api/v1/posters/${id}`, {}, navigate)
      .then(async (res) => {
        if (res.status === 401) {
          // Chưa đăng nhập, chuyển hướng login kèm redirect
          navigate(`/login?redirect=/post/${id}`);
          return;
        }
        if (res.status === 404) {
          // Bài viết không tồn tại hoặc đã bị xóa
          setError("Bài viết này không tồn tại hoặc đã bị xóa.");
          setPost(null);
          setLoading(false);
          return;
        }
        if (res.status === 451) {
          // Không phải chủ post, không có quyền xem bài private
          const data = await res.json().catch(() => ({}));
          setError(
            data.detail || "Chỉ chủ bài viết mới có quyền xem bài viết này!",
          );
          setPost(null);
          setLoading(false);
          return;
        }
        if (res.status === 403) {
          // Đã đăng nhập nhưng không có quyền với community
          const data = await res.json().catch(() => ({}));
          setError(data.detail || "Bạn không có quyền xem bài viết này!");
          setPost(null);
          setLoading(false);
          return;
        }
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(
            data.detail || "Không tìm thấy bài viết hoặc không có quyền xem!",
          );
        }
        return res.json();
      })
      .then((data) => {
        if (data) setPost(data);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id, navigate, showEdit]);

  async function handleDelete() {
    setError("");
    try {
      const res = await api.delete(`/api/v1/posters/${id}`);
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Lỗi xoá bài viết");
      }
      navigate("/");
    } catch (e) {
      setError(e.message);
    }
  }

  // Xử lý đăng bài thành công: reload post
  async function reloadPost() {
    setLoading(true);
    setError("");
    try {
      const res = await api.get(`/api/v1/posters/${id}`, {}, navigate);
      if (res.status === 401) {
        navigate(`/login?redirect=/post/${id}`);
        return;
      }
      if (res.status === 404) {
        // Bài viết không tồn tại hoặc đã bị xóa
        setError("Bài viết này không tồn tại hoặc đã bị xóa.");
        setPost(null);
        setLoading(false);
        return;
      }
      if (res.status === 451) {
        const data = await res.json().catch(() => ({}));
        setError(
          data.detail || "Chỉ chủ bài viết mới có quyền xem bài viết này!",
        );
        setPost(null);
        setLoading(false);
        return;
      }
      if (res.status === 403) {
        const data = await res.json().catch(() => ({}));
        setError(data.detail || "Bạn không có quyền xem bài viết này!");
        setPost(null);
        setLoading(false);
        return;
      }
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(
          data.detail || "Không tìm thấy bài viết hoặc không có quyền xem!",
        );
      }
      const data = await res.json();
      setPost(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
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
  if (!post) return null;

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "var(--color-background, #fff)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 24,
      }}
    >
      <div style={{ width: "100%", maxWidth: 700 }}>
        <PostDetail
          post={post}
          onEdit={() => setShowEdit(true)}
          onDelete={() => setShowDeleteConfirm(true)}
        />
      </div>
      {/* Edit Modal */}
      {showEdit && (
        <PostFormModal
          open={showEdit}
          onClose={() => setShowEdit(false)}
          onSuccess={() => {
            setShowEdit(false);
            reloadPost(); // Reload to get updated post
          }}
          post={post}
          mode="edit"
        />
      )}
      {/* Delete Confirm Modal */}
      {showDeleteConfirm && (
        <Modal
          open={showDeleteConfirm}
          onClose={() => setShowDeleteConfirm(false)}
        >
          <div style={{ padding: 24, maxWidth: 400 }}>
            <div style={{ fontWeight: 600, fontSize: 18, marginBottom: 16 }}>
              Xác nhận xoá bài viết
            </div>
            <div style={{ marginBottom: 24 }}>
              Bạn có chắc chắn muốn xoá bài viết này không? Bài viết sẽ được
              chuyển vào thùng rác và có thể khôi phục hoặc xoá vĩnh viễn sau
              này.
            </div>
            <div style={{ display: "flex", gap: 12 }}>
              <button
                onClick={() => setShowDeleteConfirm(false)}
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
                onClick={handleDelete}
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
                Xoá
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

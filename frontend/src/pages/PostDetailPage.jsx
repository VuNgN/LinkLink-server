import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import PostDetail from "../components/PostDetail";
import { api } from "../utils/api";

export default function PostDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
  }, [id, navigate]);

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
        <PostDetail post={post} />
      </div>
    </div>
  );
}

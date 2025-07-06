import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../utils/api";
import PostItem from "../components/PostItem";
import PostDetail from "../components/PostDetail";
import Modal from "../components/Modal";
import PostFormModal from "../components/PostFormModal";

export default function Home() {
  const navigate = useNavigate();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [hasNewPost, setHasNewPost] = useState(false);
  const [selectedPost, setSelectedPost] = useState(null);
  const [showEdit, setShowEdit] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [postToEdit, setPostToEdit] = useState(null);
  const [postToDelete, setPostToDelete] = useState(null);

  useEffect(() => {
    api
      .get("/api/v1/posters/", {}, navigate)
      .then(async (res) => {
        if (!res.ok) throw new Error("Lỗi tải danh sách bài viết");
        const data = await res.json();
        setPosts(data);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
    // WebSocket notification for new posts
    let ws;
    let closed = false;
    function getUsernameFromToken() {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) return "";
        const payload = JSON.parse(atob(token.split(".")[1]));
        return payload.username || "";
      } catch {
        return "";
      }
    }
    const username = getUsernameFromToken();
    function connectWS() {
      ws = new window.WebSocket(
        `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/ws/posts/notify?username=${encodeURIComponent(username)}`,
      );
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.event === "new_post") {
            setHasNewPost(true);
          }
        } catch {
          // ignore
        }
      };
      ws.onclose = () => {
        if (!closed) setTimeout(connectWS, 2000); // reconnect
      };
    }
    connectWS();
    return () => {
      closed = true;
      if (ws) ws.close();
    };
  }, [navigate]);

  // Xử lý đăng bài thành công: reload post
  async function reloadPosts() {
    setLoading(true);
    try {
      const res = await api.get("/api/v1/posters/", {}, navigate);
      if (!res.ok) throw new Error("Lỗi tải danh sách bài viết");
      const data = await res.json();
      setPosts(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  // Handle edit post
  const handleEdit = (post) => {
    setPostToEdit(post);
    setShowEdit(true);
    setSelectedPost(null); // Close the detail modal
  };

  // Handle delete post
  const handleDelete = (post) => {
    setPostToDelete(post);
    setShowDeleteConfirm(true);
    setSelectedPost(null); // Close the detail modal
  };

  // Confirm delete
  const confirmDelete = async () => {
    if (!postToDelete) return;

    setError("");
    try {
      const res = await api.delete(`/api/v1/posters/${postToDelete.id}`);
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Lỗi xoá bài viết");
      }
      // Remove the deleted post from the list
      setPosts(posts.filter((p) => p.id !== postToDelete.id));
      setShowDeleteConfirm(false);
      setPostToDelete(null);
    } catch (e) {
      setError(e.message);
    }
  };

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
        <div style={{ display: "flex", gap: 12 }}>
          <button
            onClick={async () => {
              try {
                await fetch("/api/v1/logout", {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("access_token")}`,
                  },
                  credentials: "include",
                });
              } catch {
                // ignore
              }
              localStorage.removeItem("access_token");
              localStorage.removeItem("username");
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
          <button
            onClick={() => navigate("/trash")}
            style={{
              background: "#757575",
              color: "#fff",
              border: "none",
              borderRadius: 6,
              padding: "8px 20px",
              fontSize: 16,
              cursor: "pointer",
              fontWeight: 500,
            }}
          >
            Thùng rác
          </button>
        </div>
      </div>
      {/* Popup đăng bài viết */}
      <PostFormModal
        open={showForm}
        onClose={() => setShowForm(false)}
        onSuccess={reloadPosts}
      />
      {/* Nút thông báo có bài viết mới */}
      {hasNewPost && (
        <div style={{ margin: "16px 0" }}>
          <button
            onClick={async () => {
              setLoading(true);
              setHasNewPost(false);
              try {
                const res = await api.get("/api/v1/posters/", {}, navigate);
                if (!res.ok) throw new Error("Lỗi tải danh sách bài viết");
                const data = await res.json();
                setPosts(data);
              } catch (e) {
                setError(e.message);
              } finally {
                setLoading(false);
              }
            }}
            style={{
              background: "#ffeb3b",
              color: "#222",
              border: "1px solid #fbc02d",
              borderRadius: 8,
              padding: "8px 20px",
              fontSize: 16,
              fontWeight: 600,
              cursor: "pointer",
              boxShadow: "0 2px 8px #fbc02d33",
            }}
          >
            Có bài viết mới, refresh lại
          </button>
        </div>
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
          {selectedPost && (
            <PostDetail
              post={selectedPost}
              onEdit={() => handleEdit(selectedPost)}
              onDelete={() => handleDelete(selectedPost)}
            />
          )}
        </Modal>
      </div>

      {/* Edit Modal */}
      {showEdit && postToEdit && (
        <PostFormModal
          open={showEdit}
          onClose={() => {
            setShowEdit(false);
            setPostToEdit(null);
          }}
          onSuccess={() => {
            setShowEdit(false);
            setPostToEdit(null);
            reloadPosts(); // Reload to get updated post
          }}
          post={postToEdit}
          mode="edit"
        />
      )}

      {/* Delete Confirm Modal */}
      {showDeleteConfirm && (
        <Modal
          open={showDeleteConfirm}
          onClose={() => {
            setShowDeleteConfirm(false);
            setPostToDelete(null);
          }}
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
                onClick={() => {
                  setShowDeleteConfirm(false);
                  setPostToDelete(null);
                }}
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
                onClick={confirmDelete}
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

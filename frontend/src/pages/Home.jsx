import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import fetchWithAuth from "../utils/fetchWithAuth";
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
        } catch {}
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
      const res = await fetchWithAuth("/api/v1/posters/", {}, navigate);
      if (!res.ok) throw new Error("Lỗi tải danh sách bài viết");
      const data = await res.json();
      setPosts(data);
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
                const res = await fetchWithAuth(
                  "/api/v1/posters/",
                  {},
                  navigate,
                );
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
          {selectedPost && <PostDetail post={selectedPost} />}
        </Modal>
      </div>
    </div>
  );
}

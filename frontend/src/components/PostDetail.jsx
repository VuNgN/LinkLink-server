import React from "react";

function PostDetail({ post, onEdit, onDelete }) {
  if (!post) return null;
  let imageUrl = post.image_path;
  if (imageUrl && !imageUrl.startsWith("/uploads/")) {
    const idx = imageUrl.lastIndexOf("/uploads/");
    if (idx !== -1) imageUrl = imageUrl.slice(idx);
  }
  let createdAt = "";
  if (post.created_at) {
    const d = new Date(post.created_at);
    createdAt = d.toLocaleString(undefined, { hour12: false });
  }
  // Get current user
  const currentUsername =
    localStorage.getItem("username") ||
    (() => {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) return "";
        const payload = JSON.parse(atob(token.split(".")[1]));
        return payload.username || "";
      } catch {
        return "";
      }
    })();
  const isOwner = post.username === currentUsername;

  return (
    <div
      style={{
        maxHeight: "90vh",
        overflow: "auto",
        padding: "32px 0",
        boxSizing: "border-box",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <img
        src={imageUrl}
        alt={post.message}
        style={{
          width: "100%",
          maxHeight: "55vh",
          objectFit: "contain",
          borderRadius: 8,
          marginBottom: 16,
          background: "#fafafa",
        }}
      />
      <div style={{ marginBottom: 8 }}>
        <span
          style={{
            fontSize: 14,
            color:
              post.privacy === "public"
                ? "#2196f3"
                : post.privacy === "community"
                  ? "#388e3c"
                  : "#b71c1c",
            fontWeight: 500,
            display: "flex",
            alignItems: "center",
            gap: 4,
          }}
        >
          {post.privacy === "public"
            ? "🌐 Công khai"
            : post.privacy === "community"
              ? "👥 Cộng đồng"
              : "🔒 Riêng tư"}
        </span>
      </div>
      <div
        style={{
          fontSize: 18,
          fontWeight: 600,
          marginBottom: 8,
          color: "var(--color-on-surface, #222)",
        }}
      >
        {post.message}
      </div>
      <div style={{ color: "#888", fontSize: 15, marginBottom: 8 }}>
        🕒 {createdAt}
      </div>
      <div style={{ color: "#888", fontSize: 15, marginBottom: 16 }}>
        👤 {post.username}
      </div>
      {isOwner && (
        <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
          <button
            onClick={onEdit}
            style={{
              background: "#7C4DFF",
              color: "#fff",
              border: "none",
              borderRadius: 6,
              padding: "8px 20px",
              fontSize: 16,
              cursor: "pointer",
              fontWeight: 500,
            }}
          >
            Chỉnh sửa
          </button>
          <button
            onClick={onDelete}
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
            Xoá bài viết
          </button>
        </div>
      )}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: 24,
          marginTop: 24,
        }}
      >
        <a
          href={imageUrl}
          download
          style={{
            display: "inline-block",
            background: "var(--color-primary,#7C4DFF)",
            color: "#fff",
            borderRadius: 20,
            padding: "10px 28px",
            textDecoration: "none",
            fontWeight: 700,
            fontSize: 18,
            boxShadow: "0 2px 8px #7c4dff22",
          }}
        >
          ⬇️ Tải ảnh xuống
        </a>
        <button
          type="button"
          style={{
            background: "#e3f2fd",
            color: "#1565c0",
            border: "none",
            borderRadius: 20,
            padding: "10px 28px",
            fontWeight: 700,
            cursor: "pointer",
            fontSize: 18,
            boxShadow: "0 2px 8px #2196f322",
            display: "flex",
            alignItems: "center",
            gap: 8,
            transition: "background 0.2s",
          }}
          onClick={() => {
            const url = window.location.origin + "/post/" + post.id;
            navigator.clipboard.writeText(url);
            window.alert("Đã copy link bài viết!");
          }}
        >
          <span style={{ fontSize: 22, marginRight: 6 }}>📤</span>{" "}
          <span>Chia sẻ</span>
        </button>
      </div>
    </div>
  );
}

export default PostDetail;

import React from "react";

function PostDetail({ post }) {
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
  return (
    <div>
      <img
        src={imageUrl}
        alt={post.message}
        style={{
          width: "100%",
          maxHeight: 600,
          objectFit: "contain",
          borderRadius: 8,
          marginBottom: 16,
          background: "#fafafa",
        }}
      />
      <div
        style={{
          fontSize: 18,
          fontWeight: 600,
          marginBottom: 8,
          color: "#222",
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
      <a
        href={imageUrl}
        download
        style={{
          display: "inline-block",
          background: "var(--color-primary,#7C4DFF)",
          color: "#fff",
          borderRadius: 6,
          padding: "10px 24px",
          textDecoration: "none",
          fontWeight: 500,
        }}
      >
        Tải ảnh xuống
      </a>
    </div>
  );
}

export default PostDetail;

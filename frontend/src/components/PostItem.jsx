import React, { memo } from "react";

const PostItem = memo(function PostItem({ post, onClick }) {
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
    <div
      onClick={onClick}
      style={{
        background: "var(--color-surface)",
        borderRadius: 12,
        boxShadow: "0 2px 8px #7C4DFF11",
        margin: "0 auto 24px auto",
        padding: 16,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        width: "100%",
        maxWidth: 600,
        cursor: "pointer",
        transition: "box-shadow 0.2s",
      }}
    >
      <img
        src={imageUrl}
        alt={post.message}
        style={{
          width: "100%",
          height: "auto",
          borderRadius: 8,
          marginBottom: 12,
          objectFit: "cover",
          aspectRatio: "4/3",
          maxHeight: 400,
        }}
        loading="lazy"
      />
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          width: "100%",
          marginBottom: 8,
          fontSize: 14,
          color: "#888",
        }}
      >
        <span>🕒 {createdAt}</span>
        <span>👤 {post.username}</span>
      </div>
      <div
        style={{
          color: "var(--color-on-surface, #222)",
          fontSize: 16,
          textAlign: "center",
          wordBreak: "break-word",
        }}
      >
        {post.message}
      </div>
    </div>
  );
});

export default PostItem;

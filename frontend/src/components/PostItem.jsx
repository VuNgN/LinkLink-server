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
          width: "100%",
          display: "flex",
          alignItems: "center",
          marginBottom: 4,
          gap: 8,
          color: "var(--color-on-background, #222)",
        }}
      >
        <span
          style={{
            fontSize: 13,
            color:
              post.privacy === "public"
                ? "#1565c0"
                : post.privacy === "community"
                  ? "#388e3c"
                  : "#b71c1c",
            background:
              post.privacy === "public"
                ? "#e3f2fd"
                : post.privacy === "community"
                  ? "#e8f5e9"
                  : "#ffebee",
            fontWeight: 500,
            display: "inline-flex",
            alignItems: "center",
            gap: 4,
            borderRadius: 8,
            padding: "2px 10px",
            boxShadow: "0 1px 2px #0001",
          }}
        >
          {post.privacy === "public"
            ? "🌐 Công khai"
            : post.privacy === "community"
              ? "👥 Cộng đồng"
              : "🔒 Riêng tư"}
        </span>
        <button
          type="button"
          style={{
            marginLeft: "auto",
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
          onClick={(e) => {
            e.stopPropagation();
            const url = window.location.origin + "/post/" + post.id;
            navigator.clipboard.writeText(url);
            window.alert("Đã copy link bài viết!");
          }}
        >
          <span style={{ fontSize: 22, marginRight: 6 }}>📤</span>{" "}
          <span>Chia sẻ</span>
        </button>
      </div>
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

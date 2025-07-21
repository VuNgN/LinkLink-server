import React, { memo } from "react";

const PostItem = memo(function PostItem({ post, onClick, showActions = true }) {
  let imageUrls = [];
  if (
    Array.isArray(post.images) &&
    post.images.length > 0 &&
    post.images[0].file_path
  ) {
    imageUrls = post.images.map((img) => img.file_path);
  } else if (post.file_path || post.image_path) {
    imageUrls = [post.file_path || post.image_path];
  }
  let createdAt = "";
  if (post.created_at) {
    const d = new Date(post.created_at);
    createdAt = d.toLocaleString(undefined, { hour12: false });
  }
  return (
    <div
      onClick={() => onClick(post)}
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
        boxSizing: "border-box",
      }}
    >
      {/* Image grid for up to 4 images */}
      <div style={{
        width: "100%",
        display: "grid",
        gridTemplateColumns: imageUrls.length > 1 ? "1fr 1fr" : "1fr",
        gridTemplateRows: imageUrls.length > 2 ? "1fr 1fr" : "1fr",
        gap: 6,
        marginBottom: 12,
        borderRadius: 8,
        overflow: "hidden",
        aspectRatio: imageUrls.length === 1 ? "4/3" : "1/1",
        background: "#fafafa"
      }}>
        {imageUrls.slice(0, 4).map((url, idx) => (
          <div key={url} style={{
            position: "relative",
            width: "100%",
            height: "100%",
            overflow: "hidden",
            borderRadius: 8,
            gridColumn: imageUrls.length === 3 && idx === 2 ? "1 / span 2" : undefined,
            aspectRatio: imageUrls.length === 1 ? "4/3" : "1/1",
            cursor: "pointer"
          }}
          onClick={e => {
            e.stopPropagation();
            onClick(post, idx);
          }}
          >
            <img
              src={url}
              alt={post.message}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                display: "block",
                borderRadius: 8,
                aspectRatio: imageUrls.length === 1 ? "4/3" : "1/1"
              }}
              loading="lazy"
            />
            {/* Overlay for more images */}
            {idx === 3 && imageUrls.length > 4 && (
              <div style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                background: "rgba(0,0,0,0.45)",
                color: "#fff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 32,
                fontWeight: 700,
                borderRadius: 8
              }}>
                +{imageUrls.length - 4}
              </div>
            )}
          </div>
        ))}
      </div>
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
        {showActions && (
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
        )}
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

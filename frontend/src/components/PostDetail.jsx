import React from "react";

function PostDetail({ post, onEdit, onDelete, initialImageIndex = 0 }) {
  if (!post) return null;
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
  const [carouselIdx, setCarouselIdx] = React.useState(initialImageIndex);

  React.useEffect(() => {
    setCarouselIdx(initialImageIndex);
  }, [initialImageIndex]);

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
      {/* Carousel for images */}
      {imageUrls.length > 1 ? (
        <div style={{
          width: "100%",
          maxWidth: 600,
          position: "relative",
          marginBottom: 16,
          display: "flex",
          alignItems: "center",
          justifyContent: "center"
        }}>
          <button
            onClick={() => setCarouselIdx((prev) => (prev - 1 + imageUrls.length) % imageUrls.length)}
            style={{
              position: "absolute",
              left: 0,
              top: "50%",
              transform: "translateY(-50%)",
              background: "rgba(255,255,255,0.7)",
              border: "none",
              borderRadius: "50%",
              width: 36,
              height: 36,
              fontSize: 22,
              fontWeight: 700,
              cursor: "pointer",
              zIndex: 2,
              display: imageUrls.length > 1 ? "flex" : "none",
              alignItems: "center",
              justifyContent: "center",
              padding: 0
            }}
            aria-label="Trước"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M13 16L8 10L13 4" stroke="#7C4DFF" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          <div style={{
            width: "100%",
            maxWidth: 600,
            overflow: "hidden",
            borderRadius: 8,
            background: "#fafafa"
          }}>
            <img
              src={imageUrls[carouselIdx]}
              alt={post.message}
              style={{
                width: "100%",
                maxHeight: "55vh",
                objectFit: "contain",
                borderRadius: 8,
                display: "block",
                background: "#fafafa",
                transition: "all 0.3s"
              }}
            />
          </div>
          <button
            onClick={() => setCarouselIdx((prev) => (prev + 1) % imageUrls.length)}
            style={{
              position: "absolute",
              right: 0,
              top: "50%",
              transform: "translateY(-50%)",
              background: "rgba(255,255,255,0.7)",
              border: "none",
              borderRadius: "50%",
              width: 36,
              height: 36,
              fontSize: 22,
              fontWeight: 700,
              cursor: "pointer",
              zIndex: 2,
              display: imageUrls.length > 1 ? "flex" : "none",
              alignItems: "center",
              justifyContent: "center",
              padding: 0
            }}
            aria-label="Sau"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 4L12 10L7 16" stroke="#7C4DFF" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          {/* Dots indicator */}
          <div style={{
            position: "absolute",
            bottom: 8,
            left: "50%",
            transform: "translateX(-50%)",
            display: "flex",
            gap: 6
          }}>
            {imageUrls.map((_, idx) => (
              <span
                key={idx}
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: "50%",
                  background: idx === carouselIdx ? "#7C4DFF" : "#ccc",
                  display: "inline-block"
                }}
              />
            ))}
          </div>
        </div>
      ) : imageUrls.length === 1 ? (
        <img
          src={imageUrls[0]}
          alt={post.message}
          style={{
            width: "100%",
            maxHeight: "55vh",
            objectFit: "contain",
            borderRadius: 8,
            marginBottom: 16,
            background: "#fafafa"
          }}
        />
      ) : null}
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
        {/* Download first image only for now */}
        <a
          href={imageUrls[0]}
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

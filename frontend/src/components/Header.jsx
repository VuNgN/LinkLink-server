import React from "react";

const Header = ({
  isAuthenticated,
  onLogin,
  onLogout,
  onCreatePost,
  onNavigateToTrash,
}) => {
  return (
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
        {isAuthenticated ? (
          <>
            <button
              onClick={onLogout}
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
              onClick={onCreatePost}
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
              onClick={onNavigateToTrash}
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
          </>
        ) : (
          <button
            onClick={onLogin}
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
            Đăng nhập
          </button>
        )}
      </div>
    </div>
  );
};

export default Header;

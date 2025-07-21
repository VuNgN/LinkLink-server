import React from "react";

const closeBtnStyle = {
  position: "absolute",
  top: 12,
  right: 12,
  background: "#fff",
  border: "1.5px solid #bbb",
  borderRadius: "50%",
  width: 40,
  height: 40,
  fontSize: 26,
  fontWeight: 700,
  color: "#333",
  cursor: "pointer",
  lineHeight: "40px",
  textAlign: "center",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  boxShadow: "0 2px 8px #0001",
  transition: "background 0.2s, border 0.2s",
  zIndex: 10,
};

function Modal({ open, onClose, children }) {
  if (!open) return null;
  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(0,0,0,0.35)",
        zIndex: 1000,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
      onClick={onClose}
    >
      <div
        style={{
          position: "relative",
          minWidth: 320,
          maxWidth: 700,
          width: "90vw",
          background: "#fff",
          borderRadius: 12,
          boxShadow: "0 2px 16px #0002",
          padding: 24,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {children}
        <button
          onClick={onClose}
          style={closeBtnStyle}
          onMouseOver={(e) => {
            e.currentTarget.style.background = "#e3f2fd";
            e.currentTarget.style.border = "1.5px solid #2196f3";
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = "#fff";
            e.currentTarget.style.border = "1.5px solid #bbb";
          }}
          aria-label="Đóng"
        >
          <span style={{ marginTop: -2, marginLeft: 1 }}>×</span>
        </button>
      </div>
    </div>
  );
}

export default Modal;

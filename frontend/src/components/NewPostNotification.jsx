import React from "react";

const NewPostNotification = ({ onRefresh }) => {
  return (
    <div style={{ margin: "16px 0" }}>
      <button
        onClick={onRefresh}
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
  );
};

export default NewPostNotification;

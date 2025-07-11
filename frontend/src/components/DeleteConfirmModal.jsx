import React from "react";
import Modal from "./Modal";

const DeleteConfirmModal = ({ open, onClose, onConfirm }) => {
  return (
    <Modal open={open} onClose={onClose}>
      <div style={{ padding: 24, maxWidth: 400 }}>
        <div style={{ fontWeight: 600, fontSize: 18, marginBottom: 16 }}>
          Xác nhận xoá bài viết
        </div>
        <div style={{ marginBottom: 24 }}>
          Bạn có chắc chắn muốn xoá bài viết này không? Bài viết sẽ được chuyển
          vào thùng rác và có thể khôi phục hoặc xoá vĩnh viễn sau này.
        </div>
        <div style={{ display: "flex", gap: 12 }}>
          <button
            onClick={onClose}
            style={{
              background: "#eee",
              color: "#222",
              border: "none",
              borderRadius: 6,
              padding: "8px 20px",
              fontSize: 16,
              cursor: "pointer",
            }}
          >
            Huỷ
          </button>
          <button
            onClick={onConfirm}
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
            Xoá
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default DeleteConfirmModal;

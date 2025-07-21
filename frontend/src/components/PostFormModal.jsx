import React, { useState } from "react";
import Modal from "./Modal";
import { api } from "../utils/api";

export default function PostFormModal({
  open,
  onClose,
  onSuccess,
  post = null,
  mode = "create",
}) {
  const [formImages, setFormImages] = useState([]);
  const [formImageUrls, setFormImageUrls] = useState(
    post ? post.images.map((img) => img.file_path) : [],
  );
  const [formMessage, setFormMessage] = useState(post ? post.message : "");
  const [formPrivacy, setFormPrivacy] = useState(
    post ? post.privacy : "public",
  );
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState("");

  React.useEffect(() => {
    if (post) {
      setFormMessage(post.message || "");
      setFormPrivacy(post.privacy || "public");
      setFormImageUrls(post.images ? post.images.map((img) => img.file_path) : []);
      setFormImages([]);
    } else {
      setFormMessage("");
      setFormPrivacy("public");
      setFormImageUrls([]);
      setFormImages([]);
    }
  }, [post, open]);

  function handleImageChange(e) {
    const files = Array.from(e.target.files);
    setFormImages(files);
    if (files.length > 0) {
      const urls = files.map((file) => URL.createObjectURL(file));
      setFormImageUrls(urls);
    } else {
      setFormImageUrls(post ? post.images.map((img) => img.file_path) : []);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setFormError("");
    if (mode === "create" && formImages.length === 0) {
      setFormError("Vui lòng chọn ảnh!");
      return;
    }
    if (!formMessage.trim()) {
      setFormError("Vui lòng nhập lời nhắn!");
      return;
    }
    setFormLoading(true);
    try {
      const formData = new FormData();
      if (formImages.length > 0) {
        formImages.forEach((image) => {
          formData.append("images", image);
        });
      }
      formData.append("message", formMessage);
      formData.append("privacy", formPrivacy);
      let res;
      if (mode === "edit" && post) {
        res = await api.patch(`/api/v1/posters/${post.id}`, formData);
      } else {
        res = await api.post("/api/v1/posters/", formData);
      }
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(
          data.detail ||
            (mode === "edit" ? "Lỗi cập nhật bài viết" : "Lỗi đăng bài"),
        );
      }
      setFormImages([]);
      setFormImageUrls([]);
      setFormMessage("");
      setFormPrivacy("private");
      setFormLoading(false);
      if (onSuccess) onSuccess();
      if (onClose) onClose();
    } catch (e) {
      setFormError(e.message);
      setFormLoading(false);
    }
  }

  return (
    <Modal open={open} onClose={onClose}>
      <form
        onSubmit={handleSubmit}
        style={{
          background: "#fff",
          border: "1px solid #eee",
          borderRadius: 12,
          boxShadow: "0 2px 8px #7C4DFF11",
          padding: 24,
          marginBottom: 32,
          width: "100%",
          maxWidth: 500,
          boxSizing: "border-box",
          display: "flex",
          flexDirection: "column",
          gap: 16,
          position: "relative",
          maxHeight: "90vh",
          overflowY: "auto",
        }}
      >
        <div
          style={{
            fontWeight: 600,
            fontSize: 20,
            marginBottom: 8,
            color: "var(--color-on-background, #222)",
          }}
        >
          {mode === "edit" ? "Chỉnh sửa bài viết" : "Đăng bài viết mới"}
        </div>
        <input
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          disabled={formLoading}
          multiple
        />
        {formImageUrls.length > 0 && (
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {formImageUrls.map((url, index) => (
              <img
                key={index}
                src={url}
                alt={`Preview ${index}`}
                style={{
                  width: 100,
                  height: 100,
                  objectFit: "cover",
                  borderRadius: 8,
                }}
              />
            ))}
          </div>
        )}
        <textarea
          placeholder="Nhập lời nhắn..."
          value={formMessage}
          onChange={(e) => setFormMessage(e.target.value)}
          rows={3}
          style={{
            padding: 16,
            borderRadius: 8,
            border: "2px solid #bdbdbd",
            fontSize: 16,
            resize: "vertical",
            color: "var(--color-on-background, #222)",
            background: "#fff",
            outline: "none",
            boxShadow: "0 1px 4px #0001",
            transition: "border 0.2s",
          }}
          onFocus={(e) => (e.target.style.border = "2px solid #7c4dff")}
          onBlur={(e) => (e.target.style.border = "2px solid #bdbdbd")}
          disabled={formLoading}
        />
        {/* Chọn privacy */}
        <div
          style={{
            display: "flex",
            gap: 16,
            alignItems: "center",
            color: "var(--color-on-background, #222)",
            flexWrap: "wrap",
          }}
        >
          <span>Quyền riêng tư:</span>
          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: 4,
              background: "#e3f2fd",
              color: "#1565c0",
              borderRadius: 8,
              padding: "2px 10px",
              fontWeight: 500,
            }}
          >
            <input
              type="radio"
              name="privacy"
              value="public"
              checked={formPrivacy === "public"}
              onChange={() => setFormPrivacy("public")}
              disabled={formLoading}
              style={{ accentColor: "#1565c0" }}
            />
            Công khai
          </label>
          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: 4,
              background: "#e8f5e9",
              color: "#388e3c",
              borderRadius: 8,
              padding: "2px 10px",
              fontWeight: 500,
            }}
          >
            <input
              type="radio"
              name="privacy"
              value="community"
              checked={formPrivacy === "community"}
              onChange={() => setFormPrivacy("community")}
              disabled={formLoading}
              style={{ accentColor: "#388e3c" }}
            />
            Cộng đồng
          </label>
          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: 4,
              background: "#ffebee",
              color: "#b71c1c",
              borderRadius: 8,
              padding: "2px 10px",
              fontWeight: 500,
            }}
          >
            <input
              type="radio"
              name="privacy"
              value="private"
              checked={formPrivacy === "private"}
              onChange={() => setFormPrivacy("private")}
              disabled={formLoading}
              style={{ accentColor: "#b71c1c" }}
            />
            Riêng tư
          </label>
        </div>
        {formError && (
          <div style={{ color: "var(--color-error)", marginBottom: 8 }}>
            {formError}
          </div>
        )}
        <div style={{ display: "flex", gap: 12 }}>
          <button
            type="button"
            onClick={onClose}
            style={{
              background: "#eee",
              color: "var(--color-on-background, #222)",
              border: "none",
              borderRadius: 6,
              padding: "8px 20px",
              fontSize: 16,
              cursor: "pointer",
            }}
            disabled={formLoading}
          >
            Huỷ
          </button>
          <button
            type="submit"
            style={{
              background: "var(--color-primary,#7C4DFF)",
              color: "#fff",
              border: "none",
              borderRadius: 6,
              padding: "8px 20px",
              fontSize: 16,
              cursor: "pointer",
              fontWeight: 500,
            }}
            disabled={formLoading}
          >
            {formLoading
              ? mode === "edit"
                ? "Đang lưu..."
                : "Đang đăng..."
              : mode === "edit"
                ? "Lưu thay đổi"
                : "Đăng bài"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

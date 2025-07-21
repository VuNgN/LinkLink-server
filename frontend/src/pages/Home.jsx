import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PostItem from "../components/PostItem";
import PostDetail from "../components/PostDetail";
import Modal from "../components/Modal";
import PostFormModal from "../components/PostFormModal";
import Header from "../components/Header";
import NewPostNotification from "../components/NewPostNotification";
import DeleteConfirmModal from "../components/DeleteConfirmModal";
import usePosts from "../hooks/usePosts";
import useAuth from "../hooks/useAuth";
import useWebSocket from "../hooks/useWebSocket";

export default function Home() {
  const navigate = useNavigate();
  const { posts, loading, error, reloadPosts, deletePost } = usePosts(navigate);
  const { isAuthenticated, logout } = useAuth();

  const [showForm, setShowForm] = useState(false);
  const [hasNewPost, setHasNewPost] = useState(false);
  const [selectedPost, setSelectedPost] = useState(null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [showEdit, setShowEdit] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [postToEdit, setPostToEdit] = useState(null);
  const [postToDelete, setPostToDelete] = useState(null);

  // WebSocket hook
  useWebSocket(isAuthenticated, () => setHasNewPost(true));

  // Handle new post notification
  const handleNewPostNotification = async () => {
    setHasNewPost(false);
    await reloadPosts();
  };

  // Handle edit post
  const handleEdit = (post) => {
    setPostToEdit(post);
    setShowEdit(true);
    setSelectedPost(null);
  };

  // Handle delete post
  const handleDelete = (post) => {
    setPostToDelete(post);
    setShowDeleteConfirm(true);
    setSelectedPost(null);
  };

  // Confirm delete
  const confirmDelete = async () => {
    if (!postToDelete) return;

    const success = await deletePost(postToDelete.id);
    if (success) {
      setShowDeleteConfirm(false);
      setPostToDelete(null);
    }
  };

  const handlePostClick = (post, imageIndex = 0) => {
    setSelectedPost(post);
    setSelectedImageIndex(imageIndex);
  };

  // Handle login
  const handleLogin = () => {
    navigate("/login");
  };

  // Handle logout
  const handleLogout = async () => {
    await logout();
  };

  // Handle create post
  const handleCreatePost = () => {
    setShowForm(true);
  };

  // Handle navigate to trash
  const handleNavigateToTrash = () => {
    navigate("/trash");
  };

  if (loading) {
    return (
      <div style={{ textAlign: "center", marginTop: 40 }}>Đang tải...</div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          color: "var(--color-on-background, #222)",
          textAlign: "center",
          marginTop: 40,
        }}
      >
        {error}
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100%",
        boxSizing: "border-box",
        background: "var(--color-background, #fff)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: 0,
        margin: 0,
        overflowX: "hidden",
        color: "var(--color-on-background, #222)",
      }}
    >
      <Header
        isAuthenticated={isAuthenticated}
        onLogin={handleLogin}
        onLogout={handleLogout}
        onCreatePost={handleCreatePost}
        onNavigateToTrash={handleNavigateToTrash}
      />

      {/* Popup đăng bài viết - chỉ hiển thị khi đã đăng nhập */}
      {isAuthenticated && (
        <PostFormModal
          open={showForm}
          onClose={() => setShowForm(false)}
          onSuccess={reloadPosts}
        />
      )}

      {/* Nút thông báo có bài viết mới - chỉ hiển thị khi đã đăng nhập */}
      {isAuthenticated && hasNewPost && (
        <NewPostNotification onRefresh={handleNewPostNotification} />
      )}

      <div style={{ width: "100%" }}>
        {posts.length === 0 && <div>Chưa có bài viết nào.</div>}
        {posts.map((post) => (
          <PostItem
            key={post.id}
            post={post}
            onClick={handlePostClick}
          />
        ))}
        <Modal open={!!selectedPost} onClose={() => setSelectedPost(null)}>
          {selectedPost && (
            <PostDetail
              post={selectedPost}
              initialImageIndex={selectedImageIndex}
              onEdit={
                isAuthenticated ? () => handleEdit(selectedPost) : undefined
              }
              onDelete={
                isAuthenticated ? () => handleDelete(selectedPost) : undefined
              }
            />
          )}
        </Modal>
      </div>

      {/* Edit Modal - chỉ hiển thị khi đã đăng nhập */}
      {isAuthenticated && showEdit && postToEdit && (
        <PostFormModal
          open={showEdit}
          onClose={() => {
            setShowEdit(false);
            setPostToEdit(null);
          }}
          onSuccess={() => {
            setShowEdit(false);
            setPostToEdit(null);
            reloadPosts();
          }}
          post={postToEdit}
          mode="edit"
        />
      )}

      {/* Delete Confirm Modal - chỉ hiển thị khi đã đăng nhập */}
      {isAuthenticated && (
        <DeleteConfirmModal
          open={showDeleteConfirm}
          onClose={() => {
            setShowDeleteConfirm(false);
            setPostToDelete(null);
          }}
          onConfirm={confirmDelete}
        />
      )}
    </div>
  );
}

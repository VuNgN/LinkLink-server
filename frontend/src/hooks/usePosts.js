import { useState, useEffect, useCallback } from "react";
import { api } from "../utils/api";

const usePosts = (navigate) => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadPosts = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get("/api/v1/posters/", {}, navigate);
      if (!res.ok) {
        // If user is not authenticated (401/403), just return empty posts
        if (res.status === 401 || res.status === 403) {
          setPosts([]);
          setError("");
          return;
        }
        throw new Error("Lỗi tải danh sách bài viết");
      }
      const data = await res.json();
      setPosts(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  const reloadPosts = async () => {
    setLoading(true);
    try {
      const res = await api.get("/api/v1/posters/", {}, navigate);
      if (!res.ok) {
        // If user is not authenticated (401/403), just return empty posts
        if (res.status === 401 || res.status === 403) {
          setPosts([]);
          setError("");
          return;
        }
        throw new Error("Lỗi tải danh sách bài viết");
      }
      const data = await res.json();
      setPosts(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const deletePost = async (postId) => {
    setError("");
    try {
      const res = await api.delete(`/api/v1/posters/${postId}`);
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Lỗi xoá bài viết");
      }
      setPosts(posts.filter((p) => p.id !== postId));
      return true;
    } catch (e) {
      setError(e.message);
      return false;
    }
  };

  useEffect(() => {
    loadPosts();
  }, [navigate, loadPosts]);

  return {
    posts,
    loading,
    error,
    reloadPosts,
    deletePost,
    setError,
  };
};

export default usePosts;

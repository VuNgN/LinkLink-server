import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import PostDetailPage from "./pages/PostDetailPage";
import Trash from "./pages/Trash";
import "./styles/App.css";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/" element={<Home />} />
      <Route path="/post/:id" element={<PostDetailPage />} />
      <Route path="/trash" element={<Trash />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

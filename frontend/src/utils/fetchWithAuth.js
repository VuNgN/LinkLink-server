export default async function fetchWithAuth(url, options = {}, navigate) {
  let res = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${localStorage.getItem("access_token")}`,
    },
    credentials: "include",
  });
  if (res.status === 401 || res.status === 403) {
    // Thử refresh token qua cookie
      const refreshRes = await fetch("/api/v1/refresh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      credentials: "include",
      });
      if (refreshRes.ok) {
        const data = await refreshRes.json();
        localStorage.setItem("access_token", data.access_token);
      if (data.username) {
        localStorage.setItem("username", data.username);
      }
        // Thử lại request gốc
        res = await fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            Authorization: `Bearer ${data.access_token}`,
          },
        credentials: "include",
        });
      } else {
        localStorage.removeItem("access_token");
      localStorage.removeItem("username");
      navigate("/login");
      throw new Error("Phiên đăng nhập hết hạn!");
    }
  }
  return res;
}

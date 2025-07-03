export default async function fetchWithAuth(url, options = {}, navigate) {
  let res = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${localStorage.getItem("access_token")}`,
    },
  });
  if (res.status === 401 || res.status === 403) {
    // Thử refresh token
    const refresh = localStorage.getItem("refresh_token");
    if (refresh) {
      const refreshRes = await fetch("/api/v1/refresh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
      });
      if (refreshRes.ok) {
        const data = await refreshRes.json();
        localStorage.setItem("access_token", data.access_token);
        // Thử lại request gốc
        res = await fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            Authorization: `Bearer ${data.access_token}`,
          },
        });
      } else {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        navigate("/login");
        throw new Error("Phiên đăng nhập hết hạn!");
      }
    } else {
      navigate("/login");
      throw new Error("Chưa đăng nhập!");
    }
  }
  return res;
}

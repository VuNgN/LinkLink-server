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
<<<<<<< Updated upstream
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
=======
    // Token might be expired, try to refresh
    const refreshToken = localStorage.getItem('refreshToken');
    if (refreshToken) {
      try {
        const refreshResponse = await fetch('/api/v1/refresh', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh_token: refreshToken })
        });

        if (refreshResponse.ok) {
          const refreshData = await refreshResponse.json();
          localStorage.setItem('accessToken', refreshData.access_token);
          
          // Retry the original request with new token
          const newHeaders = { ...headers };
          if (refreshData.access_token) {
            newHeaders['Authorization'] = `Bearer ${refreshData.access_token}`;
          }
          
          return fetch(url, { ...options, headers: newHeaders });
        } else {
          // Refresh failed, redirect to login
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          window.location.href = '/login';
          throw new Error('Authentication failed');
        }
      } catch (error) {
        // Refresh failed, redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        throw error;
      }
    } else {
      // No refresh token, redirect to login
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      window.location.href = '/login';
      throw new Error('No refresh token available');
>>>>>>> Stashed changes
    }
  }
  
  return res;
}

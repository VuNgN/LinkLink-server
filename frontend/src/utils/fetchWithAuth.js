export default async function fetchWithAuth(url, options = {}) {
  let res = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${localStorage.getItem("access_token")}`,
    },
    credentials: "include",
  });

  if (res.status === 401 || res.status === 403) {
    // Token might be expired, try to refresh
    const refreshToken = localStorage.getItem("refresh_token");
    if (refreshToken) {
      try {
        const refreshResponse = await fetch("/api/v1/refresh", {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (refreshResponse.ok) {
          const refreshData = await refreshResponse.json();
          localStorage.setItem("access_token", refreshData.access_token);

          // Retry the original request with new token
          const newHeaders = { ...options.headers };
          if (refreshData.access_token) {
            newHeaders["Authorization"] = `Bearer ${refreshData.access_token}`;
          }

          return fetch(url, { ...options, headers: newHeaders });
        } else {
          // Refresh failed, redirect to login
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
          throw new Error("Authentication failed");
        }
      } catch (error) {
        // Refresh failed, redirect to login
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        throw error;
      }
    } else {
      // No refresh token, redirect to login
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.location.href = "/login";
      throw new Error("No refresh token available");
    }
  }

  return res;
}

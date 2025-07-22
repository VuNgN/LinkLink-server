export default async function fetchWithAuth(url, options = {}) {
  const accessToken = localStorage.getItem("access_token");

  // Only add Authorization header if token exists
  const headers = { ...options.headers };
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }

  let res = await fetch(url, {
    ...options,
    headers,
    credentials: "include",
  });

  console.log("Initial fetch response status:", res.status);

  // Only try to refresh token if we had a token in the first place
  if (res.status === 401 || res.status === 403) {
    if (accessToken) {
      // Token might be expired, try to refresh using HttpOnly cookie
      try {
        console.log("Attempting to refresh token using HttpOnly cookie");
        const refreshResponse = await fetch("/api/v1/auth/refresh", {
          method: "POST",
          credentials: "include",
          // No Authorization header needed
        });

        if (refreshResponse.ok) {
          const refreshData = await refreshResponse.json();
          localStorage.setItem("access_token", refreshData.access_token);

          // Retry the original request with new token
          const newHeaders = { ...options.headers };
          if (refreshData.access_token) {
            newHeaders["Authorization"] =
              `Bearer ${refreshData.access_token}`;
          }

          const retryRes = await fetch(url, { ...options, headers: newHeaders });
          return retryRes;
        } else {
          // Refresh failed, redirect to login
          console.log("Refresh failed, redirecting to login");
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
          throw new Error("Authentication failed");
        }
      } catch (error) {
        // Refresh failed, redirect to login
        console.log("Error during refresh:", error);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        throw error;
      }
    } else {
      // No token was sent, so this is expected for unauthenticated requests
      // Just return the response as is
      return res;
    }
  }

  return res;
}

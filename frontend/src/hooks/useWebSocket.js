import { useEffect } from "react";

const useWebSocket = (isAuthenticated, onNewPost) => {
  useEffect(() => {
    if (!isAuthenticated) return;

    let ws;
    let closed = false;

    function getUsernameFromToken() {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) return "";
        const payload = JSON.parse(atob(token.split(".")[1]));
        return payload.username || "";
      } catch {
        return "";
      }
    }

    const username = getUsernameFromToken();

    function connectWS() {
      ws = new window.WebSocket(
        `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/ws/posts/notify?username=${encodeURIComponent(username)}`,
      );

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.event === "new_post") {
            onNewPost();
          }
        } catch {
          // ignore
        }
      };

      ws.onclose = () => {
        if (!closed) setTimeout(connectWS, 2000); // reconnect
      };
    }

    connectWS();

    return () => {
      closed = true;
      if (ws) ws.close();
    };
  }, [isAuthenticated, onNewPost]);
};

export default useWebSocket;

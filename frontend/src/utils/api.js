import fetchWithAuth from "./fetchWithAuth";

export const api = {
  get: (url, options = {}, navigate) =>
    fetchWithAuth(url, { ...options, method: "GET" }, navigate),
  post: (url, body, navigate, options = {}) =>
    fetchWithAuth(url, { ...options, method: "POST", body }, navigate),
  put: (url, body, navigate, options = {}) =>
    fetchWithAuth(url, { ...options, method: "PUT", body }, navigate),
  delete: (url, navigate, options = {}) =>
    fetchWithAuth(url, { ...options, method: "DELETE" }, navigate),
};

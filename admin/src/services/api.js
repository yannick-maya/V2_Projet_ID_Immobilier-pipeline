import axios from "axios";

const getApiBaseUrl = () => {
  const envUrl = process.env.REACT_APP_API_URL || "http://localhost:8000";
  return envUrl
    .split(",")
    .map((url) => url.trim())
    .find((url) => url.length > 0) || "http://localhost:8000";
};

const api = axios.create({
  baseURL: getApiBaseUrl(),
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const adminAuth = {
  login: (payload) => api.post("/auth/login", payload),
  me: () => api.get("/auth/me"),
};

export default api;

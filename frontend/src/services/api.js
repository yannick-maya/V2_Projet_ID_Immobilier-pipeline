import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const authApi = {
  register: (payload) => api.post("/auth/register", payload),
  login: (payload) => api.post("/auth/login", payload),
  me: () => api.get("/auth/me"),
};

export const annoncesApi = {
  list: (params) => api.get("/annonces", { params }),
  get: (id) => api.get(`/annonces/${id}`),
  create: (payload) => api.post("/annonces", payload),
};

export const statsApi = {
  list: (params) => api.get("/statistiques", { params }),
};

export const indiceApi = {
  list: (params) => api.get("/indice", { params }),
  tendances: () => api.get("/indice/tendances"),
};

export const scoringApi = {
  predict: (payload) => api.post("/scoring", payload),
};

export const favorisApi = {
  list: () => api.get("/favoris"),
  add: (id) => api.post(`/favoris/${id}`),
  remove: (id) => api.delete(`/favoris/${id}`),
};

export default api;

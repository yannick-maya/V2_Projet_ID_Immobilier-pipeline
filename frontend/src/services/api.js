import axios from "axios";

const getApiBaseUrl = () => {
  const envUrl = process.env.REACT_APP_API_URL || "http://localhost:8000";
  return envUrl
    .split(",")
    .map((url) => url.trim())
    .find((url) => url.length > 0) || "http://localhost:8000";
};

const API_BASE_URL = getApiBaseUrl();

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
  options: () => api.get("/statistiques/options"),
  project: () => api.get("/statistiques/project"),
  overview: (params) => api.get("/statistiques/overview", { params }),
  timeline: (params) => api.get("/statistiques/timeline", { params }),
  compareSources: (params) => api.get("/statistiques/comparaison-sources", { params }),
  compareZones: (params) => api.get("/statistiques/comparaison-zones", { params }),
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

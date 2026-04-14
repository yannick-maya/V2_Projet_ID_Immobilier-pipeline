import axios from "axios";

// Cache simple en mémoire
const cache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

const getCachedData = (key) => {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }
  return null;
};

const setCachedData = (key, data) => {
  cache.set(key, { data, timestamp: Date.now() });
};

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
  timeout: 10000, // Timeout de 10 secondes
});

// Intercepteur pour ajouter le token d'authentification
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      console.warn('Requête timeout, retrying...');
      // On pourrait implémenter un retry ici
    }
    return Promise.reject(error);
  }
);

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
  list: (params) => {
    const cacheKey = `stats_list_${JSON.stringify(params)}`;
    const cached = getCachedData(cacheKey);
    if (cached) return Promise.resolve({ data: cached });

    return api.get("/statistiques", { params }).then(response => {
      setCachedData(cacheKey, response.data);
      return response;
    });
  },
  options: () => {
    const cacheKey = 'stats_options';
    const cached = getCachedData(cacheKey);
    if (cached) return Promise.resolve({ data: cached });

    return api.get("/statistiques/options").then(response => {
      setCachedData(cacheKey, response.data);
      return response;
    });
  },
  project: () => {
    const cacheKey = 'stats_project';
    const cached = getCachedData(cacheKey);
    if (cached) return Promise.resolve({ data: cached });

    return api.get("/statistiques/project").then(response => {
      setCachedData(cacheKey, response.data);
      return response;
    });
  },
  overview: (params) => {
    const cacheKey = `stats_overview_${JSON.stringify(params)}`;
    const cached = getCachedData(cacheKey);
    if (cached) return Promise.resolve({ data: cached });

    return api.get("/statistiques/overview", { params }).then(response => {
      setCachedData(cacheKey, response.data);
      return response;
    });
  },
  timeline: (params) => {
    const cacheKey = `stats_timeline_${JSON.stringify(params)}`;
    const cached = getCachedData(cacheKey);
    if (cached) return Promise.resolve({ data: cached });

    return api.get("/statistiques/timeline", { params }).then(response => {
      setCachedData(cacheKey, response.data);
      return response;
    });
  },
  compareSources: (params) => {
    const cacheKey = `stats_compare_sources_${JSON.stringify(params)}`;
    const cached = getCachedData(cacheKey);
    if (cached) return Promise.resolve({ data: cached });

    return api.get("/statistiques/comparaison-sources", { params }).then(response => {
      setCachedData(cacheKey, response.data);
      return response;
    });
  },
  compareZones: (params) => {
    const cacheKey = `stats_compare_zones_${JSON.stringify(params)}`;
    const cached = getCachedData(cacheKey);
    if (cached) return Promise.resolve({ data: cached });

    return api.get("/statistiques/comparaison-zones", { params }).then(response => {
      setCachedData(cacheKey, response.data);
      return response;
    });
  },
};

export const indiceApi = {
  list: (params) => {
    const cacheKey = `indice_list_${JSON.stringify(params)}`;
    const cached = getCachedData(cacheKey);
    if (cached) return Promise.resolve({ data: cached });

    return api.get("/indice", { params }).then(response => {
      setCachedData(cacheKey, response.data);
      return response;
    });
  },
  tendances: () => {
    const cacheKey = 'indice_tendances';
    const cached = getCachedData(cacheKey);
    if (cached) return Promise.resolve({ data: cached });

    return api.get("/indice/tendances").then(response => {
      setCachedData(cacheKey, response.data);
      return response;
    });
  },
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

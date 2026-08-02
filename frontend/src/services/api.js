import axios from "axios";

const DEFAULT_API_BASE_URL = "http://localhost:8000/api/v1";
const REQUEST_TIMEOUT_MS = 15000;

export class ApiError extends Error {
  constructor(message, options = {}) {
    super(message);
    this.name = "ApiError";
    this.status = options.status;
    this.details = options.details;
    this.url = options.url;
    this.method = options.method;
    this.isAuthError = options.status === 401 || options.status === 403;
  }
}

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL,
  timeout: REQUEST_TIMEOUT_MS,
  headers: {
    "Content-Type": "application/json"
  }
});

function getAuthToken() {
  const storedToken = localStorage.getItem("customeriq.accessToken");
  const demoToken = import.meta.env.VITE_DEMO_AUTH_TOKEN;

  if (storedToken) {
    return storedToken;
  }

  if (demoToken) {
    return demoToken;
  }

  return import.meta.env.DEV ? "dummy-token" : null;
}

apiClient.interceptors.request.use((config) => {
  const token = getAuthToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const detail = error.response?.data?.detail;
    const message =
      typeof detail === "string"
        ? detail
        : error.message || "CustomerIQ API request failed.";

    const apiError = new ApiError(message, {
      status,
      details: error.response?.data,
      url: error.config?.url,
      method: error.config?.method?.toUpperCase()
    });

    window.dispatchEvent(
      new CustomEvent("customeriq:api-error", {
        detail: {
          message: apiError.message,
          status: apiError.status,
          url: apiError.url
        }
      })
    );

    return Promise.reject(apiError);
  }
);

const unwrap = (request) => request.then((response) => response.data);

export const api = {
  health: () => unwrap(apiClient.get("/health")),

  customers: {
    stats: () => unwrap(apiClient.get("/customers/stats")),
    list: (params = {}) => unwrap(apiClient.get("/customers/", { params })),
    get: (customerId) => unwrap(apiClient.get(`/customers/${customerId}`)),
    auditLogs: (limit = 10) =>
      unwrap(apiClient.get("/customers/audit/logs", { params: { limit } }))
  },

  predict: {
    single: (payload) => unwrap(apiClient.post("/predict/", payload)),
    batch: (file) => {
      const formData = new FormData();
      formData.append("file", file);
      return unwrap(
        apiClient.post("/predict/batch", formData, {
          headers: { "Content-Type": "multipart/form-data" },
          timeout: 30000
        })
      );
    },
    churn: () => unwrap(apiClient.get("/predict/churn")),
    shap: () => unwrap(apiClient.get("/predict/shap")),
    status: () => unwrap(apiClient.get("/predict/status")),
    recommendations: (customerId) =>
      unwrap(apiClient.get(`/predict/recommendations/${customerId}`)),
    trainAsync: (useOptuna = false) =>
      unwrap(apiClient.post("/predict/train/async", null, { params: { use_optuna: useOptuna } }))
  },

  segments: {
    // Current FastAPI router exposes KMeans segments under /predict/segments.
    list: (params = { n_clusters: 4 }) =>
      unwrap(apiClient.get("/predict/segments", { params }))
  },

  intelligence: {
    query: (payload) => unwrap(apiClient.post("/intelligence/query", payload)),
    generateBrief: (payload) => unwrap(apiClient.post("/intelligence/brief", payload))
  }
};

export default api;

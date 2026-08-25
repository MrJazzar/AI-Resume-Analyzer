/**
 * api.js — thin fetch wrapper around the AI Resume Analyzer backend.
 *
 * Auth is a server-side session sent as an HttpOnly cookie, so every
 * request must include credentials. There is no token to attach manually.
 */

// Change this if the API is served from somewhere other than localhost:8000.
const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";

class ApiError extends Error {
  constructor(message, status, payload) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

/**
 * Extracts a human-readable message from the backend's
 * `{"detail": "..."}` error shape (or FastAPI validation errors).
 */
function extractErrorMessage(payload, fallback) {
  if (!payload) return fallback;
  if (typeof payload.detail === "string") return payload.detail;
  if (Array.isArray(payload.errors) && payload.errors.length) {
    const first = payload.errors[0];
    const field = Array.isArray(first.loc) ? first.loc.slice(-1)[0] : "";
    return field ? `${field}: ${first.msg}` : first.msg || fallback;
  }
  if (Array.isArray(payload.detail) && payload.detail.length) {
    return payload.detail[0].msg || fallback;
  }
  return fallback;
}

async function request(path, { method = "GET", body, isForm = false, params } = {}) {
  let url = `${API_BASE_URL}${path}`;

  if (params) {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")
    ).toString();
    if (qs) url += `?${qs}`;
  }

  const options = {
    method,
    credentials: "include", // send the session cookie
    headers: {},
  };

  if (body !== undefined) {
    if (isForm) {
      options.body = body; // FormData sets its own multipart headers
    } else {
      options.headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(body);
    }
  }

  let response;
  try {
    response = await fetch(url, options);
  } catch (networkErr) {
    throw new ApiError(
      "Can't reach the server. Check that the API is running and reachable.",
      0,
      null
    );
  }

  const isJson = (response.headers.get("content-type") || "").includes("application/json");
  const payload = isJson ? await response.json().catch(() => null) : null;

  if (!response.ok) {
    throw new ApiError(
      extractErrorMessage(payload, `Request failed (${response.status})`),
      response.status,
      payload
    );
  }

  return payload;
}

const api = {
  get: (path, params) => request(path, { method: "GET", params }),
  post: (path, body) => request(path, { method: "POST", body }),
  put: (path, body) => request(path, { method: "PUT", body }),
  del: (path) => request(path, { method: "DELETE" }),
  upload: (path, formData) => request(path, { method: "POST", body: formData, isForm: true }),
};

window.api = api;
window.ApiError = ApiError;
window.API_BASE_URL = API_BASE_URL;

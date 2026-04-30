/* OpenTrails — fetch helper */
const BASE = "/api";

async function request(method, path, { body, params, headers = {}, signal } = {}) {
  let url = path.startsWith("http") ? path : BASE + (path.startsWith("/") ? path : "/" + path);
  if (params) {
    const q = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined && v !== null && v !== "") q.append(k, v);
    }
    const qs = q.toString();
    if (qs) url += (url.includes("?") ? "&" : "?") + qs;
  }
  const opts = {
    method,
    headers: {
      "Accept": "application/json",
      ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      ...headers,
    },
    signal,
  };
  if (body !== undefined) opts.body = typeof body === "string" ? body : JSON.stringify(body);

  let res;
  try {
    res = await fetch(url, opts);
  } catch (err) {
    const e = new Error("Network error. Please check your connection.");
    e.cause = err;
    throw e;
  }

  let data = null;
  const ct = res.headers.get("content-type") || "";
  try {
    data = ct.includes("application/json") ? await res.json() : await res.text();
  } catch (_) { /* ignore */ }

  if (!res.ok) {
    const msg = (data && data.detail) || (data && data.message) || res.statusText || `Request failed (${res.status})`;
    const e = new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
    e.status = res.status;
    e.data = data;
    throw e;
  }
  return data;
}

export const api = {
  get: (path, opts) => request("GET", path, opts),
  post: (path, body, opts = {}) => request("POST", path, { ...opts, body }),
  put: (path, body, opts = {}) => request("PUT", path, { ...opts, body }),
  patch: (path, body, opts = {}) => request("PATCH", path, { ...opts, body }),
  del: (path, opts) => request("DELETE", path, opts),
};

// Toast on errors helper — pages can call this in catch blocks
export async function tryApi(fn, { onError } = {}) {
  try {
    return await fn();
  } catch (err) {
    console.error("[api]", err);
    if (typeof onError === "function") onError(err);
    if (window.toast) window.toast.error(err.message || "Something went wrong.");
    return null;
  }
}

window.api = api;
window.tryApi = tryApi;

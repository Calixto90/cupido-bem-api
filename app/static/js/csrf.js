function csrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.content : "";
}

async function fetchJSON(url, options = {}) {
  const opts = Object.assign({}, options);
  opts.headers = Object.assign({ "Content-Type": "application/json" }, options.headers || {});
  if (opts.method && opts.method.toUpperCase() !== "GET") {
    opts.headers["X-CSRFToken"] = csrfToken();
  }
  const resp = await fetch(url, opts);
  let data = null;
  try {
    data = await resp.json();
  } catch (e) {
    data = null;
  }
  return { ok: resp.ok, status: resp.status, data };
}

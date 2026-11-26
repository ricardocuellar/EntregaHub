export class ApiError extends Error {
  constructor(public status: number, message: string, public data: unknown = null) { super(message); }
}
let csrfToken: string | null = null;
let csrfRequest: Promise<void> | null = null;

async function ensureCsrf() {
  if (csrfToken) return;
  if (!csrfRequest) {
    csrfRequest = api<{ csrfToken: string }>('/api/auth/csrf/')
      .then(() => undefined)
      .finally(() => { csrfRequest = null; });
  }
  await csrfRequest;
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = new URL(path, window.location.origin);
  if (!path.startsWith('/api/') || url.origin !== window.location.origin || !url.pathname.startsWith('/api/')) {
    throw new Error('La API debe usar rutas internas /api/.');
  }
  const headers = new Headers(options.headers);
  if (!['GET', 'HEAD', 'OPTIONS'].includes((options.method ?? 'GET').toUpperCase())) {
    await ensureCsrf();
    headers.set('X-CSRFToken', csrfToken!);
  }
  const response = await fetch(url, {...options, headers, credentials: 'same-origin', redirect: 'error', cache: 'no-store'});
  const data = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(response.status, data?.detail ?? 'No se pudo completar la solicitud.', data);
  if (['/api/auth/csrf/', '/api/auth/login/', '/api/auth/logout/'].includes(url.pathname) && typeof data?.csrfToken === 'string') {
    csrfToken = data.csrfToken;
  }
  return data as T;
}

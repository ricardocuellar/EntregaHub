export class ApiError extends Error {
  constructor(public status: number, message: string, public data: unknown = null) { super(message); }
}
export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  if (!path.startsWith('/api/')) throw new Error('La API debe usar rutas internas /api/.');
  const response = await fetch(path, {...options, credentials: 'same-origin'});
  const data = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(response.status, data?.detail ?? 'No se pudo completar la solicitud.', data);
  return data as T;
}

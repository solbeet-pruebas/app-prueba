/**
 * Cliente mínimo de la API. Usa rutas relativas (/api/...) porque frontend y backend
 * se sirven en el mismo origen: el proxy de Vite en desarrollo y el ingress en producción.
 */

/** Item tal como lo devuelve el backend. */
export interface Item {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
}

/** Error HTTP con el código de estado, para que la UI distinga 4xx de 5xx. */
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    throw new ApiError(response.status, `Error ${response.status} en ${path}`);
  }
  return (await response.json()) as T;
}

/** Lista los items. Lanza ApiError si la respuesta no es 2xx. */
export function listItems(): Promise<Item[]> {
  return request<Item[]>("/api/items");
}

/** Crea un item y devuelve el creado. Lanza ApiError si la respuesta no es 2xx. */
export function createItem(name: string): Promise<Item> {
  return request<Item>("/api/items", { method: "POST", body: JSON.stringify({ name }) });
}

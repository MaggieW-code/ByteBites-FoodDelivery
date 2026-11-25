// One place for the backend URL and response handling (F15, F30).
export const API_BASE_URL = process.env.API_BASE_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly detail: unknown,
  ) {
    super(`Request failed with status ${status}`);
    this.name = "ApiError";
  }

  // 422 bodies list errors as { loc: [..., field], msg }; map them to field -> message
  get fieldErrors(): Record<string, string> {
    if (this.status !== 422 || !Array.isArray(this.detail)) return {};
    return Object.fromEntries(
      this.detail
        .filter((error) => Array.isArray(error?.loc) && typeof error?.msg === "string")
        .map((error) => [String(error.loc[error.loc.length - 1]), error.msg]),
    );
  }
}

export async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init.headers },
  });
  const body = response.status === 204 ? undefined : await response.json().catch(() => undefined);
  if (!response.ok) throw new ApiError(response.status, body?.detail);
  return body as T;
}

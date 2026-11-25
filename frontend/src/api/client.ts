// One place for the backend URL, the saved token, and response handling (F15, F30).
export const API_BASE_URL = process.env.API_BASE_URL ?? "http://127.0.0.1:8000";

const ACCESS_TOKEN_KEY = "bytebites.access_token";
export const SESSION_EXPIRED_EVENT = "bytebites:session-expired";

export const getAccessToken = (): string | null => localStorage.getItem(ACCESS_TOKEN_KEY);
export const saveAccessToken = (token: string): void => localStorage.setItem(ACCESS_TOKEN_KEY, token);
export const clearAccessToken = (): void => localStorage.removeItem(ACCESS_TOKEN_KEY);

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

interface RequestOptions extends RequestInit {
  // Send the saved token. A 401 then means it expired or was revoked: it is cleared and
  // SESSION_EXPIRED_EVENT fires so the app can send the user back to sign in.
  isAuthenticated?: boolean;
}

export async function request<T>(path: string, { isAuthenticated = false, ...init }: RequestOptions = {}): Promise<T> {
  const token = isAuthenticated ? getAccessToken() : null;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  });
  const body = response.status === 204 ? undefined : await response.json().catch(() => undefined);
  if (!response.ok) {
    if (isAuthenticated && response.status === 401) {
      clearAccessToken();
      window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
    }
    throw new ApiError(response.status, body?.detail);
  }
  return body as T;
}

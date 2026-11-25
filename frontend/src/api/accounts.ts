import type { Account, AccountCreationRequest, CustomerAccount, SignInRequest, TokenResponse } from "../types/account";
import { request } from "./client";

const ACCESS_TOKEN_KEY = "bytebites.access_token";

export const getAccessToken = (): string | null => localStorage.getItem(ACCESS_TOKEN_KEY);

export const clearAccessToken = (): void => localStorage.removeItem(ACCESS_TOKEN_KEY);

const bearer = (token: string) => ({ Authorization: `Bearer ${token}` });

export const registerCustomer = (account: AccountCreationRequest): Promise<CustomerAccount> =>
  request<CustomerAccount>("/customers", { method: "POST", body: JSON.stringify(account) });

export const signIn = async (credentials: SignInRequest): Promise<TokenResponse> => {
  const token = await request<TokenResponse>("/auth/sign-in", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
  localStorage.setItem(ACCESS_TOKEN_KEY, token.access_token);
  return token;
};

// Throws ApiError 401 for a missing, expired, or signed-out token, 403 for a deactivated account
export const getCurrentAccount = (token: string, signal?: AbortSignal): Promise<Account> =>
  request<Account>("/auth/me", { headers: bearer(token), signal });

// Always forgets the token locally, even if the backend can't be reached
export const signOut = async (): Promise<void> => {
  const token = getAccessToken();
  clearAccessToken();
  if (token) await request<void>("/auth/sign-out", { method: "POST", headers: bearer(token) }).catch(() => undefined);
};

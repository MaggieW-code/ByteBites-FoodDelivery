import type {
  Account,
  AccountCreationRequest,
  CreateDeliveryAddressRequest,
  CustomerAccount,
  DeliveryAddress,
  SignInRequest,
  TokenResponse,
  UpdateCustomerRequest,
  UpdateDeliveryAddressRequest,
} from "../types/account";
import { clearAccessToken, getAccessToken, request, saveAccessToken } from "./client";

const json = (method: string, body: unknown): RequestInit => ({ method, body: JSON.stringify(body) });

export const registerCustomer = (account: AccountCreationRequest): Promise<CustomerAccount> =>
  request<CustomerAccount>("/customers", json("POST", account));

export const signIn = async (credentials: SignInRequest): Promise<TokenResponse> => {
  const token = await request<TokenResponse>("/auth/sign-in", json("POST", credentials));
  saveAccessToken(token.access_token);
  return token;
};

// Throws ApiError 401 for a missing, expired, or signed-out token, 403 for a deactivated account
export const getCurrentAccount = (signal?: AbortSignal): Promise<Account> =>
  request<Account>("/auth/me", { isAuthenticated: true, signal });

// Always forgets the token locally, even if the backend can't be reached
export const signOut = async (): Promise<void> => {
  const token = getAccessToken();
  clearAccessToken();
  if (token) {
    await request<void>("/auth/sign-out", { method: "POST", headers: { Authorization: `Bearer ${token}` } }).catch(
      () => undefined,
    );
  }
};

// --- signed-in customer (/customers/me) ---

export const getMyProfile = (signal?: AbortSignal): Promise<CustomerAccount> =>
  request<CustomerAccount>("/customers/me", { isAuthenticated: true, signal });

export const updateMyProfile = (changes: UpdateCustomerRequest): Promise<CustomerAccount> =>
  request<CustomerAccount>("/customers/me", { ...json("PATCH", changes), isAuthenticated: true });

export const addMyAddress = (address: CreateDeliveryAddressRequest): Promise<DeliveryAddress> =>
  request<DeliveryAddress>("/customers/me/addresses", { ...json("POST", address), isAuthenticated: true });

export const updateMyAddress = (addressId: string, changes: UpdateDeliveryAddressRequest): Promise<DeliveryAddress> =>
  request<DeliveryAddress>(`/customers/me/addresses/${encodeURIComponent(addressId)}`, {
    ...json("PATCH", changes),
    isAuthenticated: true,
  });

export const removeMyAddress = (addressId: string): Promise<void> =>
  request<void>(`/customers/me/addresses/${encodeURIComponent(addressId)}`, {
    method: "DELETE",
    isAuthenticated: true,
  });

// Ends every session on the backend, so the saved token is useless afterwards
export const deactivateMyAccount = async (): Promise<void> => {
  await request<void>("/customers/me/deactivate", { method: "POST", isAuthenticated: true });
  clearAccessToken();
};

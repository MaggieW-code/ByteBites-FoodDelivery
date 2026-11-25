// Mirrors backend/app/models/accounts/account_model.py and auth_model.py

export interface DeliveryAddress {
  id: string;
  label: string;
  address: string;
}

export interface CustomerAccount {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  is_active: boolean;
  role: "customer";
  delivery_addresses: DeliveryAddress[];
}

export interface RestaurantAccount extends Omit<CustomerAccount, "role" | "delivery_addresses"> {
  role: "restaurant_owner";
  owned_restaurant_ids: string[];
}

export interface AdminAccount extends Omit<CustomerAccount, "role" | "delivery_addresses"> {
  role: "admin";
}

// GET /auth/me returns any role; `role` tells them apart
export type Account = CustomerAccount | RestaurantAccount | AdminAccount;

export interface AccountCreationRequest {
  full_name: string;
  email: string;
  phone: string;
  password: string;
}

export interface SignInRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
  expires_at: string;
}

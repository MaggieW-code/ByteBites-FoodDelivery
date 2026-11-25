# models

## Purpose

Pydantic models that define the shape of every piece of data in the backend: what clients
may send, what is stored, and what the API returns. A model is the single check that data
is valid.

## Contents

| File | Models | Role |
|---|---|---|
| `restaurant_model.py` | `RestaurantId` | The restaurant ID rule (exactly 8 characters), reused by menu models and route path parameters |
| | `Restaurant` | Stored record and API response |
| | `CreateRestaurantRequest`, `UpdateRestaurantRequest` | Request bodies for `POST` / `PATCH` |
| `menu_model.py` | `MenuItemId`, `Price` | The menu item ID rule (exactly 8 characters) and the price rule, reused by routes |
| | `Menu`, `MenuListItem` | A restaurant's menu as stored in `menus.json` and returned by `GET .../menu` |
| | `CreateMenuItem`, `UpdateMenuItem` | Request bodies for `POST` / `PATCH .../menu` |
| | `MenuItem` | A saved menu item (adds `id` and `restaurant_id`); response for `POST` / `PATCH` |
| `accounts/account_model.py` | `EightCharId`, `NonEmptyText`, `Email` (`EmailStr` from `email-validator`, trimmed and lowercased; reserved domains like `.test` are rejected; for registration and changes), `PhoneNumber` (`PhoneNumberValidator` from `pydantic-extra-types`, backed by libphonenumber: Canadian numbers only, any common format in, stored as E.164, e.g. `(250) 222-1234` → `+12502221234`; extensions are dropped), `Role` | Shared type aliases, also imported by `accounts/auth_model.py` |
| | `AccountCreationRequest` | Request body for registering. Password is `SecretStr` (8–128 characters) so it never prints |
| | `PartialUpdateRequest` | Base for PATCH bodies: at least one field, no `null`s |
| | `DeliveryAddressId`, `DeliveryAddressFields` → `DeliveryAddress`, `CreateDeliveryAddressRequest`; `UpdateDeliveryAddressRequest` | A saved address has an 8-character `id`, unique within its customer. Create needs `label` and `address`; update sends either |
| | `UpdateCustomerRequest` | `PATCH /customers/me` body: `full_name`, `email`, `phone`, all optional. Undeclared fields (`role`, `is_active`, `password`, `delivery_addresses`) are ignored |
| | `AccountBase` → `CustomerAccount`, `RestaurantAccount`, `AdminAccount`; `Account` | API responses. `Account` picks the class from `role` |
| | `StoredCredentials` → `Stored<Role>Account`; `StoredAccount` | Stored records: the public account plus `password_hash` |
| `accounts/auth_model.py` | `AuthenticatedAccount` | The signed-in caller (`id`, `role`, `is_active`), built by authentication and read by protected routes |
| | `Session` | A stored sign-in: `token_hash` (never the raw token), `account_id`, `created_at`, `expires_at` |
| | `LoginEmail` | Sign-in email: trimmed, lowercased, 1–254 characters, no format check, so stored addresses always look up (registration uses `Email`) |
| | `SignInRequest` | Request body for signing in. `email` is a `LoginEmail`, password is `SecretStr` |
| | `TokenResponse` | Sign-in response: `access_token`, `token_type` (`bearer`), `expires_at` |

All menu prices are `Decimal` (`Price` in `menu_model.py`): a number or decimal string,
0 or more, at most 2 decimal places, at most 999999.99.

## How it connects

Models are the shared vocabulary of the backend, so every layer uses them, but they depend on
no layer:

```
routes ──► services ──► repositories ──► data/
   │           │             │
   └───────────┴──────┬──────┘
                      ▼
                   models/   (imports only pydantic and the standard library)
```

- **Routes** use request models as body types and stored models as `response_model`.
  FastAPI returns 422 for invalid input before any service code runs, and builds `/docs` from
  them.
- **Services** receive request models, apply business rules, and return stored models.
- **Repositories** validate file records into stored models on load and dump them on save.
- **Frontend** `frontend/src/types/` mirrors every model here by hand (stored, request, and
  response), one TypeScript type per model with the same name and fields. A model change and
  its type change go in the same PR.

## Conventions

- Models never import from `routes/`, `services/`, or `repositories/`.
- One file per feature holds all of that feature's models (`restaurant_model.py` is the
  reference).
- Naming: the stored model is the plain noun (`Restaurant`); request bodies are
  `Create<Noun>Request` and `Update<Noun>Request`.
- Every field uses `Field(strict=True, ...)` with explicit limits. IDs are exactly 8
  characters. Update models make every field optional (`None` means "don't change").
- Money is `Decimal`, never `float`.
- Proposed (after #122): frontend types will be generated from these models instead
  of copied by hand. FastAPI's `/openapi.json` → `openapi-typescript` → `frontend/src/types/api.ts`,
  called through `openapi-fetch` in `frontend/src/api/`. CI regenerates and fails on any diff,
  so a model change without regenerated types can't merge. Every route needs a
  `response_model` for its type to be generated.
- Not yet true: the menu request models skip the `Request` suffix, `Menu` /
  `MenuListItem` have no field constraints, and `price` is not `strict` (so a decimal
  string like `"14.99"` is accepted).

// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { deactivateMyAccount, getCurrentAccount, registerCustomer, signIn, signOut, updateMyProfile } from "../accounts";
import { API_BASE_URL, ApiError, getAccessToken, SESSION_EXPIRED_EVENT } from "../client";

const respond = (status: number, body?: unknown) =>
  vi.fn().mockResolvedValue(new Response(body === undefined ? null : JSON.stringify(body), { status }));

describe("account API", () => {
  beforeEach(() => localStorage.clear());
  afterEach(() => vi.unstubAllGlobals());

  it("sign-in posts the credentials and keeps the token", async () => {
    const fetchMock = respond(200, { access_token: "abc", token_type: "bearer", expires_at: "2026-11-25T00:00:00Z" });
    vi.stubGlobal("fetch", fetchMock);

    await signIn({ email: "cara@example.com", password: "secret-pass" });

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe(`${API_BASE_URL}/auth/sign-in`);
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body)).toEqual({ email: "cara@example.com", password: "secret-pass" });
    expect(getAccessToken()).toBe("abc");
  });

  it("a failed sign-in throws ApiError with the status and keeps no token", async () => {
    vi.stubGlobal("fetch", respond(401, { detail: "Invalid email or password" }));

    const error = await signIn({ email: "cara@example.com", password: "wrong" }).catch((caught) => caught);

    expect(error).toBeInstanceOf(ApiError);
    expect(error.status).toBe(401);
    expect(getAccessToken()).toBeNull();
  });

  it("register posts to /customers", async () => {
    const fetchMock = respond(201, { id: "cust_002" });
    vi.stubGlobal("fetch", fetchMock);

    await registerCustomer({ full_name: "Nina", email: "nina@example.com", phone: "2505550123", password: "nina-pass-1" });

    expect(fetchMock.mock.calls[0][0]).toBe(`${API_BASE_URL}/customers`);
  });

  it("a 422 maps each invalid field to its message", async () => {
    vi.stubGlobal(
      "fetch",
      respond(422, { detail: [{ loc: ["body", "phone"], msg: "value is not a valid phone number" }] }),
    );

    const error = await registerCustomer({ full_name: "N", email: "n@example.com", phone: "123", password: "x" }).catch(
      (caught) => caught,
    );

    expect(error.fieldErrors).toEqual({ phone: "value is not a valid phone number" });
  });

  it("current account sends the token as a bearer header", async () => {
    localStorage.setItem("bytebites.access_token", "abc");
    const fetchMock = respond(200, { id: "cust_001", role: "customer" });
    vi.stubGlobal("fetch", fetchMock);

    await getCurrentAccount();

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe(`${API_BASE_URL}/auth/me`);
    expect(init.headers.Authorization).toBe("Bearer abc");
  });

  it("sign-out revokes the token on the backend and forgets it", async () => {
    localStorage.setItem("bytebites.access_token", "abc");
    const fetchMock = respond(204);
    vi.stubGlobal("fetch", fetchMock);

    await signOut();

    expect(fetchMock.mock.calls[0][0]).toBe(`${API_BASE_URL}/auth/sign-out`);
    expect(fetchMock.mock.calls[0][1].headers.Authorization).toBe("Bearer abc");
    expect(getAccessToken()).toBeNull();
  });

  it("sign-out still forgets the token when the backend is down", async () => {
    localStorage.setItem("bytebites.access_token", "abc");
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    await signOut();

    expect(getAccessToken()).toBeNull();
  });

  it("a 401 on a signed-in request forgets the token and announces the session expired", async () => {
    localStorage.setItem("bytebites.access_token", "expired");
    vi.stubGlobal("fetch", respond(401, { detail: "Token expired" }));
    const onExpired = vi.fn();
    window.addEventListener(SESSION_EXPIRED_EVENT, onExpired);

    const error = await updateMyProfile({ full_name: "X" }).catch((caught) => caught);

    window.removeEventListener(SESSION_EXPIRED_EVENT, onExpired);
    expect(error.status).toBe(401);
    expect(getAccessToken()).toBeNull();
    expect(onExpired).toHaveBeenCalledOnce();
  });

  it("a 401 on sign-in is a wrong password, not an expired session", async () => {
    vi.stubGlobal("fetch", respond(401, { detail: "Invalid email or password" }));
    const onExpired = vi.fn();
    window.addEventListener(SESSION_EXPIRED_EVENT, onExpired);

    await signIn({ email: "cara@example.com", password: "wrong" }).catch(() => undefined);

    window.removeEventListener(SESSION_EXPIRED_EVENT, onExpired);
    expect(onExpired).not.toHaveBeenCalled();
  });

  it("profile changes send only the changed fields with the token", async () => {
    localStorage.setItem("bytebites.access_token", "abc");
    const fetchMock = respond(200, { id: "cust_001" });
    vi.stubGlobal("fetch", fetchMock);

    await updateMyProfile({ phone: "250-555-0199" });

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe(`${API_BASE_URL}/customers/me`);
    expect(init.method).toBe("PATCH");
    expect(init.headers.Authorization).toBe("Bearer abc");
    expect(JSON.parse(init.body)).toEqual({ phone: "250-555-0199" });
  });

  it("deactivating forgets the token", async () => {
    localStorage.setItem("bytebites.access_token", "abc");
    vi.stubGlobal("fetch", respond(204));

    await deactivateMyAccount();

    expect(getAccessToken()).toBeNull();
  });
});

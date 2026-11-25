// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { RequireSignIn } from "../RequireSignIn";
import { getCurrentAccount } from "../../api/accounts";
import { ApiError } from "../../api/client";
import type { Account } from "../../types/account";

vi.mock("../../api/accounts", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../../api/accounts")>()),
  getCurrentAccount: vi.fn(),
}));
const mockGetCurrentAccount = vi.mocked(getCurrentAccount);

const cara: Account = {
  id: "cust_001", full_name: "Cara", email: "cara@example.com", phone: "+12505550100",
  is_active: true, role: "customer", delivery_addresses: [],
};

function SignInPage() {
  const from = (useLocation().state as { from?: string } | null)?.from;
  return <p>Sign-in page, from {from}</p>;
}

const renderAt = (path: string) =>
  render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/account" element={<SignInPage />} />
        <Route element={<RequireSignIn />}>
          <Route path="/restaurants" element={<p>Discover page</p>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );

describe("RequireSignIn", () => {
  beforeEach(() => {
    localStorage.clear();
    mockGetCurrentAccount.mockReset();
  });
  afterEach(cleanup);

  it("without a token, sends you to sign in and remembers where you were going", () => {
    renderAt("/restaurants");

    expect(screen.getByText("Sign-in page, from /restaurants")).toBeTruthy();
    expect(mockGetCurrentAccount).not.toHaveBeenCalled();
  });

  it("with a valid token, shows the page", async () => {
    localStorage.setItem("bytebites.access_token", "good");
    mockGetCurrentAccount.mockResolvedValue(cara);
    renderAt("/restaurants");

    expect(screen.getByRole("status").textContent).toBe("Checking your sign-in…");
    expect(await screen.findByText("Discover page")).toBeTruthy();
    expect(mockGetCurrentAccount).toHaveBeenCalledOnce();
  });

  it.each([401, 403])("a token the backend rejects (%i) is forgotten and you go to sign in", async (status) => {
    localStorage.setItem("bytebites.access_token", "stale");
    mockGetCurrentAccount.mockRejectedValue(new ApiError(status, "rejected"));
    renderAt("/restaurants");

    expect(await screen.findByText(/Sign-in page/)).toBeTruthy();
    expect(localStorage.getItem("bytebites.access_token")).toBeNull();
  });

  it("when the backend can't be reached, shows an error and keeps the token", async () => {
    localStorage.setItem("bytebites.access_token", "good");
    mockGetCurrentAccount.mockRejectedValue(new TypeError("Failed to fetch"));
    renderAt("/restaurants");

    expect((await screen.findByRole("alert")).textContent).toMatch("Can't reach ByteBites");
    expect(localStorage.getItem("bytebites.access_token")).toBe("good");
  });
});

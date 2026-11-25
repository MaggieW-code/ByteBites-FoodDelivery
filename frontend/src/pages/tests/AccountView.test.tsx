// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { Account } from "../AccountView";
import { registerCustomer, signIn } from "../../api/accounts";
import { ApiError } from "../../api/client";

vi.mock("../../api/accounts", () => ({ signIn: vi.fn(), registerCustomer: vi.fn() }));
const mockSignIn = vi.mocked(signIn);
const mockRegister = vi.mocked(registerCustomer);

const renderAccount = (from?: string) =>
  render(
    <MemoryRouter initialEntries={[{ pathname: "/account", state: from ? { from } : null }]}>
      <Routes>
        <Route path="/account" element={<Account />} />
        <Route path="/restaurants" element={<p>Discover page</p>} />
        <Route path="/manage/restaurants" element={<p>Manage page</p>} />
      </Routes>
    </MemoryRouter>,
  );

const type = (label: string, value: string) => fireEvent.change(screen.getByLabelText(label), { target: { value } });

describe("Account page", () => {
  beforeEach(() => {
    mockSignIn.mockReset();
    mockRegister.mockReset();
  });
  afterEach(cleanup);

  it("signing in goes to Discover", async () => {
    mockSignIn.mockResolvedValue({ access_token: "abc", token_type: "bearer", expires_at: "" });
    renderAccount();

    type("Email", "cara@example.com");
    type("Password", "secret-pass");
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByText("Discover page")).toBeTruthy();
    expect(mockSignIn).toHaveBeenCalledWith({ email: "cara@example.com", password: "secret-pass" });
  });

  it("a wrong password shows a message and stays on the page", async () => {
    mockSignIn.mockRejectedValue(new ApiError(401, "Invalid email or password"));
    renderAccount();

    type("Email", "cara@example.com");
    type("Password", "wrong");
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect((await screen.findByRole("alert")).textContent).toBe("Email or password is incorrect.");
    expect(screen.queryByText("Discover page")).toBeNull();
  });

  it("registering creates the account, signs in, and goes to Discover", async () => {
    mockRegister.mockResolvedValue({} as never);
    mockSignIn.mockResolvedValue({ access_token: "abc", token_type: "bearer", expires_at: "" });
    renderAccount();

    fireEvent.click(screen.getByRole("button", { name: /Create an account/ }));
    type("Full name", "Nina New");
    type("Email", "nina@example.com");
    type("Phone", "250-555-0123");
    type("Password", "nina-pass-1");
    fireEvent.click(screen.getByRole("button", { name: "Create account" }));

    expect(await screen.findByText("Discover page")).toBeTruthy();
    expect(mockRegister).toHaveBeenCalledWith({
      full_name: "Nina New",
      email: "nina@example.com",
      phone: "250-555-0123",
      password: "nina-pass-1",
    });
  });

  it("shows the backend's message next to an invalid field", async () => {
    mockRegister.mockRejectedValue(new ApiError(422, [{ loc: ["body", "phone"], msg: "value is not a valid phone number" }]));
    renderAccount();

    fireEvent.click(screen.getByRole("button", { name: /Create an account/ }));
    type("Phone", "123");
    fireEvent.click(screen.getByRole("button", { name: "Create account" }));

    expect(await screen.findByText("value is not a valid phone number")).toBeTruthy();
    expect(screen.getByLabelText("Phone").getAttribute("aria-invalid")).toBe("true");
    expect(mockSignIn).not.toHaveBeenCalled();
  });

  it("a used email says to sign in instead", async () => {
    mockRegister.mockRejectedValue(new ApiError(409, "Email already registered"));
    renderAccount();

    fireEvent.click(screen.getByRole("button", { name: /Create an account/ }));
    fireEvent.click(screen.getByRole("button", { name: "Create account" }));

    expect((await screen.findByRole("alert")).textContent).toBe("That email is already registered. Sign in instead.");
  });

  it("after signing in, goes back to the page the guard sent you from", async () => {
    mockSignIn.mockResolvedValue({ access_token: "abc", token_type: "bearer", expires_at: "" });
    renderAccount("/manage/restaurants");

    type("Email", "omar@example.com");
    type("Password", "owner-pass-1");
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByText("Manage page")).toBeTruthy();
  });
});

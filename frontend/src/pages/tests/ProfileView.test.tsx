// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { Profile } from "../ProfileView";
import * as accounts from "../../api/accounts";
import { ApiError } from "../../api/client";
import type { CustomerAccount } from "../../types/account";

vi.mock("../../api/accounts", () => ({
  getMyProfile: vi.fn(),
  updateMyProfile: vi.fn(),
  addMyAddress: vi.fn(),
  updateMyAddress: vi.fn(),
  removeMyAddress: vi.fn(),
  deactivateMyAccount: vi.fn(),
}));
const api = vi.mocked(accounts);

const HOME = { id: "addr_001", label: "Home", address: "1 Main St" };
const cara: CustomerAccount = {
  id: "cust_001", full_name: "Cara", email: "cara@example.com", phone: "+12505550100",
  is_active: true, role: "customer", delivery_addresses: [HOME],
};

const renderProfile = () =>
  render(
    <MemoryRouter initialEntries={["/profile"]}>
      <Routes>
        <Route path="/profile" element={<Profile />} />
        <Route path="/account" element={<p>Sign-in page</p>} />
      </Routes>
    </MemoryRouter>,
  );

const type = (label: string, value: string) => fireEvent.change(screen.getByLabelText(label), { target: { value } });

describe("Profile page", () => {
  beforeEach(() => {
    Object.values(api).forEach((mock) => mock.mockReset());
    api.getMyProfile.mockResolvedValue(cara);
  });
  afterEach(cleanup);

  it("shows the customer's details and addresses", async () => {
    renderProfile();

    expect(screen.getByRole("status").textContent).toBe("Loading your profile…");
    expect(((await screen.findByLabelText("Email")) as HTMLInputElement).value).toBe("cara@example.com");
    expect(screen.getByText("Home")).toBeTruthy();
  });

  it("saves only the fields that changed", async () => {
    api.updateMyProfile.mockResolvedValue({ ...cara, phone: "+12505550199" });
    renderProfile();
    await screen.findByLabelText("Phone");

    expect((screen.getByRole("button", { name: "Save details" }) as HTMLButtonElement).disabled).toBe(true);
    type("Phone", "250-555-0199");
    fireEvent.click(screen.getByRole("button", { name: "Save details" }));

    expect((await screen.findByRole("status")).textContent).toBe("Saved.");
    expect(api.updateMyProfile).toHaveBeenCalledWith({ phone: "250-555-0199" });
    expect((screen.getByLabelText("Phone") as HTMLInputElement).value).toBe("+12505550199");
  });

  it("an email used by someone else shows a message", async () => {
    api.updateMyProfile.mockRejectedValue(new ApiError(409, "Email already registered"));
    renderProfile();
    await screen.findByLabelText("Email");

    type("Email", "omar@example.com");
    fireEvent.click(screen.getByRole("button", { name: "Save details" }));

    expect((await screen.findByRole("alert")).textContent).toBe("That email is already used by another account.");
  });

  it("adds, edits, and removes addresses", async () => {
    const WORK = { id: "addr_002", label: "Work", address: "2 Office Rd" };
    api.addMyAddress.mockResolvedValue(WORK);
    api.updateMyAddress.mockResolvedValue({ ...HOME, address: "9 New Ave" });
    api.removeMyAddress.mockResolvedValue(undefined);
    renderProfile();
    await screen.findByText("Home");

    type("New address label", "Work");
    type("New address", "2 Office Rd");
    fireEvent.click(screen.getByRole("button", { name: "Add address" }));
    expect(await screen.findByText("Work")).toBeTruthy();
    expect(api.addMyAddress).toHaveBeenCalledWith({ label: "Work", address: "2 Office Rd" });

    fireEvent.click(screen.getByRole("button", { name: "Edit Home" }));
    const editForm = screen.getByRole("form", { name: "Edit Home" });
    fireEvent.change(within(editForm).getByLabelText("Address"), { target: { value: "9 New Ave" } });
    fireEvent.click(within(editForm).getByRole("button", { name: "Save address" }));
    expect(await screen.findByText(/9 New Ave/)).toBeTruthy();
    expect(api.updateMyAddress).toHaveBeenCalledWith("addr_001", { label: "Home", address: "9 New Ave" });

    fireEvent.click(screen.getByRole("button", { name: "Remove Work" }));
    await vi.waitFor(() => expect(screen.queryByText("Work")).toBeNull());
    expect(api.removeMyAddress).toHaveBeenCalledWith("addr_002");
  });

  it("deactivating after confirming goes to sign-in", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    api.deactivateMyAccount.mockResolvedValue(undefined);
    renderProfile();

    fireEvent.click(await screen.findByRole("button", { name: "Deactivate my account" }));

    expect(await screen.findByText("Sign-in page")).toBeTruthy();
  });

  it("cancelling the confirm does nothing", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(false);
    renderProfile();

    fireEvent.click(await screen.findByRole("button", { name: "Deactivate my account" }));

    expect(api.deactivateMyAccount).not.toHaveBeenCalled();
  });

  it("an owner sees that profiles are for customers", async () => {
    api.getMyProfile.mockRejectedValue(new ApiError(403, "Customers only"));
    renderProfile();

    expect((await screen.findByRole("alert")).textContent).toBe("Profiles are for customer accounts.");
  });
});

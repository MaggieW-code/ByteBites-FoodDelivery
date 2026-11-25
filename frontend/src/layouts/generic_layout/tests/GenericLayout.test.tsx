// @vitest-environment jsdom
import { describe, it, expect, afterEach } from "vitest";
import { render, screen, cleanup, act } from "@testing-library/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { GenericLayout } from "../GenericLayout";
import { SESSION_EXPIRED_EVENT } from "../../../api/client";

function SignInPage() {
  const from = (useLocation().state as { from?: string } | null)?.from;
  return <p>Sign-in page, from {from}</p>;
}

describe("GenericLayout", () => {
  afterEach(() => {
    cleanup();
    localStorage.clear();
  });

  it("an expired session sends you to sign in, remembering the page", () => {
    localStorage.setItem("bytebites.access_token", "abc");
    render(
      <MemoryRouter initialEntries={["/profile"]}>
        <GenericLayout>
          <Routes>
            <Route path="/profile" element={<p>Profile page</p>} />
            <Route path="/account" element={<SignInPage />} />
          </Routes>
        </GenericLayout>
      </MemoryRouter>,
    );
    expect(screen.getByRole("link", { name: "Profile" })).toBeTruthy();

    act(() => {
      localStorage.clear();
      window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
    });

    expect(screen.getByText("Sign-in page, from /profile")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Sign out" })).toBeNull();
  });
});

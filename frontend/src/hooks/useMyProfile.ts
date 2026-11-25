import { useEffect, useState } from "react";
import { getMyProfile } from "../api/accounts";
import { ApiError } from "../api/client";
import type { CustomerAccount } from "../types/account";

export type MyProfileState =
  | { status: "loading" }
  | { status: "loaded"; profile: CustomerAccount }
  | { status: "not-a-customer" }
  | { status: "error" };

// Loads the signed-in customer's profile. `setProfile` lets the page show saved changes without reloading.
export function useMyProfile() {
  const [state, setState] = useState<MyProfileState>({ status: "loading" });

  useEffect(() => {
    const controller = new AbortController();
    getMyProfile(controller.signal)
      .then((profile) => setState({ status: "loaded", profile }))
      .catch((error) => {
        if (controller.signal.aborted) return;
        // 401 is handled by api/client.ts (back to sign-in); 403 means an owner or admin is signed in
        setState(error instanceof ApiError && error.status === 403 ? { status: "not-a-customer" } : { status: "error" });
      });
    return () => controller.abort();
  }, []);

  const setProfile = (profile: CustomerAccount) => setState({ status: "loaded", profile });

  return { state, setProfile };
}

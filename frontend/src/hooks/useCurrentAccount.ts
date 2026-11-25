import { useEffect, useState } from "react";
import { getCurrentAccount } from "../api/accounts";
import { ApiError, clearAccessToken, getAccessToken } from "../api/client";
import type { Account } from "../types/account";

export type CurrentAccountState =
  | { status: "loading" }
  | { status: "signed-in"; account: Account }
  | { status: "signed-out" }
  | { status: "error" };

// Asks the backend who the saved token belongs to. A rejected token is forgotten.
export function useCurrentAccount(): CurrentAccountState {
  const [token] = useState(getAccessToken);
  const [state, setState] = useState<CurrentAccountState>(token ? { status: "loading" } : { status: "signed-out" });

  useEffect(() => {
    if (!token) return;
    const controller = new AbortController();
    getCurrentAccount(controller.signal)
      .then((account) => setState({ status: "signed-in", account }))
      .catch((error) => {
        if (controller.signal.aborted) return;
        if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
          clearAccessToken();
          setState({ status: "signed-out" });
        } else {
          setState({ status: "error" });
        }
      });
    return () => controller.abort();
  }, [token]);

  return state;
}

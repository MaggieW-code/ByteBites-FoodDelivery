import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useCurrentAccount } from "../hooks/useCurrentAccount";

// Guard route: child routes render only for a signed-in account; everyone else goes to /account
export function RequireSignIn() {
  const location = useLocation();
  const current = useCurrentAccount();

  if (current.status === "loading") return <p role="status">Checking your sign-in…</p>;
  if (current.status === "error") return <p role="alert">Can't reach ByteBites right now. Please refresh to try again.</p>;
  if (current.status === "signed-out") return <Navigate to="/account" replace state={{ from: location.pathname }} />;
  return <Outlet />;
}

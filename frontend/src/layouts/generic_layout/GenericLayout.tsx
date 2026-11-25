import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { useEffect, type ReactNode } from "react";
import { signOut } from "../../api/accounts";
import { getAccessToken, SESSION_EXPIRED_EVENT } from "../../api/client";

type GenericLayoutProps = {
    children: ReactNode;
};

export function GenericLayout({children}: GenericLayoutProps) {
    const location = useLocation(); // re-render on navigation so the sign-out button follows the saved token
    const navigate = useNavigate();
    const isSignedIn = getAccessToken() !== null;

    // api/client.ts fires this when a signed-in request gets 401 (token expired or revoked)
    useEffect(() => {
        const backToSignIn = () => navigate("/account", { replace: true, state: { from: location.pathname } });
        window.addEventListener(SESSION_EXPIRED_EVENT, backToSignIn);
        return () => window.removeEventListener(SESSION_EXPIRED_EVENT, backToSignIn);
    }, [navigate, location.pathname]);

    const handleSignOut = async () => {
        await signOut();
        navigate("/account", { replace: true });
    };

    return(
        <div className="generic-layout_container">
            <header className="generic-layout_header">
                <h1><NavLink to="/">ByteBites</NavLink></h1>
                <nav aria-label="Main navigation">
                    <NavLink to="/" end>Home</NavLink>
                    {isSignedIn && <NavLink to="/profile">Profile</NavLink>}
                    {isSignedIn && <button type="button" onClick={handleSignOut}>Sign out</button>}
                </nav>
            </header>
            {children}
        </div>
    ); 
}
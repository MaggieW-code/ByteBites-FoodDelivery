import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { getAccessToken, signOut } from "../../api/accounts";
import { type ReactNode } from "react";

type GenericLayoutProps = {
    children: ReactNode;
};

export function GenericLayout({children}: GenericLayoutProps) {
    useLocation(); // re-render on navigation so the sign-out button follows the saved token
    const navigate = useNavigate();
    const isSignedIn = getAccessToken() !== null;

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
                    {isSignedIn && <button type="button" onClick={handleSignOut}>Sign out</button>}
                </nav>
            </header>
            {children}
        </div>
    ); 
}
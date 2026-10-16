import { NavLink } from "react-router-dom";
import { type ReactNode } from "react";

type GenericLayoutProps = {
    children: ReactNode;
};

export function GenericLayout({children}: GenericLayoutProps) {
    return(
        <div className="generic-layout_container">
            <header className="generic-layout_header">
                <h1><NavLink to="/">ByteBites</NavLink></h1>
                <nav aria-label="Main navigation">
                    <NavLink to="/" end>Home</NavLink>
                </nav>
            </header>
            {children}
        </div>
    ); 
}

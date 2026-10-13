import { type ReactNode } from "react";

type GenericLayoutProps = {
    children: ReactNode;
};

export function GenericLayout({children}: GenericLayoutProps) {
    return(
        <div className="generic-layout_container">
            <header className="generic-layout_header">
                <h1>ByteBites</h1>
            </header>
            {children}
        </div>
    ); 
}
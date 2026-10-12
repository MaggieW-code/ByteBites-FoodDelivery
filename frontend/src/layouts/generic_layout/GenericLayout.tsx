import { type ReactNode } from "react";

type GenericLayoutProps = {
    children: ReactNode;
};

export function GenericLayout({children}: GenericLayoutProps) {
    return(
        <div className="layout">
            <header className="layout-header">
                <h1>ByteBites</h1>
            </header>
            <main className="layout-body">
                {children}
            </main>
        </div>
    ); 
}
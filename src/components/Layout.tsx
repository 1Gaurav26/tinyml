import { ReactNode } from 'react';
import Header from './Header';

interface LayoutProps {
    children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
    return (
        <div className="app-container">
            <Header />
            <main className="main-content">
                {children}
            </main>
        </div>
    );
}

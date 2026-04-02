
import { Car, Radio } from 'lucide-react';
import './Header.css';

export default function Header() {
    return (
        <header className="glass-panel app-header">
            <div className="header-brand">
                <div className="brand-icon">
                    <Car size={24} color="var(--accent-blue)" />
                </div>
                <div>
                    <h1 className="brand-title">Smart Parking</h1>
                    <p className="brand-subtitle">PRP Basement</p>
                </div>
            </div>

            <div className="header-status">
                <div className="live-indicator">
                    <div className="pulse-dot"></div>
                    <span className="live-text">Live Status</span>
                    <Radio size={16} className="radio-icon" />
                </div>
            </div>
        </header>
    );
}

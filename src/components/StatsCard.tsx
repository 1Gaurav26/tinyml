import { ReactNode } from 'react';
import './StatsCard.css';

interface StatsCardProps {
    title: string;
    value: number | string;
    icon: ReactNode;
    trend?: string;
    trendUp?: boolean;
    colorClass: 'blue' | 'green' | 'red' | 'orange';
}

export default function StatsCard({ title, value, icon, trend, trendUp, colorClass }: StatsCardProps) {
    return (
        <div className={`glass-panel stats-card card-${colorClass}`}>
            <div className="stats-header">
                <h3 className="stats-title">{title}</h3>
                <div className={`stats-icon icon-${colorClass}`}>
                    {icon}
                </div>
            </div>
            <div className="stats-body">
                <div className="stats-value">{value}</div>
                {trend && (
                    <div className={`stats-trend ${trendUp ? 'trend-up' : 'trend-down'}`}>
                        {trendUp ? '↑' : '↓'} {trend}
                    </div>
                )}
            </div>
            <div className="stats-bg-glow"></div>
        </div>
    );
}

import { useState, useEffect } from 'react';
import { fetchSlots, startRealTimeUpdates, ParkingSlot } from '../services/mockData';
import StatsCard from './StatsCard';
import ParkingLayout from './ParkingLayout';
import { Layers, CheckCircle, XCircle, User } from 'lucide-react';
import './Dashboard.css';

export default function Dashboard() {
    const [slots, setSlots] = useState<ParkingSlot[]>([]);

    useEffect(() => {
        // Fetch initial slots
        fetchSlots().then(setSlots);

        // Start real-time updates
        const cleanup = startRealTimeUpdates((updatedSlots) => {
            setSlots(updatedSlots);
        });
        return cleanup;
    }, []);

    const totalSlots = slots.length;
    const availableSlots = slots.filter(s => s.status === 'available').length;
    const occupiedSlots = slots.filter(s => s.status === 'occupied').length;
    const reservedSlots = slots.filter(s => s.status === 'reserved').length;

    return (
        <div className="dashboard">
            <div className="stats-grid">
                <StatsCard
                    title="Total Capacity"
                    value={totalSlots}
                    icon={<Layers size={24} />}
                    colorClass="blue"
                />
                <StatsCard
                    title="Available"
                    value={availableSlots}
                    icon={<CheckCircle size={24} />}
                    colorClass="green"
                    trend="2%" trendUp={true}
                />
                <StatsCard
                    title="Occupied"
                    value={occupiedSlots}
                    icon={<XCircle size={24} />}
                    colorClass="red"
                    trend="1%" trendUp={false}
                />
                <StatsCard
                    title="Reserved"
                    value={reservedSlots}
                    icon={<User size={24} />}
                    colorClass="orange"
                />
            </div>

            <div className="layout-section">
                <ParkingLayout slots={slots} />
            </div>
        </div>
    );
}

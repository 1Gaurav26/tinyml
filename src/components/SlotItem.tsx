
import { ParkingSlot } from '../services/mockData';
import { Car, User, Accessibility } from 'lucide-react';
import './SlotItem.css';

interface SlotItemProps {
    slot: ParkingSlot;
}

export default function SlotItem({ slot }: SlotItemProps) {
    const { label, status, type } = slot;

    return (
        <div className={`slot-item slot-${status} slot-${type}`}>
            <div className="slot-glow"></div>

            <div className="slot-visual">
                {status === 'occupied' && (
                    <Car className="slot-car-icon" size={28} absoluteStrokeWidth strokeWidth={1.5} />
                )}
            </div>

            <div className="slot-details">
                <span className="slot-id">{label}</span>
                {type === 'accessible' && <Accessibility size={12} className="type-icon" />}
                {type === 'compact' && <span className="type-icon text-xs">C</span>}
            </div>

            {status === 'reserved' && (
                <div className="reserved-badge">
                    <User size={10} />
                    <span>RSRV</span>
                </div>
            )}
        </div>
    );
}

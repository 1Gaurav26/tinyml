
import { ParkingSlot } from '../services/mockData';
import SlotItem from './SlotItem';
import './ParkingLayout.css';

interface ParkingLayoutProps {
    slots: ParkingSlot[];
}

export default function ParkingLayout({ slots }: ParkingLayoutProps) {
    // Group slots by row
    const rows = ['A', 'B', 'C', 'D', 'E'];
    const gridLayout = rows.map(r => ({
        id: r,
        slots: slots.filter(s => s.id.startsWith(r))
    }));

    return (
        <div className="glass-panel parking-layout">
            <div className="layout-header">
                <h2 className="layout-title">Basement Map</h2>
                <div className="layout-legend">
                    <div className="legend-item"><div className="legend-color bg-green"></div>Available</div>
                    <div className="legend-item"><div className="legend-color bg-red"></div>Occupied</div>
                    <div className="legend-item"><div className="legend-color bg-orange"></div>Reserved</div>
                </div>
            </div>

            <div className="parking-grid-container">
                {gridLayout.map(row => (
                    <div key={row.id} className="parking-row-group">
                        <div className="row-label-container">
                            <span className="row-label">Lane {row.id}</span>
                        </div>
                        <div className="parking-row">
                            {row.slots.map(slot => (
                                <SlotItem key={slot.id} slot={slot} />
                            ))}
                        </div>
                    </div>
                ))}

                {/* Driveway visualization */}
                <div className="driveway driveway-vertical"></div>
                <div className="driveway driveway-horizontal">
                    <span className="driveway-text">MAIN DRIVEWAY (10 km/h)</span>
                </div>
            </div>
        </div>
    );
}

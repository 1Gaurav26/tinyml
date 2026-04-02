export type SlotStatus = 'available' | 'occupied' | 'reserved';

export interface ParkingSlot {
    id: string;
    label: string;
    status: SlotStatus;
    type: 'compact' | 'standard' | 'accessible';
}

// Fetch slots from backend
export const fetchSlots = async (): Promise<ParkingSlot[]> => {
    const response = await fetch('http://localhost:3000/api/slots');
    return response.json();
};

// Start real-time updates by polling
export const startRealTimeUpdates = (
    onUpdate: (updatedSlots: ParkingSlot[]) => void
) => {
    setInterval(async () => {
        const slots = await fetchSlots();
        onUpdate(slots);
    }, 2000); // Poll every 2 seconds
};

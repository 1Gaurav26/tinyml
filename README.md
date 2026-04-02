# Smart Parking Slot Indicator

A modern, dynamic, and visually striking "Smart Parking slot availability indicator" designed for the PRP basement. This project uses React and Vite to deliver a premium user interface with real-time status updates of parking availability.

## Features

- **Real-Time Simulation**: A mock data service that simulates real-world sensor updates, toggling parking slots between available and occupied states realistically.
- **Premium UI Aesthetic**: Beautiful, glassmorphism-inspired design with sleek ambient gradients and a futuristic space-themed color palette.
- **Interactive Parking Grid**: A 2D visual layout of the basement parking lanes with clear color-coded statuses (Green for available, Red/Gray for occupied, Orange for reserved).
- **Live Status Badges**: A pulsing, animated "Live Status" indicator to assure users the data is current.
- **Micro-Animations**: Smooth entry animations, hover-triggered glows, and subtle scale effects for an engaging user experience.
- **Responsive Dashboard**: Stats cards that adapt to different screen sizes, providing an at-a-glance view of total capacity, available, occupied, and reserved slots.
- **Accessible & Compact Types**: Differentiates between standard, compact, and accessible parking spaces with visual badges.

## Tech Stack

- **Framework**: [React 18](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Styling**: Vanilla CSS with advanced variables and modern properties (no heavy CSS frameworks required).

## Getting Started

### Prerequisites

- Node.js (v18 or higher recommended)
- npm or yarn

### Installation

1. Clone the repository or download the source code.
2. Navigate to the project directory:
   ```bash
   cd e:/DLD
   ```
3. Install the dependencies:
   ```bash
   npm install
   ```

### Running the Development Server

Start the local Vite development server:

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser to view the application in action.

### Building for Production

To create a production-ready build:

```bash
npm run build
```

This commands runs both the TypeScript compiler and Vite's build process, outputting optimized static files to the `dist` directory.

## Project Structure

- `src/components/`: Contains all the reusable UI components (`Layout`, `Header`, `Dashboard`, `StatsCard`, `ParkingLayout`, `SlotItem`).
- `src/services/mockData.ts`: The simulated real-time data engine generating the parking grid and its updates.
- `src/index.css`: Global styles, CSS variables for the color palette, and base glassmorphism utilities.

## Customization

To swap the mock data with a real backend API, you'll want to modify the `useEffect` hook inside `src/components/Dashboard.tsx` to fetch and listen to websockets from your real sensors, rather than calling the `simulateRealTimeUpdates` function.

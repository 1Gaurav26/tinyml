# Project Overview: Smart Parking Slot Indicator

## Description
The "Smart Parking Slot Indicator" is a modern, full-stack Internet of Things (IoT) project that provides a dynamic, real-time 2D visual layout of a parking basement. It uses cutting-edge **TinyML** (Machine Learning running on microcontrollers) to determine parking slot availability directly from a camera sensor via an onboard TensorFlow Lite model, transmitting its state to a central server that feeds a beautiful, glassmorphism-inspired React dashboard.

## Code Architecture

The architecture spans three key layers:

1. **Hardware/Edge AI Layer (Arduino / ESP32)**
   - Located in the `arduino/parking_sensor/` folder.
   - Built for the XIAO ESP32S3 Sense development setup equipped with a camera module.
   - It captures 96x96 grayscale images and feeds them into a TensorFlow Lite Micro CNN model (loaded into PSRAM).
   - Once a frame is inferred class "available" or "occupied" (with a configurable >70% confidence threshold), the microcontroller pushes the state change to an MQTT message broker over Wi-Fi.

2. **Backend & Message Broker Layer (Node.js)**
   - Located in `server.js`.
   - Uses an Express.js server and an MQTT Client to listen to `parking/slots/+` and `parking/debug/+` topics routed via a Mosquitto MQTT broker (`mosquitto_local.conf`).
   - The backend runs an in-memory datastore containing the parking grid state. Upon receiving an MQTT event, it updates the specific slot's state. 
   - Exposes a REST API (`/api/slots`) for the frontend to consume. 
   - Also includes legacy fallback detection using `multer` and `sharp` to determine brightness from manual image uploads as a simple heuristic logic mechanism.

3. **Frontend Presentation Layer (React + Vite)**
   - Located in the `src/` folder.
   - A highly-polished UI built utilizing React 18, TypeScript, and Vite.
   - Showcases real-time data on varying slot sizes (compact, standard, accessible) with smooth entry animations powered by `framer-motion`.
   - Utilizes custom "Vanilla CSS" variables for a premium, futuristic space-themed color palette and glassmorphism styling, minimizing dependency on large CSS frameworks.
   - Currently includes mock data simulation via `src/services/mockData.ts` to showcase real-time UI reactions without needing the live hardware setup.

## Tech Stack

**Frontend Frameworks & Libraries:**
- React 18
- TypeScript
- Vite
- Framer Motion (Micro-animations)
- Lucide React (Icons)
- Vanilla CSS (Styling/Theming)

**Backend Frameworks & Protocol Libraries:**
- Node.js (via Express)
- MQTT.js (Broker Communication)
- Sharp (Image Processing)
- Multer (Multipart Form Handling)

**Embedded & Machine Learning:**
- C/C++ (Arduino framework)
- TensorFlow Lite for Microcontrollers (TinyML)
- Mosquitto (MQTT Message Broker)

## Terminology

- **TinyML**: Machine learning techniques meant to operate at the extreme edge, on hardware with low computational power and restricted memory limits, like the ESP32.
- **MQTT**: A lightweight, publish-subscribe network protocol common in IoT to transport messages efficiently.
- **Confidence Threshold**: The baseline percentage (e.g., 70% or 0.70) the AI model must meet before definitively changing the registered status of a parking slot. 
- **Glassmorphism**: A UI design trend prioritizing semi-transparent backgrounds with a soft blur, mimicking frosted glass which gives the frontend a premium aesthetic.

## Data Flow Pipeline

1. **Capture**: The ESP32 camera detects the parking bay area.
2. **Inference**: The edge device processes the frame using the TFLite model, estimating if a car is present.
3. **Publish**: If state changes (from "available" to "occupied") and confidence allows, ESP32 publishes an MQTT signal to `parking/slots/A1`.
4. **Subscribe & Update**: Node.js `server.js` script catches the MQTT topic, registers it, and modifies its internal HTTP JSON slot array.
5. **Render**: The React Dashboard polls the API endpoints or hooks into WebSocket data seamlessly updating the CSS styling corresponding to the layout slot from green (available) to red (occupied).

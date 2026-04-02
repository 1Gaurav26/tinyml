import express from 'express';
import cors from 'cors';
import mqtt from 'mqtt';
import multer from 'multer';
import sharp from 'sharp';

const app = express();
app.use(cors());
app.use(express.json());

// Multer for image uploads
const upload = multer({ dest: 'uploads/' });

// In-memory storage for slots (hardcoded for simplicity)
const initialSlots = [
  { id: 'A1', label: 'A1', status: 'available', type: 'standard' },
  { id: 'A2', label: 'A2', status: 'occupied', type: 'standard' },
  // Add more as needed
];
let slots = initialSlots;

// MQTT setup
const mqttClient = mqtt.connect('mqtt://localhost:1883'); // Assuming Mosquitto on localhost
mqttClient.on('connect', () => {
  console.log('Connected to MQTT broker');
  mqttClient.subscribe('parking/slots/+');  // slot status updates
  mqttClient.subscribe('parking/debug/+');  // confidence / debug info
});

mqttClient.on('message', (topic, message) => {
  const parts = topic.split('/');
  const slotId = parts[2];

  if (parts[1] === 'slots') {
    const status = message.toString();
    const slot = slots.find(s => s.id === slotId);
    if (slot) {
      slot.status = status;
      console.log(`[${slotId}] status → ${status}`);
    }
  } else if (parts[1] === 'debug') {
    try {
      const data = JSON.parse(message.toString());
      const method = data.method || 'brightness';
      const conf   = data.confidence != null ? ` (${(data.confidence * 100).toFixed(1)}% conf, ${method})` : '';
      console.log(`[${slotId}] debug: ${data.status}${conf}`);
    } catch (_) { /* ignore malformed debug messages */ }
  }
});

// Endpoint to get current slots
app.get('/api/slots', (req, res) => {
  res.json(slots);
});

// Endpoint to upload image and detect occupancy
app.post('/api/upload-image/:slotId', upload.single('image'), async (req, res) => {
  const { slotId } = req.params;
  if (!req.file) return res.status(400).send('No image uploaded');

  try {
    // Analyze image: get average brightness
    const image = sharp(req.file.path);
    const { data, info } = await image.raw().toBuffer({ resolveWithObject: true });
    let totalBrightness = 0;
    for (let i = 0; i < data.length; i += 3) {
      const r = data[i], g = data[i+1], b = data[i+2];
      totalBrightness += (r + g + b) / 3;
    }
    const avgBrightness = totalBrightness / (data.length / 3);

    // Simple logic: if brightness < 100, occupied (dark = car present)
    const status = avgBrightness < 100 ? 'occupied' : 'available';

    // Update slot
    const slot = slots.find(s => s.id === slotId);
    if (slot) {
      slot.status = status;
      console.log(`Updated slot ${slotId} to ${status} via image`);
    }

    res.status(200).send('Image processed');
  } catch (err) {
    console.error(err);
    res.status(500).send('Error processing image');
  }
});

app.listen(3000, () => console.log('Server running on port 3000'));
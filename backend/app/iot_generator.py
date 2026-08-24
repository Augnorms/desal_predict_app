import random
import math
import time
from typing import Dict, Any
from app.predict import predict
from app.database import save_entry

class IoTTelemetryGenerator:
    def __init__(self):
        self.step = 0
        self.active_nodes = ['IOT-NODE-01', 'IOT-NODE-02', 'IOT-NODE-03']

    def generate_raw_reading(self, operator_id: str = None) -> Dict[str, Any]:
        """Generate dynamic, realistic IoT telemetry reading with natural micro-fluctuations."""
        self.step += 1
        
        # Smooth diurnal temperature wave (day/night micro ripple)
        temp_wave = math.sin(self.step * 0.1) * 0.6
        
        # Realistic sensor micro-variations around baseline target
        feed_flowrate = round(max(72.0, min(78.0, 75.0 + random.gauss(0, 0.8))), 2)
        feed_tds = int(max(770, min(830, round(800 + random.gauss(0, 8.0)))))
        feed_salinity = round(max(24.0, min(26.0, 25.0 + random.gauss(0, 0.3))), 2)
        temperature = round(max(24.5, min(27.5, 26.0 + temp_wave + random.uniform(-0.15, 0.15))), 2)
        recovery = round(max(73.0, min(77.0, 75.0 + random.gauss(0, 0.6))), 2)
        flux = round(max(19.0, min(21.0, 20.0 + random.gauss(0, 0.3))), 2)
        pressure_drop = round(max(0.45, min(0.55, 0.50 + random.uniform(-0.02, 0.02))), 2)

        selected_operator = operator_id or random.choice(self.active_nodes)

        return {
            'operator_id': selected_operator,
            'feed_flowrate': feed_flowrate,
            'feed_tds': feed_tds,
            'feed_salinity': feed_salinity,
            'temperature': temperature,
            'recovery': recovery,
            'flux': flux,
            'pressure_drop': pressure_drop,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def generate_and_predict(self, operator_id: str = None) -> Dict[str, Any]:
        """Generate telemetry reading, run ML prediction, save to DB, and return combined payload."""
        raw = self.generate_raw_reading(operator_id)

        # Format input dictionary matching model feature expectations
        model_input = {
            'Feed Flowrate (m3/h)': raw['feed_flowrate'],
            'Feed TDS (ppm)': raw['feed_tds'],
            'Feed Salinity (g/L)': raw['feed_salinity'],
            'Feed Temperature (°C)': raw['temperature'],
            'Recovery (%)': raw['recovery'],
            'Flux (LMH)': raw['flux'],
            'Pressure Drop (bar)': raw['pressure_drop']
        }

        # Run machine learning inference
        prediction_result = predict(model_input)

        # Prepare database record payload
        db_entry = {
            'operator_id': raw['operator_id'],
            'feed_flowrate': raw['feed_flowrate'],
            'feed_tds': raw['feed_tds'],
            'feed_salinity': raw['feed_salinity'],
            'temperature': raw['temperature'],
            'recovery': raw['recovery'],
            'flux': raw['flux'],
            'pressure_drop': raw['pressure_drop'],
            'permeate_flowrate': prediction_result['flowrate'],
            'permeate_tds': prediction_result['tds'],
            'status': prediction_result['status']
        }

        # Save to SQLite database
        entry_id = save_entry(db_entry)

        # Return rich response
        return {
            'id': entry_id,
            'timestamp': raw['timestamp'],
            'telemetry': raw,
            'prediction': prediction_result
        }

# Global singleton instance
generator = IoTTelemetryGenerator()

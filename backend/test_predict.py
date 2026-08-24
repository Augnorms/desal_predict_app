# pyrefly: ignore [missing-import]
from app.predict import predict  # Only import predict function

# Sample data
test_data = {
    'Feed Flowrate (m3/h)': 100.0,
    'Feed TDS (ppm)': 3000.0,
    'Feed Salinity (g/L)': 25.0,
    'Feed Temperature (°C)': 26.0,
    'Recovery (%)': 45.0,
    'Flux (LMH)': 18.0,  # Changed from 12.5 to a more realistic value
    'Pressure Drop (bar)': 2.0  # Changed from 6.5 to a more realistic value
}

# Get prediction
prediction = predict(test_data)

print("Prediction Result:")
print(f"   Permeate Flowrate: {prediction['flowrate']} m3/h")
print(f"   Permeate TDS: {prediction['tds']} ppm")
print(f"   Status: {prediction['status']}")
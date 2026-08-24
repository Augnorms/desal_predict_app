# pyrefly: ignore [missing-import]
import joblib
import pandas as pd
import os

# Define feature names exactly as the model expects
feature_names = [
    'Feed Flowrate (m3/h)',
    'Feed TDS (ppm)',
    'Feed Salinity (g/L)',
    'Feed Temperature (°C)',
    'Recovery (%)',
    'Flux (LMH)',
    'Pressure Drop (bar)'
]

# Path to models - resolve relative to this file's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "saved_models")

# Load models with the CORRECT file names
model_permeate_flowrate = joblib.load(os.path.join(MODEL_PATH, "permeate_flowrate_model_rf.pkl"))
model_permeate_tds = joblib.load(os.path.join(MODEL_PATH, "permeate_flowtds_model_rf.pkl"))

print("Models loaded successfully!")

def predict(data):
    '''Make prediction using two models'''
    
    # Create DataFrame with column names
    feature = pd.DataFrame([[
        data['Feed Flowrate (m3/h)'],
        data['Feed TDS (ppm)'],
        data['Feed Salinity (g/L)'],
        data['Feed Temperature (°C)'],
        data['Recovery (%)'],
        data['Flux (LMH)'],
        data['Pressure Drop (bar)']
    ]], columns=feature_names)
    
    flowrate = model_permeate_flowrate.predict(feature)[0]
    tds = model_permeate_tds.predict(feature)[0]

    # More detailed status
    if tds < 50:
        status = 'Excellent'
    elif tds < 100:
        status = 'Good'
    elif tds < 200:
        status = 'Warning'
    else:
        status = 'Poor'

    return {
        "flowrate": round(float(flowrate), 2),
        "tds": round(float(tds), 2),
        "status": status
    }
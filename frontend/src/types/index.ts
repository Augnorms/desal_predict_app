export interface PredictionInput {
  operator_id?: string
  Feed_Flowrate_m3h: number
  Feed_TDS_ppm: number
  Feed_Salinity_gL: number
  Feed_Temperature_C: number
  Recovery_percent: number
  Flux_LMH: number
  Pressure_Drop_bar: number
}

export interface PredictionResult {
  flowrate: number
  tds: number
  status: 'Excellent' | 'Good' | 'Warning' | 'Poor' | string
}

export interface PredictAndSaveResponse {
  entry_id: number
  prediction: PredictionResult
}

export interface DbEntry {
  id: number
  operator_id: string
  feed_flowrate: number
  feed_tds: number
  feed_salinity: number
  temperature: number
  recovery: number
  flux: number
  pressure_drop: number
  permeate_flowrate?: number
  permeate_tds?: number
  status?: string
  timestamp: string
}

export interface ScadaParameter {
  id: string
  stream: 'FEED' | 'PERMEATE' | 'CALCULATED'
  parameter: string
  liveValue: number
  unit: string
  threshold: string
  status: 'NORMAL' | 'CAUTION' | 'WARNING' | 'CRITICAL'
}

export interface SelectOption {
  label: string
  value: string | number
}

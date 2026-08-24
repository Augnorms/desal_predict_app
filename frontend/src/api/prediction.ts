import { api } from './index'
import type { PredictionInput, PredictAndSaveResponse, DbEntry } from '../types'

export async function predictAndSave(data: PredictionInput): Promise<PredictAndSaveResponse> {
  const response = await api.post<PredictAndSaveResponse>('/predict-and-save', data)
  return response.data
}

export async function getEntries(): Promise<DbEntry[]> {
  const response = await api.get('/entries')
  const rawData = response.data

  if (!Array.isArray(rawData)) return []

  return rawData.map((row: any) => {
    // If SQLite returned a tuple list:
    // [id, operator_id, feed_flowrate, feed_tds, feed_salinity, temperature, recovery, flux, pressure_drop, permeate_flowrate, permeate_tds, status, timestamp]
    if (Array.isArray(row)) {
      return {
        id: row[0],
        operator_id: row[1] || 'Unknown',
        feed_flowrate: Number(row[2] || 0),
        feed_tds: Number(row[3] || 0),
        feed_salinity: Number(row[4] || 0),
        temperature: Number(row[5] || 0),
        recovery: Number(row[6] || 0),
        flux: Number(row[7] || 0),
        pressure_drop: Number(row[8] || 0),
        permeate_flowrate: row[9] !== undefined ? Number(row[9]) : undefined,
        permeate_tds: row[10] !== undefined ? Number(row[10]) : undefined,
        status: row[11] || undefined,
        timestamp: row[12] || row[9] || new Date().toISOString()
      }
    }

    // If returned as object:
    return {
      id: row.id,
      operator_id: row.operator_id || 'Unknown',
      feed_flowrate: Number(row.feed_flowrate || 0),
      feed_tds: Number(row.feed_tds || 0),
      feed_salinity: Number(row.feed_salinity || 0),
      temperature: Number(row.temperature || 0),
      recovery: Number(row.recovery || 0),
      flux: Number(row.flux || 0),
      pressure_drop: Number(row.pressure_drop || 0),
      permeate_flowrate: row.permeate_flowrate,
      permeate_tds: row.permeate_tds,
      status: row.status,
      timestamp: row.timestamp || new Date().toISOString()
    }
  })
}

export async function getEntryById(id: number): Promise<DbEntry | null> {
  try {
    const response = await api.get(`/entry/${id}`)
    const row = response.data
    if (!row) return null

    if (Array.isArray(row)) {
      return {
        id: row[0],
        operator_id: row[1] || 'Unknown',
        feed_flowrate: Number(row[2] || 0),
        feed_tds: Number(row[3] || 0),
        feed_salinity: Number(row[4] || 0),
        temperature: Number(row[5] || 0),
        recovery: Number(row[6] || 0),
        flux: Number(row[7] || 0),
        pressure_drop: Number(row[8] || 0),
        permeate_flowrate: row[9] !== undefined ? Number(row[9]) : undefined,
        permeate_tds: row[10] !== undefined ? Number(row[10]) : undefined,
        status: row[11] || undefined,
        timestamp: row[12] || row[9] || new Date().toISOString()
      }
    }
    return row as DbEntry
  } catch {
    return null
  }
}

export async function triggerIotTick() {
  const res = await api.post('/iot/tick')
  return res.data
}

export async function startIotStream() {
  const res = await api.post('/iot/start')
  return res.data
}

export async function stopIotStream() {
  const res = await api.post('/iot/stop')
  return res.data
}

export async function configIotStream(intervalSeconds: number) {
  const res = await api.post(`/iot/config?interval_seconds=${intervalSeconds}`)
  return res.data
}

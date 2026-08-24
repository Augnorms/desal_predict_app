<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { CheckCircle2, AlertTriangle, Download, RefreshCw, Database } from 'lucide-vue-next'
import Card from '../components/ui/Card.vue'
import Button from '../components/ui/Button.vue'
import Badge from '../components/ui/Badge.vue'
import type { DbEntry } from '../types'
import { getEntries } from '../api/prediction'

const router = useRouter()
const isRefreshing = ref(false)
const lastUpdatedTime = ref<string>('')
const recentHistory = ref<DbEntry[]>([])
const isLoadedFromDb = ref(false)

const latestPrediction = computed(() => {
  if (recentHistory.value.length === 0) {
    return { flowrate: 145.2, tds: 22, status: 'Good', operator: 'OP-001' }
  }
  const latest = recentHistory.value[recentHistory.value.length - 1]
  return {
    flowrate: latest.permeate_flowrate ?? 0,
    tds: latest.permeate_tds ?? 0,
    status: latest.status || 'Good',
    operator: latest.operator_id || 'OP-001'
  }
})

function generateSparkline(values: number[], width = 200, height = 40): string {
  if (values.length < 2) {
    return 'M0 30 Q 30 35, 60 20 T 120 25 T 160 10 T 200 20'
  }
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1

  return values.map((val, idx) => {
    const x = (idx / (values.length - 1)) * width
    const y = height - ((val - min) / range) * (height - 12) - 6
    return `${idx === 0 ? 'M' : 'L'}${x.toFixed(1)} ${y.toFixed(1)}`
  }).join(' ')
}

const displayedEntries = computed(() => {
  return recentHistory.value.slice().reverse().slice(0, 10)
})

const flowrateSparklinePath = computed(() => {
  const values = recentHistory.value
    .map(e => e.permeate_flowrate ?? e.feed_flowrate)
    .filter((v): v is number => v !== undefined && !isNaN(v))
  return generateSparkline(values)
})

const tdsSparklinePath = computed(() => {
  const values = recentHistory.value
    .map(e => e.permeate_tds ?? e.feed_tds)
    .filter((v): v is number => v !== undefined && !isNaN(v))
  return generateSparkline(values)
})

const loadLatestEntry = async () => {
  isRefreshing.value = true
  try {
    const entries = await getEntries()
    recentHistory.value = entries
    isLoadedFromDb.value = entries.length > 0
    lastUpdatedTime.value = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch (e) {
    console.error('Failed to load entries from backend', e)
  } finally {
    isRefreshing.value = false
  }
}

const exportCSV = () => {
  if (recentHistory.value.length === 0) return
  const headers = ['ID', 'Operator', 'Feed Flowrate (m3/h)', 'Feed TDS (ppm)', 'Feed Salinity (g/L)', 'Temperature (C)', 'Recovery (%)', 'Flux (LMH)', 'Pressure Drop (bar)', 'Permeate Flowrate (m3/h)', 'Permeate TDS (ppm)', 'Status', 'Timestamp']
  const rows = recentHistory.value.map(row => [
    row.id,
    row.operator_id,
    row.feed_flowrate,
    row.feed_tds,
    row.feed_salinity,
    row.temperature,
    row.recovery,
    row.flux,
    row.pressure_drop,
    row.permeate_flowrate ?? '',
    row.permeate_tds ?? '',
    row.status ?? '',
    row.timestamp
  ])
  const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', `plant_db_entries_${new Date().toISOString().slice(0,10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

onMounted(() => {
  loadLatestEntry()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Top Action Bar & Title -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl font-bold text-slate-900 tracking-tight">System Performance Overview</h1>
        <p class="text-xs text-slate-500 mt-0.5 flex items-center gap-2">
          <span>Last updated: {{ lastUpdatedTime || 'Fetching backend live data...' }}</span>
          <button @click="loadLatestEntry" class="text-slate-400 hover:text-slate-700" title="Refresh">
            <RefreshCw class="w-3 h-3" :class="{ 'animate-spin': isRefreshing }" />
          </button>
        </p>
      </div>

      <!-- Mode Selector -->
      <div class="inline-flex p-1 bg-slate-200/80 rounded-lg border border-slate-300/50 shadow-inner">
        <Button variant="ghost" size="sm" class="rounded-md text-xs font-semibold text-slate-700 hover:text-slate-900 py-1.5" @click="router.push('/iot-predictive-center')">
          IOT Mode Live
        </Button>
        <Button variant="ghost" size="sm" class="rounded-md text-xs font-semibold text-slate-700 hover:text-slate-900 py-1.5" @click="router.push('/prediction-center')">
          Manual Entry Mode
        </Button>
      </div>
    </div>

    <!-- Predictive Engine Banner -->
    <div class="p-4 border rounded-xl flex items-center justify-between shadow-xs transition-colors" :class="latestPrediction.status === 'Warning' || latestPrediction.status === 'Poor' ? 'bg-amber-50/80 border-amber-200' : 'bg-emerald-50/80 border-emerald-200'">
      <div class="flex items-center gap-3.5">
        <div class="w-9 h-9 rounded-full flex items-center justify-center shrink-0" :class="latestPrediction.status === 'Warning' || latestPrediction.status === 'Poor' ? 'bg-amber-500/15' : 'bg-emerald-500/15'">
          <AlertTriangle v-if="latestPrediction.status === 'Warning' || latestPrediction.status === 'Poor'" class="w-5 h-5 text-amber-600" />
          <CheckCircle2 v-else class="w-5 h-5 text-emerald-600" />
        </div>
        <div>
          <span class="text-[10px] font-bold uppercase tracking-wider" :class="latestPrediction.status === 'Warning' || latestPrediction.status === 'Poor' ? 'text-amber-800/80' : 'text-emerald-800/80'">Predictive Engine</span>
          <h3 class="text-sm font-bold flex items-center gap-2" :class="latestPrediction.status === 'Warning' || latestPrediction.status === 'Poor' ? 'text-amber-950' : 'text-emerald-950'">
            Latest Status: <span class="font-bold" :class="latestPrediction.status === 'Warning' || latestPrediction.status === 'Poor' ? 'text-amber-700' : 'text-emerald-700'">{{ latestPrediction.status }}</span>
          </h3>
        </div>
      </div>
      <div class="flex items-center gap-3 text-xs">
        <span class="text-slate-600 font-semibold">Active Operator: <span class="text-slate-900 font-bold font-mono">{{ latestPrediction.operator }}</span></span>
      </div>
    </div>

    <!-- KPI Metric Cards Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
      <!-- Card 1: Flowrate -->
      <Card class="relative overflow-hidden">
        <div class="flex items-start justify-between">
          <div>
            <span class="text-[11px] font-bold uppercase tracking-wider text-slate-500">Predicted Permeate Flowrate</span>
            <div class="flex items-baseline gap-2 mt-2">
              <span class="text-3xl font-extrabold text-slate-900 font-mono tracking-tight">{{ latestPrediction.flowrate }}</span>
              <span class="text-sm font-semibold text-slate-500">m³/h</span>
            </div>
          </div>
          <span class="inline-flex items-center text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
            Live ML Output
          </span>
        </div>
        <!-- Dynamic Sparkline Curve -->
        <div class="mt-4 h-12 w-full">
          <svg class="w-full h-full overflow-visible" viewBox="0 0 200 40">
            <path :d="flowrateSparklinePath" fill="none" stroke="#0284c7" stroke-width="2.5" stroke-linecap="round" />
          </svg>
        </div>
      </Card>

      <!-- Card 2: TDS -->
      <Card class="relative overflow-hidden">
        <div class="flex items-start justify-between">
          <div>
            <span class="text-[11px] font-bold uppercase tracking-wider text-slate-500">Predicted Permeate TDS</span>
            <div class="flex items-baseline gap-2 mt-2">
              <span class="text-3xl font-extrabold text-slate-900 font-mono tracking-tight">{{ latestPrediction.tds }}</span>
              <span class="text-sm font-semibold text-slate-500">ppm</span>
            </div>
          </div>
          <span class="inline-flex items-center text-xs font-semibold text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
            Live ML Output
          </span>
        </div>
        <!-- Dynamic Sparkline Curve -->
        <div class="mt-4 h-12 w-full">
          <svg class="w-full h-full overflow-visible" viewBox="0 0 200 40">
            <path :d="tdsSparklinePath" fill="none" stroke="#f97316" stroke-width="2.5" stroke-opacity="0.8" stroke-linecap="round" />
          </svg>
        </div>
      </Card>
    </div>

    <!-- Real Backend Database Table Section -->
    <Card no-padding class="overflow-hidden border border-slate-200">
      <template #header>
        <h3 class="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
          <Database class="w-4 h-4 text-emerald-600" />
          <span>Plant Database Records (`plant_data.db`)</span>
          <span v-if="isLoadedFromDb" class="text-[10px] bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded border border-emerald-300 flex items-center gap-1 font-sans">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            {{ recentHistory.length }} Records Live
          </span>
        </h3>
      </template>
      <template #action>
        <Button variant="outline" size="sm" class="text-xs font-medium" @click="exportCSV">
          <template #icon><Download class="w-3.5 h-3.5 text-slate-600" /></template>
          Export CSV
        </Button>
      </template>

      <!-- Database Table -->
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-xs">
          <thead>
            <tr class="bg-slate-100/90 text-slate-600 uppercase font-bold tracking-wider text-[11px] border-b border-slate-200 whitespace-nowrap">
              <th class="py-3 px-4">ID</th>
              <th class="py-3 px-4">Operator</th>
              <th class="py-3 px-4">Feed Flow (m³/h)</th>
              <th class="py-3 px-4">Feed TDS (ppm)</th>
              <th class="py-3 px-4">Salinity (g/L)</th>
              <th class="py-3 px-4">Temp (°C)</th>
              <th class="py-3 px-4">Recovery (%)</th>
              <th class="py-3 px-4">Flux (LMH)</th>
              <th class="py-3 px-4">Press. Drop (bar)</th>
              <th class="py-3 px-4 text-blue-700">Perm. Flow (m³/h)</th>
              <th class="py-3 px-4 text-blue-700">Perm. TDS (ppm)</th>
              <th class="py-3 px-4">Status</th>
              <th class="py-3 px-4">Timestamp</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 font-mono">
            <tr 
              v-for="entry in displayedEntries" 
              :key="entry.id"
              class="hover:bg-slate-50 transition-colors"
            >
              <td class="py-3 px-4 font-bold text-slate-900">#{{ entry.id }}</td>
              <td class="py-3 px-4 text-slate-700 font-sans font-semibold">{{ entry.operator_id }}</td>
              <td class="py-3 px-4 text-slate-900">{{ entry.feed_flowrate }}</td>
              <td class="py-3 px-4 text-slate-900">{{ entry.feed_tds }}</td>
              <td class="py-3 px-4 text-slate-900">{{ entry.feed_salinity }}</td>
              <td class="py-3 px-4 text-slate-900">{{ entry.temperature }}</td>
              <td class="py-3 px-4 text-slate-900">{{ entry.recovery }}%</td>
              <td class="py-3 px-4 text-slate-900">{{ entry.flux }}</td>
              <td class="py-3 px-4 text-slate-900">{{ entry.pressure_drop }}</td>
              <td class="py-3 px-4 text-emerald-700 font-extrabold">{{ entry.permeate_flowrate ?? '-' }}</td>
              <td class="py-3 px-4 text-emerald-700 font-extrabold">{{ entry.permeate_tds ?? '-' }}</td>
              <td class="py-3 px-4">
                <Badge :variant="entry.status === 'Good' || entry.status === 'Excellent' ? 'success' : 'warning'" size="sm">
                  {{ entry.status || 'Good' }}
                </Badge>
              </td>
              <td class="py-3 px-4 text-slate-500 text-[11px] font-sans whitespace-nowrap">{{ entry.timestamp }}</td>
            </tr>
            <tr v-if="recentHistory.length === 0">
              <td colspan="13" class="py-8 text-center text-slate-400 font-sans text-xs">
                No database entries found. Use Manual Entry Mode to run predictions.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
  </div>
</template>


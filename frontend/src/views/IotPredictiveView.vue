<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  Activity, 
  Play, 
  Pause, 
  RefreshCw, 
  Zap, 
  Gauge, 
  Droplets, 
  Thermometer, 
  TrendingUp, 
  CheckCircle2, 
  Clock,
  Radio,
  Sliders,
  Database
} from 'lucide-vue-next'
import Card from '../components/ui/Card.vue'
import Button from '../components/ui/Button.vue'
import Badge from '../components/ui/Badge.vue'
import type { DbEntry, PredictionInput } from '../types'
import { 
  getEntries, 
  triggerIotTick, 
  startIotStream, 
  stopIotStream, 
  configIotStream 
} from '../api/prediction'

// Streaming & Control States
const isStreaming = ref(false)
const pollIntervalMs = ref(3000)
const isSimulating = ref(false)
const lastSyncTime = ref<string>('')
const telemetryLog = ref<DbEntry[]>([])
const socket = ref<WebSocket | null>(null)

// Current Live Telemetry Input Feed (Baseline Parameters)
const liveFeed = ref<PredictionInput>({
  operator_id: 'IOT-NODE-01',
  Feed_Flowrate_m3h: 75.0,
  Feed_TDS_ppm: 800,
  Feed_Salinity_gL: 25.0,
  Feed_Temperature_C: 26.0,
  Recovery_percent: 75.0,
  Flux_LMH: 20.0,
  Pressure_Drop_bar: 0.5
})

interface CurrentPrediction {
  flowrate: number
  tds: number
  status: string
}

// Current Live Predicted Outputs
const currentPrediction = ref<CurrentPrediction>({
  flowrate: 35.0,
  tds: 85.0,
  status: 'Good'
})

// Metrics & trends
const totalPackets = computed(() => telemetryLog.value.length)

const flowrateTrend = computed(() => {
  if (telemetryLog.value.length < 2) return 0
  const curr = telemetryLog.value[telemetryLog.value.length - 1]?.permeate_flowrate || 0
  const prev = telemetryLog.value[telemetryLog.value.length - 2]?.permeate_flowrate || 0
  if (!prev) return 0
  return Number((((curr - prev) / prev) * 100).toFixed(1))
})

const tdsTrend = computed(() => {
  if (telemetryLog.value.length < 2) return 0
  const curr = telemetryLog.value[telemetryLog.value.length - 1]?.permeate_tds || 0
  const prev = telemetryLog.value[telemetryLog.value.length - 2]?.permeate_tds || 0
  if (!prev) return 0
  return Number((((curr - prev) / prev) * 100).toFixed(1))
})

// Sparkline generators
const flowrateHistory = computed(() => {
  return telemetryLog.value.slice(-12).map(e => e.permeate_flowrate ?? 35)
})

const tdsHistory = computed(() => {
  return telemetryLog.value.slice(-12).map(e => e.permeate_tds ?? 85)
})

function buildSparklinePath(data: number[], width = 160, height = 36): string {
  if (data.length < 2) return 'M0 18 L160 18'
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  return data.map((val, i) => {
    const x = (i / (data.length - 1)) * width
    const y = height - ((val - min) / range) * (height - 8) - 4
    return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)} ${y.toFixed(1)}`
  }).join(' ')
}

// Handle incoming telemetry tick from backend
function handleIncomingTick(data: any) {
  const tel = data.telemetry
  const pred = data.prediction

  if (tel) {
    liveFeed.value = {
      operator_id: tel.operator_id || 'IOT-NODE-01',
      Feed_Flowrate_m3h: tel.feed_flowrate,
      Feed_TDS_ppm: tel.feed_tds,
      Feed_Salinity_gL: tel.feed_salinity,
      Feed_Temperature_C: tel.temperature,
      Recovery_percent: tel.recovery,
      Flux_LMH: tel.flux,
      Pressure_Drop_bar: tel.pressure_drop
    }
  }

  if (pred) {
    currentPrediction.value = {
      flowrate: Number(pred.flowrate || 0),
      tds: Number(pred.tds || 0),
      status: pred.status || 'Good'
    }
  }

  lastSyncTime.value = new Date().toLocaleTimeString()
  refreshHistory()
}

const streamTimer = ref<any>(null)

function startStreamTimer() {
  stopStreamTimer()
  streamTimer.value = setInterval(() => {
    if (isStreaming.value) {
      handleSimulateTick()
    }
  }, pollIntervalMs.value)
}

function stopStreamTimer() {
  if (streamTimer.value) {
    clearInterval(streamTimer.value)
    streamTimer.value = null
  }
}

// Connect to backend WebSocket endpoint
function connectWebSocket() {
  try {
    const wsUrl = 'ws://127.0.0.1:8000/ws/iot'
    socket.value = new WebSocket(wsUrl)

    socket.value.onopen = () => {
      isStreaming.value = true
      lastSyncTime.value = new Date().toLocaleTimeString()
      startStreamTimer()
    }

    socket.value.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg.data) {
          handleIncomingTick(msg.data)
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err)
      }
    }

    socket.value.onclose = () => {
      isStreaming.value = false
      stopStreamTimer()
    }

    socket.value.onerror = (err) => {
      console.error('WebSocket error:', err)
      isStreaming.value = false
    }
  } catch (err) {
    console.error('Failed to create WebSocket connection:', err)
  }
}

async function refreshHistory() {
  try {
    const entries = await getEntries()
    telemetryLog.value = entries
    if (entries.length > 0) {
      const latest = entries[entries.length - 1]
      if (latest.permeate_flowrate !== undefined && latest.permeate_tds !== undefined) {
        currentPrediction.value = {
          flowrate: Number(latest.permeate_flowrate),
          tds: Number(latest.permeate_tds),
          status: latest.status || 'Good'
        }
      }
    }
  } catch (err) {
    console.error('Failed to fetch history:', err)
  }
}

async function toggleStream() {
  try {
    if (isStreaming.value) {
      await stopIotStream()
      isStreaming.value = false
      stopStreamTimer()
    } else {
      await startIotStream()
      isStreaming.value = true
      startStreamTimer()
    }
  } catch (err) {
    console.error('Error toggling stream:', err)
  }
}

async function handleSimulateTick() {
  if (isSimulating.value) return
  isSimulating.value = true

  try {
    const res = await triggerIotTick()
    if (res && res.data) {
      handleIncomingTick(res.data)
    }
  } catch (err) {
    console.error('Error triggering IoT tick:', err)
  } finally {
    isSimulating.value = false
  }
}

async function updatePollInterval(ms: number) {
  pollIntervalMs.value = ms
  try {
    await configIotStream(ms / 1000)
  } catch (err) {
    console.error('Error updating interval:', err)
  }
  if (isStreaming.value) {
    startStreamTimer()
  }
}

onMounted(async () => {
  await refreshHistory()
  connectWebSocket()
  startStreamTimer()
})

onUnmounted(() => {
  stopStreamTimer()
  if (socket.value) {
    socket.value.close()
    socket.value = null
  }
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header & Telemetry Stream Control Toolbar -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
      <div>
        <div class="flex items-center gap-2.5">
          <h1 class="text-xl font-bold text-slate-900 tracking-tight">IoT Predictive Telemetry Center</h1>
          <span 
            class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider"
            :class="isStreaming ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-amber-100 text-amber-800 border border-amber-300'"
          >
            <span class="relative flex h-2 w-2">
              <span v-if="isStreaming" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2" :class="isStreaming ? 'bg-emerald-500' : 'bg-amber-500'"></span>
            </span>
            {{ isStreaming ? 'Live Stream Connected' : 'Stream Paused' }}
          </span>
        </div>
        <p class="text-xs text-slate-500 mt-1 flex items-center gap-2">
          <span>Real-time WebSocket ingest with backend ML model predictions.</span>
          <span class="text-slate-300">•</span>
          <span class="flex items-center gap-1 text-slate-600 font-medium">
            <Clock class="w-3.5 h-3.5 text-slate-400" />
            Last Sync: {{ lastSyncTime || 'Connecting...' }}
          </span>
        </p>
      </div>

      <!-- Controls -->
      <div class="flex items-center gap-3 flex-wrap">
        <!-- Frequency Selector -->
        <div class="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs">
          <span class="text-[11px] font-semibold text-slate-500 px-2 flex items-center gap-1">
            <Sliders class="w-3 h-3" /> Interval:
          </span>
          <button 
            v-for="ms in [3000, 5000, 10000]" 
            :key="ms"
            @click="updatePollInterval(ms)"
            class="px-2 py-1 rounded text-[11px] font-bold transition-all"
            :class="pollIntervalMs === ms ? 'bg-white text-slate-900 shadow-xs border border-slate-200' : 'text-slate-600 hover:text-slate-900'"
          >
            {{ ms / 1000 }}s
          </button>
        </div>

        <!-- Play / Pause Stream -->
        <Button 
          :variant="isStreaming ? 'outline' : 'primary'" 
          size="sm" 
          class="font-semibold text-xs py-1.5"
          @click="toggleStream"
        >
          <template #icon>
            <Pause v-if="isStreaming" class="w-3.5 h-3.5 text-amber-600" />
            <Play v-else class="w-3.5 h-3.5 text-emerald-400 fill-current" />
          </template>
          {{ isStreaming ? 'Pause Stream' : 'Resume Stream' }}
        </Button>

        <!-- Manual Simulation Trigger -->
        <Button 
          variant="secondary" 
          size="sm" 
          class="font-semibold text-xs py-1.5"
          :loading="isSimulating"
          @click="handleSimulateTick"
        >
          <template #icon v-if="!isSimulating">
            <RefreshCw class="w-3.5 h-3.5 text-slate-600" />
          </template>
          Simulate Tick
        </Button>
      </div>
    </div>

    <!-- Top Predicted Output KPI Banner -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <!-- KPI 1: Predicted Permeate Flowrate -->
      <Card no-padding class="border border-slate-200/90 shadow-sm relative overflow-hidden">
        <div class="p-5">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <Zap class="w-4 h-4 text-cyan-600" />
              Predicted Permeate Flowrate
            </span>
            <span 
              class="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full"
              :class="flowrateTrend >= 0 ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'"
            >
              <TrendingUp class="w-3 h-3" :class="flowrateTrend < 0 ? 'rotate-180' : ''" />
              {{ flowrateTrend >= 0 ? '+' : '' }}{{ flowrateTrend }}%
            </span>
          </div>

          <div class="mt-3 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold text-slate-900 tracking-tight">
              {{ currentPrediction.flowrate.toFixed(2) }}
            </span>
            <span class="text-sm font-semibold text-slate-500">m³/h</span>
          </div>

          <div class="mt-4 flex items-center justify-between text-xs text-slate-500 border-t border-slate-100 pt-3">
            <span>Target Baseline: <strong class="text-slate-700 font-semibold">30.0 - 40.0 m³/h</strong></span>
            <!-- Sparkline SVG -->
            <svg class="w-24 h-8 text-cyan-500 stroke-current fill-none stroke-[2.5]" viewBox="0 0 160 36">
              <path :d="buildSparklinePath(flowrateHistory)" />
            </svg>
          </div>
        </div>
        <div class="h-1 bg-cyan-500 w-full"></div>
      </Card>

      <!-- KPI 2: Predicted Permeate TDS -->
      <Card no-padding class="border border-slate-200/90 shadow-sm relative overflow-hidden">
        <div class="p-5">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <Droplets class="w-4 h-4 text-blue-600" />
              Predicted Permeate TDS
            </span>
            <div class="flex items-center gap-1.5">
              <span 
                class="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full"
                :class="tdsTrend <= 0 ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'"
              >
                <TrendingUp class="w-3 h-3" :class="tdsTrend > 0 ? 'rotate-180' : ''" />
                {{ tdsTrend >= 0 ? '+' : '' }}{{ tdsTrend }}%
              </span>
              <Badge 
                :variant="currentPrediction.status === 'Excellent' || currentPrediction.status === 'Good' ? 'success' : currentPrediction.status === 'Warning' ? 'warning' : 'danger'"
                size="sm"
                dot
              >
                {{ currentPrediction.status }}
              </Badge>
            </div>
          </div>

          <div class="mt-3 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold text-slate-900 tracking-tight">
              {{ currentPrediction.tds.toFixed(2) }}
            </span>
            <span class="text-sm font-semibold text-slate-500">ppm</span>
          </div>

          <div class="mt-4 flex items-center justify-between text-xs text-slate-500 border-t border-slate-100 pt-3">
            <span>Water Quality Goal: <strong class="text-slate-700 font-semibold">&lt; 100.0 ppm</strong></span>
            <!-- Sparkline SVG -->
            <svg class="w-24 h-8 text-blue-500 stroke-current fill-none stroke-[2.5]" viewBox="0 0 160 36">
              <path :d="buildSparklinePath(tdsHistory)" />
            </svg>
          </div>
        </div>
        <div class="h-1 bg-blue-500 w-full"></div>
      </Card>

      <!-- KPI 3: System Health & Telemetry Metrics -->
      <Card no-padding class="border border-slate-200/90 shadow-sm relative overflow-hidden">
        <div class="p-5">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <Activity class="w-4 h-4 text-emerald-600" />
              Plant Health & Stream Stats
            </span>
            <span class="text-[11px] font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
              Station Alpha-12
            </span>
          </div>

          <div class="mt-3 flex items-center justify-between">
            <div>
              <p class="text-xs text-slate-500 font-medium">Logged Packets</p>
              <p class="text-2xl font-extrabold text-slate-900 tracking-tight mt-0.5">{{ totalPackets }}</p>
            </div>
            <div class="text-right">
              <p class="text-xs text-slate-500 font-medium">Feed Recovery</p>
              <p class="text-2xl font-extrabold text-slate-900 tracking-tight mt-0.5">{{ liveFeed.Recovery_percent }}%</p>
            </div>
          </div>

          <div class="mt-4 flex items-center justify-between text-xs text-slate-500 border-t border-slate-100 pt-3">
            <span class="flex items-center gap-1">
              <CheckCircle2 class="w-3.5 h-3.5 text-emerald-500" />
              <span>Backend Connected</span>
            </span>
            <span class="font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              WebSocket Active
            </span>
          </div>
        </div>
        <div class="h-1 bg-emerald-500 w-full"></div>
      </Card>
    </div>

    <!-- Live Telemetry 7-Sensor Matrix Grid -->
    <Card no-padding class="border border-slate-200 shadow-sm">
      <template #header>
        <div class="flex items-center justify-between w-full">
          <div class="flex items-center gap-2">
            <Radio class="w-4 h-4 text-cyan-600 animate-pulse" />
            <h2 class="text-xs font-bold uppercase tracking-wider text-slate-700">
              Real-Time Feed Telemetry Sensor Matrix (7 Ingest Nodes)
            </h2>
          </div>
          <span class="text-xs font-semibold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md border border-slate-200">
            Node ID: {{ liveFeed.operator_id }}
          </span>
        </div>
      </template>

      <div class="p-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          <!-- Sensor 1: Feed Flowrate -->
          <div class="bg-slate-50/80 p-4 rounded-xl border border-slate-200/80 hover:border-slate-300 transition-all">
            <div class="flex items-center justify-between text-xs font-bold text-slate-500 mb-1">
              <span>Feed Flowrate</span>
              <Gauge class="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div class="text-xl font-extrabold text-slate-900 mt-1">
              {{ liveFeed.Feed_Flowrate_m3h }} <span class="text-xs font-semibold text-slate-500">m³/h</span>
            </div>
            <div class="mt-3 w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div class="bg-cyan-500 h-1.5 rounded-full transition-all duration-300" :style="{ width: `${Math.min(100, (liveFeed.Feed_Flowrate_m3h / 120) * 100)}%` }"></div>
            </div>
            <p class="text-[10px] text-slate-400 mt-1.5 font-medium">Target: 70 - 80 m³/h</p>
          </div>

          <!-- Sensor 2: Feed TDS -->
          <div class="bg-slate-50/80 p-4 rounded-xl border border-slate-200/80 hover:border-slate-300 transition-all">
            <div class="flex items-center justify-between text-xs font-bold text-slate-500 mb-1">
              <span>Feed TDS</span>
              <Droplets class="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div class="text-xl font-extrabold text-slate-900 mt-1">
              {{ liveFeed.Feed_TDS_ppm }} <span class="text-xs font-semibold text-slate-500">ppm</span>
            </div>
            <div class="mt-3 w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div class="bg-blue-500 h-1.5 rounded-full transition-all duration-300" :style="{ width: `${Math.min(100, (liveFeed.Feed_TDS_ppm / 1200) * 100)}%` }"></div>
            </div>
            <p class="text-[10px] text-slate-400 mt-1.5 font-medium">Target: 750 - 850</p>
          </div>

          <!-- Sensor 3: Feed Salinity -->
          <div class="bg-slate-50/80 p-4 rounded-xl border border-slate-200/80 hover:border-slate-300 transition-all">
            <div class="flex items-center justify-between text-xs font-bold text-slate-500 mb-1">
              <span>Salinity</span>
              <Activity class="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div class="text-xl font-extrabold text-slate-900 mt-1">
              {{ liveFeed.Feed_Salinity_gL }} <span class="text-xs font-semibold text-slate-500">g/L</span>
            </div>
            <div class="mt-3 w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div class="bg-indigo-500 h-1.5 rounded-full transition-all duration-300" :style="{ width: `${Math.min(100, (liveFeed.Feed_Salinity_gL / 40) * 100)}%` }"></div>
            </div>
            <p class="text-[10px] text-slate-400 mt-1.5 font-medium">Target: 23 - 27 g/L</p>
          </div>

          <!-- Sensor 4: Feed Temperature -->
          <div class="bg-slate-50/80 p-4 rounded-xl border border-slate-200/80 hover:border-slate-300 transition-all">
            <div class="flex items-center justify-between text-xs font-bold text-slate-500 mb-1">
              <span>Temperature</span>
              <Thermometer class="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div class="text-xl font-extrabold text-slate-900 mt-1">
              {{ liveFeed.Feed_Temperature_C }} <span class="text-xs font-semibold text-slate-500">°C</span>
            </div>
            <div class="mt-3 w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div class="bg-amber-500 h-1.5 rounded-full transition-all duration-300" :style="{ width: `${Math.min(100, (liveFeed.Feed_Temperature_C / 40) * 100)}%` }"></div>
            </div>
            <p class="text-[10px] text-slate-400 mt-1.5 font-medium">Target: 24 - 28 °C</p>
          </div>

          <!-- Sensor 5: Recovery Rate -->
          <div class="bg-slate-50/80 p-4 rounded-xl border border-slate-200/80 hover:border-slate-300 transition-all">
            <div class="flex items-center justify-between text-xs font-bold text-slate-500 mb-1">
              <span>Recovery</span>
              <Zap class="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div class="text-xl font-extrabold text-slate-900 mt-1">
              {{ liveFeed.Recovery_percent }} <span class="text-xs font-semibold text-slate-500">%</span>
            </div>
            <div class="mt-3 w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div class="bg-emerald-500 h-1.5 rounded-full transition-all duration-300" :style="{ width: `${Math.min(100, liveFeed.Recovery_percent)}%` }"></div>
            </div>
            <p class="text-[10px] text-slate-400 mt-1.5 font-medium">Target: 70 - 80 %</p>
          </div>

          <!-- Sensor 6: Membrane Flux -->
          <div class="bg-slate-50/80 p-4 rounded-xl border border-slate-200/80 hover:border-slate-300 transition-all">
            <div class="flex items-center justify-between text-xs font-bold text-slate-500 mb-1">
              <span>Flux</span>
              <Activity class="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div class="text-xl font-extrabold text-slate-900 mt-1">
              {{ liveFeed.Flux_LMH }} <span class="text-xs font-semibold text-slate-500">LMH</span>
            </div>
            <div class="mt-3 w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div class="bg-purple-500 h-1.5 rounded-full transition-all duration-300" :style="{ width: `${Math.min(100, (liveFeed.Flux_LMH / 30) * 100)}%` }"></div>
            </div>
            <p class="text-[10px] text-slate-400 mt-1.5 font-medium">Target: 18 - 22 LMH</p>
          </div>

          <!-- Sensor 7: Pressure Drop -->
          <div class="bg-slate-50/80 p-4 rounded-xl border border-slate-200/80 hover:border-slate-300 transition-all">
            <div class="flex items-center justify-between text-xs font-bold text-slate-500 mb-1">
              <span>Pressure Drop</span>
              <Gauge class="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div class="text-xl font-extrabold text-slate-900 mt-1">
              {{ liveFeed.Pressure_Drop_bar }} <span class="text-xs font-semibold text-slate-500">bar</span>
            </div>
            <div class="mt-3 w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div class="bg-rose-500 h-1.5 rounded-full transition-all duration-300" :style="{ width: `${Math.min(100, (liveFeed.Pressure_Drop_bar / 1.5) * 100)}%` }"></div>
            </div>
            <p class="text-[10px] text-slate-400 mt-1.5 font-medium">Target: 0.4 - 0.6 bar</p>
          </div>
        </div>
      </div>
    </Card>

    <!-- Bottom Telemetry Stream History Table -->
    <Card no-padding class="border border-slate-200 shadow-sm">
      <template #header>
        <div class="flex items-center justify-between w-full">
          <div class="flex items-center gap-2">
            <Database class="w-4 h-4 text-slate-600" />
            <h2 class="text-xs font-bold uppercase tracking-wider text-slate-700">
              Live Telemetry Stream Log (Database Persisted)
            </h2>
          </div>
          <span class="text-xs text-slate-500 font-medium">
            Total Logged: {{ telemetryLog.length }} records
          </span>
        </div>
      </template>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-100/80 text-[11px] font-bold uppercase tracking-wider text-slate-600 border-b border-slate-200">
              <th class="py-3 px-4"># ID</th>
              <th class="py-3 px-4">Timestamp</th>
              <th class="py-3 px-4">Node / Op</th>
              <th class="py-3 px-4">Feed Flow (m³/h)</th>
              <th class="py-3 px-4">Feed TDS (ppm)</th>
              <th class="py-3 px-4">Temp (°C)</th>
              <th class="py-3 px-4">Recovery %</th>
              <th class="py-3 px-4">Pred. Permeate Flow</th>
              <th class="py-3 px-4">Pred. Permeate TDS</th>
              <th class="py-3 px-4 text-right">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200/70 text-xs">
            <tr 
              v-for="entry in telemetryLog.slice().reverse().slice(0, 15)" 
              :key="entry.id"
              class="hover:bg-slate-50/80 transition-colors"
            >
              <td class="py-3 px-4 font-mono font-bold text-slate-700">#{{ entry.id }}</td>
              <td class="py-3 px-4 text-slate-600 font-mono text-[11px] whitespace-nowrap">
                {{ entry.timestamp ? entry.timestamp.split('T')[0] + ' ' + (entry.timestamp.split('T')[1] || '').substring(0, 8) : 'Just now' }}
              </td>
              <td class="py-3 px-4 text-slate-700 font-semibold">{{ entry.operator_id }}</td>
              <td class="py-3 px-4 text-slate-800 font-mono">{{ entry.feed_flowrate }}</td>
              <td class="py-3 px-4 text-slate-800 font-mono">{{ entry.feed_tds }}</td>
              <td class="py-3 px-4 text-slate-800 font-mono">{{ entry.temperature }}°C</td>
              <td class="py-3 px-4 text-slate-800 font-mono">{{ entry.recovery }}%</td>
              <td class="py-3 px-4 text-cyan-700 font-bold font-mono">
                {{ entry.permeate_flowrate !== undefined ? entry.permeate_flowrate + ' m³/h' : '-' }}
              </td>
              <td class="py-3 px-4 text-blue-700 font-bold font-mono">
                {{ entry.permeate_tds !== undefined ? entry.permeate_tds + ' ppm' : '-' }}
              </td>
              <td class="py-3 px-4 text-right">
                <Badge 
                  :variant="entry.status === 'Excellent' || entry.status === 'Good' ? 'success' : entry.status === 'Warning' ? 'warning' : 'danger'"
                  size="sm"
                >
                  {{ entry.status || 'Good' }}
                </Badge>
              </td>
            </tr>

            <tr v-if="telemetryLog.length === 0">
              <td colspan="10" class="py-8 text-center text-slate-400 text-xs italic">
                No telemetry stream data logged yet. Click "Simulate Tick" to generate telemetry predictions.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
  </div>
</template>

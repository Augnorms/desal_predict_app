<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Play, RotateCcw, ChevronRight, RefreshCw } from 'lucide-vue-next'
import Card from '../components/ui/Card.vue'
import Button from '../components/ui/Button.vue'
import InputField from '../components/ui/InputField.vue'
import Badge from '../components/ui/Badge.vue'
import Alert from '../components/ui/Alert.vue'
import Modal from '../components/ui/Modal.vue'
import type { DbEntry, PredictionInput } from '../types'
import { predictAndSave, getEntries } from '../api/prediction'

const isSubmitting = ref(false)
const errorMessage = ref('')
const successPrediction = ref<any>(null)
const recentEntries = ref<DbEntry[]>([])
const isModalOpen = ref(false)
const selectedEntry = ref<DbEntry | null>(null)

// Form state
const form = reactive({
  operator_id: 'OP-001',
  Feed_Flowrate_m3h: 75.0,
  Feed_TDS_ppm: 800.0,
  Feed_Salinity_gL: 25.0,
  Feed_Temperature_C: 26.0,
  Recovery_percent: 75.0,
  Flux_LMH: 20.0,
  Pressure_Drop_bar: 0.5,
  Permeate_Flowrate_m3h: '',
  Permeate_TDS_ppm: ''
})

// Calculate form completeness percentage
const completeness = computed(() => {
  const fields = [
    form.Feed_Flowrate_m3h,
    form.Feed_TDS_ppm,
    form.Feed_Salinity_gL,
    form.Feed_Temperature_C,
    form.Recovery_percent,
    form.Flux_LMH,
    form.Pressure_Drop_bar
  ]
  const filled = fields.filter(v => v !== null && v !== undefined && String(v).trim() !== '' && !isNaN(Number(v))).length
  return Math.round((filled / fields.length) * 100)
})

const fetchHistory = async () => {
  try {
    const list = await getEntries()
    recentEntries.value = list.reverse() // latest first
  } catch (e) {
    console.error('Error loading history:', e)
  }
}

const loadLatestIntoForm = () => {
  if (recentEntries.value.length > 0) {
    const latest = recentEntries.value[0]
    form.operator_id = latest.operator_id || 'OP-001'
    form.Feed_Flowrate_m3h = latest.feed_flowrate
    form.Feed_TDS_ppm = latest.feed_tds
    form.Feed_Salinity_gL = latest.feed_salinity
    form.Feed_Temperature_C = latest.temperature
    form.Recovery_percent = latest.recovery
    form.Flux_LMH = latest.flux
    form.Pressure_Drop_bar = latest.pressure_drop
    if (latest.permeate_flowrate !== undefined) form.Permeate_Flowrate_m3h = String(latest.permeate_flowrate)
    if (latest.permeate_tds !== undefined) form.Permeate_TDS_ppm = String(latest.permeate_tds)
  }
}

const clearForm = () => {
  form.Feed_Flowrate_m3h = 0
  form.Feed_TDS_ppm = 0
  form.Feed_Salinity_gL = 0
  form.Feed_Temperature_C = 25.0
  form.Recovery_percent = 0
  form.Flux_LMH = 0
  form.Pressure_Drop_bar = 0
  form.Permeate_Flowrate_m3h = ''
  form.Permeate_TDS_ppm = ''
  errorMessage.value = ''
  successPrediction.value = null
}

const handlePrediction = async () => {
  errorMessage.value = ''
  successPrediction.value = null
  isSubmitting.value = true

  const payload: PredictionInput = {
    operator_id: form.operator_id || 'OP-001',
    Feed_Flowrate_m3h: Number(form.Feed_Flowrate_m3h),
    Feed_TDS_ppm: Number(form.Feed_TDS_ppm),
    Feed_Salinity_gL: Number(form.Feed_Salinity_gL),
    Feed_Temperature_C: Number(form.Feed_Temperature_C),
    Recovery_percent: Number(form.Recovery_percent),
    Flux_LMH: Number(form.Flux_LMH),
    Pressure_Drop_bar: Number(form.Pressure_Drop_bar)
  }

  try {
    const res = await predictAndSave(payload)
    successPrediction.value = res.prediction
    form.Permeate_Flowrate_m3h = String(res.prediction.flowrate)
    form.Permeate_TDS_ppm = String(res.prediction.tds)
    await fetchHistory()
  } catch (err: any) {
    errorMessage.value = err?.response?.data?.detail || err.message || 'Failed to submit prediction request.'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchHistory()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header Title -->
    <div>
      <h1 class="text-xl font-bold text-slate-900 tracking-tight">Manual Data Entry Mode</h1>
      <p class="text-xs text-slate-500 mt-0.5">
        Input system parameters manually to generate model predictions. This mode overrides the live IoT feed.
      </p>
    </div>

    <!-- Main Grid Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
      <!-- Left Column: Form & Validation (2 Cols) -->
      <div class="lg:col-span-2 space-y-5">
        <Card no-padding class="border border-slate-200 shadow-sm">
          <template #header>
            <div class="flex items-center justify-between w-full">
              <span class="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-slate-400"></span>
                Input Parameters
              </span>
              <span class="px-2.5 py-0.5 rounded bg-amber-100/90 text-amber-800 text-[10px] font-bold uppercase tracking-wider border border-amber-300">
                Override Enabled
              </span>
            </div>
          </template>

          <div class="p-6 space-y-6">
            <!-- Global error banner -->
            <Alert v-if="errorMessage" variant="error" title="Prediction Failed">
              {{ errorMessage }}
            </Alert>

            <!-- Success banner -->
            <Alert v-if="successPrediction" variant="success" title="Prediction Generated & Saved!">
              Predicted Flowrate: <strong>{{ successPrediction.flowrate }} m³/h</strong> | 
              Predicted TDS: <strong>{{ successPrediction.tds }} ppm</strong> | 
              Status: <strong>{{ successPrediction.status }}</strong>
            </Alert>

            <!-- Inputs Grid (3 columns) -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <InputField 
                v-model="form.Feed_Flowrate_m3h" 
                label="Feed Flowrate" 
                unit="m3/h" 
                type="number" 
                step="0.1" 
                placeholder="0.00" 
              />
              <InputField 
                v-model="form.Feed_TDS_ppm" 
                label="Feed TDS" 
                unit="ppm" 
                type="number" 
                step="1" 
                placeholder="0" 
              />
              <InputField 
                v-model="form.Feed_Salinity_gL" 
                label="Feed Salinity" 
                unit="g/L" 
                type="number" 
                step="0.1" 
                placeholder="0.0" 
              />

              <InputField 
                v-model="form.Feed_Temperature_C" 
                label="Feed Temp" 
                unit="°C" 
                type="number" 
                step="0.1" 
                placeholder="25.0" 
              />
              <InputField 
                v-model="form.Permeate_Flowrate_m3h" 
                label="Permeate Flowrate" 
                unit="m3/h" 
                type="text" 
                placeholder="Calculated..." 
                disabled 
              />
              <InputField 
                v-model="form.Permeate_TDS_ppm" 
                label="Permeate TDS" 
                unit="ppm" 
                type="text" 
                placeholder="Calculated..." 
                disabled 
              />

              <InputField 
                v-model="form.Recovery_percent" 
                label="Recovery" 
                unit="%" 
                type="number" 
                step="0.1" 
                placeholder="0.0" 
              />
              <InputField 
                v-model="form.Flux_LMH" 
                label="Flux" 
                unit="LMH" 
                type="number" 
                step="0.1" 
                placeholder="0.0" 
              />
              <InputField 
                v-model="form.Pressure_Drop_bar" 
                label="Pressure Drop" 
                unit="bar" 
                type="number" 
                step="0.01" 
                placeholder="0.00" 
              />
            </div>

            <!-- Form Action Buttons -->
            <div class="flex flex-wrap items-center justify-end gap-3 pt-2 border-t border-slate-100">
              <Button variant="outline" size="md" @click="loadLatestIntoForm" title="Load latest active parameters from backend DB">
                <template #icon><RefreshCw class="w-4 h-4 text-slate-500" /></template>
                Load Active Data
              </Button>
              <Button variant="outline" size="md" @click="clearForm">
                <template #icon><RotateCcw class="w-4 h-4 text-slate-500" /></template>
                Clear Form
              </Button>
              <Button 
                variant="primary" 
                size="md" 
                :loading="isSubmitting"
                class="font-bold px-6 shadow-md"
                @click="handlePrediction"
              >
                <template #icon><Play class="w-4 h-4 fill-white" /></template>
                Run Prediction
              </Button>
            </div>
          </div>
        </Card>

        <!-- Input Validation Logic Banner -->
        <Alert variant="info" title="Input Validation Logic">
          Numerical values must be within operational limits (e.g., Temperature 5–45°C). Invalid entries will be flagged in red and excluded from prediction modeling.
        </Alert>
      </div>

      <!-- Right Column: Status, Recent Entries, Reference Asset (1 Col) -->
      <div class="space-y-5">
        <!-- Card 1: Validation Status -->
        <Card no-padding class="border border-slate-200">
          <template #header>
            <span class="text-xs font-bold uppercase tracking-wider text-slate-500">Validation Status</span>
          </template>
          <div class="p-4 space-y-3.5">
            <div class="flex items-center justify-between text-xs py-1.5 border-b border-slate-100">
              <span class="text-slate-600 font-medium">Data Completeness</span>
              <span class="font-bold text-rose-600 font-mono text-sm">{{ completeness }}%</span>
            </div>
            <div class="flex items-center justify-between text-xs py-1.5 border-b border-slate-100">
              <span class="text-slate-600 font-medium">Range Compliance</span>
              <span class="font-bold text-emerald-600 flex items-center gap-1">
                Passed
              </span>
            </div>
            <div class="flex items-center justify-between text-xs py-1.5">
              <span class="text-slate-600 font-medium">Model Ready</span>
              <span class="font-mono text-slate-500 italic">
                {{ completeness === 100 ? 'Ready' : 'Waiting...' }}
              </span>
            </div>
          </div>
        </Card>

        <!-- Card 2: Recent Manual Entries -->
        <Card no-padding class="border border-slate-200">
          <template #header>
            <span class="text-xs font-bold uppercase tracking-wider text-slate-500">Recent Manual Entries</span>
          </template>
          
          <div class="p-4 divide-y divide-slate-100 max-h-56 overflow-y-auto space-y-1">
            <div 
              v-for="entry in recentEntries.slice(0, 3)" 
              :key="entry.id"
              class="py-2.5 first:pt-0 hover:bg-slate-50 rounded px-1 cursor-pointer transition-colors"
              @click="selectedEntry = entry; isModalOpen = true"
            >
              <div class="flex items-center justify-between text-xs">
                <span class="font-bold text-slate-900">Override ID: #{{ entry.id }}</span>
                <span class="text-[11px] text-slate-400">{{ new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}</span>
              </div>
              <p class="text-[11px] text-slate-500 font-mono mt-1">
                Flow: {{ entry.feed_flowrate }}m3/h | TDS: {{ entry.feed_tds }}ppm | Rec: {{ entry.recovery }}%
              </p>
            </div>

            <div v-if="recentEntries.length === 0" class="py-4 text-center text-xs text-slate-400">
              No entries logged yet.
            </div>
          </div>

          <template #footer>
            <button 
              type="button" 
              class="w-full text-center text-xs font-bold text-slate-700 hover:text-slate-900 flex items-center justify-center gap-1 py-1"
              @click="isModalOpen = true"
            >
              View Entry Log <ChevronRight class="w-3.5 h-3.5" />
            </button>
          </template>
        </Card>

        <!-- Card 3: Reference Asset -->
        <Card no-padding class="overflow-hidden border border-slate-200">
          <div class="relative h-40 bg-slate-900">
            <img 
              src="/assets/membrane_bank.jpg" 
              alt="Membrane Bank B-1" 
              class="w-full h-full object-cover opacity-80" 
            />
            <div class="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-slate-950/30 to-transparent flex flex-col justify-end p-4">
              <span class="text-[10px] uppercase font-bold text-slate-300 tracking-wider">Reference Asset</span>
              <h4 class="text-sm font-bold text-white tracking-tight">Membrane Bank B-1</h4>
            </div>
          </div>
        </Card>
      </div>
    </div>

    <!-- Entry Log History Modal -->
    <Modal :is-open="isModalOpen" title="Historical Manual Entry Log" size="xl" @close="isModalOpen = false">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="bg-slate-100 text-slate-600 font-bold uppercase tracking-wider text-[11px]">
              <th class="py-2.5 px-3">ID</th>
              <th class="py-2.5 px-3">Operator</th>
              <th class="py-2.5 px-3">Feed Flow</th>
              <th class="py-2.5 px-3">Feed TDS</th>
              <th class="py-2.5 px-3">Temp</th>
              <th class="py-2.5 px-3">Perm. Flow</th>
              <th class="py-2.5 px-3">Perm. TDS</th>
              <th class="py-2.5 px-3">Status</th>
              <th class="py-2.5 px-3">Timestamp</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 font-mono">
            <tr v-for="item in recentEntries" :key="item.id" class="hover:bg-slate-50">
              <td class="py-2.5 px-3 font-bold text-slate-900">#{{ item.id }}</td>
              <td class="py-2.5 px-3 font-sans text-slate-700">{{ item.operator_id }}</td>
              <td class="py-2.5 px-3 text-slate-800">{{ item.feed_flowrate }} m³/h</td>
              <td class="py-2.5 px-3 text-slate-800">{{ item.feed_tds }} ppm</td>
              <td class="py-2.5 px-3 text-slate-800">{{ item.temperature }} °C</td>
              <td class="py-2.5 px-3 text-emerald-700 font-bold">{{ item.permeate_flowrate ?? '-' }}</td>
              <td class="py-2.5 px-3 text-emerald-700 font-bold">{{ item.permeate_tds ?? '-' }}</td>
              <td class="py-2.5 px-3">
                <Badge v-if="item.status" :variant="item.status === 'Excellent' || item.status === 'Good' ? 'success' : 'warning'" size="sm">
                  {{ item.status }}
                </Badge>
                <span v-else class="text-slate-400">-</span>
              </td>
              <td class="py-2.5 px-3 text-slate-400 font-sans text-[11px]">{{ item.timestamp }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #footer>
        <Button variant="outline" size="sm" @click="isModalOpen = false">Close</Button>
      </template>
    </Modal>
  </div>
</template>

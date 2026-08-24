<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Bell, Settings, HelpCircle, Activity, CheckCircle2 } from 'lucide-vue-next'

const route = useRoute()

const isIotActive = computed(() => route.path === '/iot-predictive-center')
const isManualActive = computed(() => route.path === '/prediction-center')
const isNoneSelected = computed(() => !isIotActive.value && !isManualActive.value)
</script>

<template>
  <header class="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between shrink-0 select-none">
    <!-- Left: Page Title & System Status -->
    <div class="flex items-center gap-6">
      <h2 class="text-sm font-bold text-[#0b2246] tracking-tight flex items-center gap-2">
        Critical Infrastructure Monitor
      </h2>

      <!-- System Status Pills -->
      <div class="flex items-center gap-3 text-xs font-medium text-slate-600">
        <!-- IoT Active Pill -->
        <span 
          class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-[11px] transition-all duration-200"
          :class="isIotActive 
            ? 'bg-emerald-50 border-emerald-200 text-emerald-800 font-semibold' 
            : isManualActive 
              ? 'bg-slate-100/60 border-slate-200 text-slate-400 opacity-60' 
              : 'bg-slate-100 border-slate-200 text-slate-700'"
        >
          <span class="relative flex h-2 w-2">
            <span v-if="isIotActive" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2" :class="isIotActive || isNoneSelected ? 'bg-emerald-500' : 'bg-slate-300'"></span>
          </span>
          <Activity class="w-3 h-3" :class="isIotActive || isNoneSelected ? 'text-emerald-600' : 'text-slate-400'" />
          IoT Active
        </span>

        <!-- Manual Active Pill -->
        <span 
          class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-[11px] transition-all duration-200"
          :class="isManualActive 
            ? 'bg-emerald-50 border-emerald-200 text-emerald-800 font-semibold' 
            : isIotActive 
              ? 'bg-slate-100/60 border-slate-200 text-slate-400 opacity-60' 
              : 'bg-slate-100 border-slate-200 text-slate-700'"
        >
          <span class="relative flex h-2 w-2">
            <span v-if="isManualActive" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2" :class="isManualActive || isNoneSelected ? 'bg-emerald-500' : 'bg-slate-300'"></span>
          </span>
          <CheckCircle2 class="w-3.5 h-3.5" :class="isManualActive || isNoneSelected ? 'text-emerald-600' : 'text-slate-400'" />
          Manual Active
        </span>
      </div>
    </div>

    <!-- Right: Search & Tool Icons -->
    <div class="flex items-center gap-3">
      <!-- Search Input -->
      <!--<div class="relative w-64">
        <Search class="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Search systems..." 
          class="w-full pl-8 pr-3 py-1.5 text-xs bg-slate-100/80 border border-slate-200 rounded-lg text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-slate-400 focus:bg-white transition-all"
        />
      </div>-->

      <!-- Quick Action Icons -->
      <div class="flex items-center gap-1 border-l border-slate-200 pl-3">
        <button type="button" class="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors" title="Notifications">
          <Bell class="w-4 h-4" />
        </button>
        <button type="button" class="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors" title="Settings">
          <Settings class="w-4 h-4" />
        </button>
        <button type="button" class="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors" title="Help">
          <HelpCircle class="w-4 h-4" />
        </button>
      </div>
    </div>
  </header>
</template>

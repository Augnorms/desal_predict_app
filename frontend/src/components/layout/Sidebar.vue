<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { LayoutGrid, LineChart, ShieldAlert, UserCheck } from 'lucide-vue-next'
import Button from '../ui/Button.vue'

const route = useRoute()
const router = useRouter()

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutGrid },
  { name: 'Prediction Center', path: '/prediction-center', icon: LineChart },
  { name: 'IOT Predictive Center', path: '/iot-predictive-center', icon: LineChart }
]

const handleSystemOverride = () => {
  router.push('/prediction-center')
}
</script>

<template>
  <aside class="w-64 bg-[#e9ecef]/80 border-r border-slate-300/70 flex flex-col justify-between h-screen shrink-0 select-none">
    <!-- Top Branding & Navigation -->
    <div>
      <!-- App Header -->
      <div class="px-6 py-6 border-b border-slate-300/60">
        <div class="flex items-center gap-2.5">
          <div class="w-7 h-7 rounded-lg bg-[#0b2246] flex items-center justify-center text-white font-bold text-xs tracking-tighter">
            AQ
          </div>
          <div>
            <h1 class="text-base font-bold text-[#0b2246] leading-tight tracking-tight">AquaGuard OS</h1>
            <p class="text-[11px] text-slate-500 font-medium tracking-wide">Station Alpha-12</p>
          </div>
        </div>
      </div>

      <!-- Nav Links -->
      <nav class="p-3 space-y-1.5 mt-2">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold transition-all duration-150"
          :class="[
            route.path === item.path
              ? 'bg-white text-[#0b2246] shadow-xs border border-slate-200/80 border-l-4 border-l-[#0b2246]'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
          ]"
        >
          <component :is="item.icon" class="w-4 h-4 shrink-0" :class="route.path === item.path ? 'text-[#0b2246]' : 'text-slate-500'" />
          <span>{{ item.name }}</span>
        </router-link>
      </nav>
    </div>

    <!-- Bottom Actions & User Profile -->
    <div class="p-4 border-t border-slate-300/60 space-y-4">
      <!-- System Override Action -->
      <Button 
        variant="primary" 
        class="w-full justify-center text-xs py-2.5 font-bold shadow-md tracking-wide"
        @click="handleSystemOverride"
      >
        <template #icon>
          <ShieldAlert class="w-4 h-4 text-cyan-300" />
        </template>
        System Override
      </Button>

      <!-- Operator Profile -->
      <div class="flex items-center gap-3 px-1 pt-1">
        <div class="w-8 h-8 rounded-full bg-slate-300/80 border border-slate-400/50 flex items-center justify-center text-slate-700 font-semibold text-xs overflow-hidden">
          <UserCheck class="w-4 h-4 text-slate-700" />
        </div>
        <div class="min-w-0">
          <p class="text-xs font-bold text-slate-800 truncate">Operator 12-A</p>
          <p class="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Shift Supervisor</p>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Info, CheckCircle2, AlertTriangle, XCircle, X } from 'lucide-vue-next'

interface Props {
  variant?: 'info' | 'success' | 'warning' | 'error'
  title?: string
  dismissible?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'info',
  dismissible: false
})

const emit = defineEmits(['close'])

const containerClasses = computed(() => {
  const base = 'rounded-lg p-4 border text-xs leading-relaxed flex items-start gap-3 transition-all'
  const variants = {
    info: 'bg-sky-50/80 border-sky-200 text-sky-900',
    success: 'bg-emerald-50/80 border-emerald-200 text-emerald-900',
    warning: 'bg-amber-50/80 border-amber-200 text-amber-900',
    error: 'bg-rose-50/80 border-rose-200 text-rose-900'
  }
  return [base, variants[props.variant]].join(' ')
})

const iconComponent = computed(() => {
  switch (props.variant) {
    case 'success': return CheckCircle2
    case 'warning': return AlertTriangle
    case 'error': return XCircle
    default: return Info
  }
})

const iconColor = computed(() => {
  switch (props.variant) {
    case 'success': return 'text-emerald-600'
    case 'warning': return 'text-amber-600'
    case 'error': return 'text-rose-600'
    default: return 'text-sky-600'
  }
})
</script>

<template>
  <div :class="containerClasses" role="alert">
    <component :is="iconComponent" :class="['w-4 h-4 shrink-0 mt-0.5', iconColor]" />
    <div class="flex-1 min-w-0">
      <h4 v-if="title" class="font-semibold mb-0.5 text-slate-900">{{ title }}</h4>
      <div class="text-slate-700">
        <slot></slot>
      </div>
    </div>
    <button 
      v-if="dismissible" 
      type="button" 
      class="text-slate-400 hover:text-slate-600 p-0.5 rounded focus:outline-none"
      @click="emit('close')"
    >
      <X class="w-3.5 h-3.5" />
    </button>
  </div>
</template>

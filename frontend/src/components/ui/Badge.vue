<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'normal' | 'success' | 'caution' | 'warning' | 'danger' | 'info' | 'neutral'
  size?: 'sm' | 'md'
  dot?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'normal',
  size: 'md',
  dot: false
})

const badgeClasses = computed(() => {
  const base = 'inline-flex items-center font-semibold rounded-md uppercase tracking-wider transition-colors'
  
  const variants = {
    normal: 'bg-emerald-100/80 text-emerald-800 border border-emerald-300/50',
    success: 'bg-emerald-100/80 text-emerald-800 border border-emerald-300/50',
    caution: 'bg-amber-100/80 text-amber-800 border border-amber-300/50',
    warning: 'bg-amber-100/80 text-amber-800 border border-amber-300/50',
    danger: 'bg-rose-100/80 text-rose-800 border border-rose-300/50',
    info: 'bg-sky-100/80 text-sky-800 border border-sky-300/50',
    neutral: 'bg-slate-100 text-slate-700 border border-slate-200'
  }

  const sizes = {
    sm: 'px-2 py-0.5 text-[10px] gap-1',
    md: 'px-2.5 py-1 text-xs gap-1.5'
  }

  return [base, variants[props.variant], sizes[props.size]].join(' ')
})

const dotColor = computed(() => {
  const colors = {
    normal: 'bg-emerald-500',
    success: 'bg-emerald-500',
    caution: 'bg-amber-500',
    warning: 'bg-amber-500',
    danger: 'bg-rose-500',
    info: 'bg-sky-500',
    neutral: 'bg-slate-400'
  }
  return colors[props.variant]
})
</script>

<template>
  <span :class="badgeClasses">
    <span v-if="dot" :class="['w-1.5 h-1.5 rounded-full animate-pulse', dotColor]"></span>
    <slot></slot>
  </span>
</template>

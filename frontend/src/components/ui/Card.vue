<script setup lang="ts">
interface Props {
  title?: string
  subtitle?: string
  noPadding?: boolean
  borderless?: boolean
}

defineProps<Props>()
</script>

<template>
  <div 
    class="bg-white rounded-xl transition-all duration-200"
    :class="[
      borderless ? '' : 'border border-slate-200/90 shadow-sm hover:shadow',
    ]"
  >
    <div 
      v-if="title || $slots.header || $slots.action" 
      class="px-5 py-4 border-b border-slate-100 flex items-center justify-between gap-3"
    >
      <div>
        <h3 v-if="title" class="text-sm font-semibold text-slate-900 tracking-tight uppercase tracking-wider text-xs text-slate-500">
          {{ title }}
        </h3>
        <p v-if="subtitle" class="text-xs text-slate-500 mt-0.5">{{ subtitle }}</p>
        <slot name="header"></slot>
      </div>
      <div v-if="$slots.action" class="flex items-center gap-2">
        <slot name="action"></slot>
      </div>
    </div>

    <div :class="noPadding ? '' : 'p-5'">
      <slot></slot>
    </div>

    <div v-if="$slots.footer" class="px-5 py-3 bg-slate-50/50 border-t border-slate-100 rounded-b-xl">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

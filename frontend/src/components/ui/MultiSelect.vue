<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ChevronDown, X, Check } from 'lucide-vue-next'
import type { SelectOption } from '../../types'

interface Props {
  modelValue: (string | number)[]
  options: SelectOption[]
  label?: string
  placeholder?: string
  disabled?: boolean
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
  placeholder: 'Select items...',
  disabled: false
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const selectedOptions = computed(() => {
  return props.options.filter(opt => props.modelValue.includes(opt.value))
})

const toggleDropdown = () => {
  if (!props.disabled) {
    isOpen.value = !isOpen.value
  }
}

const toggleOption = (opt: SelectOption) => {
  const current = [...props.modelValue]
  const index = current.indexOf(opt.value)
  if (index > -1) {
    current.splice(index, 1)
  } else {
    current.push(opt.value)
  }
  emit('update:modelValue', current)
}

const removeItem = (val: string | number, event: Event) => {
  event.stopPropagation()
  const current = props.modelValue.filter(v => v !== val)
  emit('update:modelValue', current)
}

const handleClickOutside = (e: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div ref="dropdownRef" class="flex flex-col gap-1.5 w-full relative">
    <label v-if="label" class="text-xs font-medium text-slate-700">
      {{ label }}
    </label>

    <div
      :class="[
        'w-full min-h-[38px] px-2.5 py-1.5 bg-white border rounded-md flex items-center justify-between gap-2 flex-wrap transition-all cursor-pointer',
        'focus:outline-none focus:ring-2 focus:ring-slate-900/10 focus:border-slate-800',
        error ? 'border-rose-300 ring-1 ring-rose-300' : 'border-slate-300 shadow-xs hover:border-slate-400',
        disabled ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : ''
      ]"
      @click="toggleDropdown"
    >
      <div class="flex flex-wrap gap-1 items-center flex-1">
        <span 
          v-for="opt in selectedOptions" 
          :key="opt.value"
          class="inline-flex items-center gap-1 bg-slate-100 text-slate-800 border border-slate-200 text-xs px-2 py-0.5 rounded font-medium"
        >
          {{ opt.label }}
          <button 
            type="button" 
            class="text-slate-400 hover:text-slate-700 focus:outline-none"
            @click="removeItem(opt.value, $event)"
          >
            <X class="w-3 h-3" />
          </button>
        </span>

        <span v-if="selectedOptions.length === 0" class="text-slate-400 text-sm px-1">
          {{ placeholder }}
        </span>
      </div>

      <ChevronDown class="w-4 h-4 text-slate-400 shrink-0 transition-transform" :class="{ 'rotate-180': isOpen }" />
    </div>

    <Transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <div 
        v-if="isOpen"
        class="absolute top-full left-0 right-0 mt-1 z-50 bg-white border border-slate-200 rounded-lg shadow-lg max-h-56 overflow-y-auto py-1 text-sm"
      >
        <div
          v-for="opt in options"
          :key="opt.value"
          class="px-3 py-2 hover:bg-slate-50 cursor-pointer flex items-center justify-between text-slate-700"
          :class="{ 'bg-slate-50 font-semibold text-slate-900': modelValue.includes(opt.value) }"
          @click="toggleOption(opt)"
        >
          <span>{{ opt.label }}</span>
          <Check v-if="modelValue.includes(opt.value)" class="w-4 h-4 text-slate-800" />
        </div>
      </div>
    </Transition>

    <span v-if="error" class="text-[11px] text-rose-600 font-medium">
      {{ error }}
    </span>
  </div>
</template>

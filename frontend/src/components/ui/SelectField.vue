<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ChevronDown, Check } from 'lucide-vue-next'
import type { SelectOption } from '../../types'

interface Props {
  modelValue: string | number
  options: SelectOption[]
  label?: string
  placeholder?: string
  disabled?: boolean
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Select option...',
  disabled: false
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const selectedOption = computed(() => {
  return props.options.find(opt => opt.value === props.modelValue)
})

const toggleDropdown = () => {
  if (!props.disabled) {
    isOpen.value = !isOpen.value
  }
}

const selectOption = (opt: SelectOption) => {
  emit('update:modelValue', opt.value)
  isOpen.value = false
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

    <button
      type="button"
      :disabled="disabled"
      :class="[
        'w-full px-3 py-2 text-sm bg-white border rounded-md flex items-center justify-between transition-all text-left',
        'focus:outline-none focus:ring-2 focus:ring-slate-900/10 focus:border-slate-800',
        error ? 'border-rose-300 ring-1 ring-rose-300' : 'border-slate-300 shadow-xs hover:border-slate-400',
        disabled ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'cursor-pointer'
      ]"
      @click="toggleDropdown"
    >
      <span :class="selectedOption ? 'text-slate-900 font-medium' : 'text-slate-400'">
        {{ selectedOption ? selectedOption.label : placeholder }}
      </span>
      <ChevronDown class="w-4 h-4 text-slate-400 transition-transform" :class="{ 'rotate-180': isOpen }" />
    </button>

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
          class="px-3 py-2 hover:bg-slate-50 cursor-pointer flex items-center justify-between text-slate-700 hover:text-slate-900"
          :class="{ 'bg-slate-50 font-semibold text-slate-900': opt.value === modelValue }"
          @click="selectOption(opt)"
        >
          <span>{{ opt.label }}</span>
          <Check v-if="opt.value === modelValue" class="w-4 h-4 text-slate-800" />
        </div>
      </div>
    </Transition>

    <span v-if="error" class="text-[11px] text-rose-600 font-medium">
      {{ error }}
    </span>
  </div>
</template>

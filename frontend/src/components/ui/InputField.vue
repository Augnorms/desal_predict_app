<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: string | number
  label?: string
  placeholder?: string
  unit?: string
  type?: string
  step?: string | number
  min?: string | number
  max?: string | number
  error?: string
  disabled?: boolean
  required?: boolean
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  disabled: false,
  required: false
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus'])

const inputId = computed(() => props.id || `input-${Math.random().toString(36).substring(2, 9)}`)

const handleInput = (e: Event) => {
  const target = e.target as HTMLInputElement
  const value = props.type === 'number' ? (target.value === '' ? '' : Number(target.value)) : target.value
  emit('update:modelValue', value)
}
</script>

<template>
  <div class="flex flex-col gap-1.5 w-full">
    <label 
      v-if="label" 
      :for="inputId" 
      class="text-xs font-medium text-slate-700 flex items-center justify-between"
    >
      <span>{{ label }} <span v-if="required" class="text-rose-500">*</span></span>
      <span v-if="unit" class="text-[11px] text-slate-400 font-normal">({{ unit }})</span>
    </label>

    <div class="relative flex items-center">
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :step="step"
        :min="min"
        :max="max"
        :disabled="disabled"
        :class="[
          'w-full px-3 py-2 text-sm bg-white border rounded-md font-mono text-slate-900 transition-all duration-150',
          'placeholder:text-slate-400 placeholder:font-sans focus:outline-none focus:ring-2 focus:ring-slate-900/10 focus:border-slate-800',
          error ? 'border-rose-300 ring-1 ring-rose-300 bg-rose-50/20' : 'border-slate-300 shadow-xs hover:border-slate-400',
          disabled ? 'bg-slate-100 text-slate-500 cursor-not-allowed' : ''
        ]"
        @input="handleInput"
        @blur="emit('blur', $event)"
        @focus="emit('focus', $event)"
      />
    </div>

    <span v-if="error" class="text-[11px] text-rose-600 font-medium">
      {{ error }}
    </span>
  </div>
</template>

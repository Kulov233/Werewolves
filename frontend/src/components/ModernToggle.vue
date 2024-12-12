<template>
  <button 
    class="modern-toggle" 
    type="button"
    @click="handleToggle"
    :class="{ active: modelValue }"
    :disabled="disabled"
    :aria-checked="modelValue"
    role="switch"
  >
    <div class="toggle-track">
      <span class="toggle-indicator">
        <svg 
          v-if="modelValue" 
          class="check-icon" 
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="3"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
      </span>
    </div>
    <span class="toggle-label" :class="{ active: modelValue }">
      {{ modelValue ? onText : offText }}
    </span>
  </button>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  onText: {
    type: String,
    default: '监听开启'
  },
  offText: {
    type: String,
    default: '监听关闭'
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const handleToggle = () => {
  if (props.disabled) return
  const newValue = !props.modelValue
  emit('update:modelValue', newValue)
  emit('change', newValue)
}
</script>

<style scoped>
.modern-toggle {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 4px;
  background: transparent !important;
  border: none;
  cursor: pointer;
  user-select: none;
  transition: all 0.3s ease;
  border-radius: 30px;
}

.modern-toggle:hover:not(:disabled) {
  background-color: rgba(0, 0, 0, 0.04);
}

.modern-toggle:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.toggle-track {
  position: relative;
  width: 48px;
  height: 26px;
  background-color: #e4e4e7;
  border-radius: 30px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modern-toggle.active .toggle-track {
  background-color: #22c55e;
}

.toggle-indicator {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 20px;
  height: 20px;
  background-color: white;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modern-toggle.active .toggle-indicator {
  transform: translateX(22px);
  background-color: white;
}

.toggle-label {
  font-size: 14px;
  font-weight: 500;
  color: #71717a;
  transition: color 0.3s ease;
}

.toggle-label.active {
  color: #22c55e;
}

.check-icon {
  width: 12px;
  height: 12px;
  color: #22c55e;
  opacity: 0;
  transform: scale(0.6);
  transition: all 0.2s ease;
}

.modern-toggle.active .check-icon {
  opacity: 1;
  transform: scale(1);
}

/* 按下效果 */
.modern-toggle:active:not(:disabled) .toggle-indicator {
  width: 24px;
  border-radius: 30px;
}

/* 按钮焦点效果 */
.modern-toggle:focus-visible {
  outline: 2px solid #22c55e;
  outline-offset: 2px;
}

/* 悬停效果 */
.modern-toggle:hover:not(:disabled) .toggle-track {
  background-color: #d4d4d8;
}

.modern-toggle.active:hover:not(:disabled) .toggle-track {
  background-color: #16a34a;
}

/* 适配暗色模式 */
@media (prefers-color-scheme: dark) {
  .toggle-track {
    background-color: #3f3f46;
  }
  
  .modern-toggle:hover:not(:disabled) .toggle-track {
    background-color: #52525b;
  }
  
  .toggle-label {
    color: #a1a1aa;
  }
  
  .modern-toggle.active .toggle-label {
    color: #4ade80;
  }
  
  .modern-toggle.active .toggle-track {
    background-color: #16a34a;
  }
  
  .modern-toggle.active:hover:not(:disabled) .toggle-track {
    background-color: #15803d;
  }
}
</style>
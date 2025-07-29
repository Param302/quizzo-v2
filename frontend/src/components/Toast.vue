<template>
    <Teleport to="body">
        <Transition name="toast" appear>
            <div v-if="visible" class="toast-container" :class="[positionClass, variantClass]">
                <div class="toast-content d-flex align-items-center">
                    <i :class="iconClass" class="toast-icon me-2"></i>
                    <span class="flex-grow-1">{{ message }}</span>
                    <button v-if="dismissible" @click="close" class="toast-close btn-close ms-2" type="button"></button>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
    message: {
        type: String,
        required: true
    },
    variant: {
        type: String,
        default: 'success',
        validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
    },
    duration: {
        type: Number,
        default: 4000
    },
    dismissible: {
        type: Boolean,
        default: true
    },
    position: {
        type: String,
        default: 'top-right',
        validator: (value) => ['top-right', 'top-left', 'bottom-right', 'bottom-left', 'top-center'].includes(value)
    }
})

const emit = defineEmits(['close'])

const visible = ref(false)

const iconClass = computed(() => {
    const icons = {
        success: 'bi bi-check-circle-fill text-success',
        error: 'bi bi-exclamation-circle-fill text-danger',
        warning: 'bi bi-exclamation-triangle-fill text-warning',
        info: 'bi bi-info-circle-fill text-info'
    }
    return icons[props.variant]
})

const positionClass = computed(() => {
    const positions = {
        'top-right': 'toast-top-right',
        'top-left': 'toast-top-left',
        'bottom-right': 'toast-bottom-right',
        'bottom-left': 'toast-bottom-left',
        'top-center': 'toast-top-center'
    }
    return positions[props.position]
})

const variantClass = computed(() => {
    return `toast-variant-${props.variant}`
})

const close = () => {
    visible.value = false
    setTimeout(() => {
        emit('close')
    }, 300)
}

onMounted(() => {
    visible.value = true

    if (props.duration > 0) {
        setTimeout(() => {
            close()
        }, props.duration)
    }
})
</script>
<style scoped>
.toast-container {
    position: fixed;
    z-index: 1050;
    min-width: 300px;
    max-width: 400px;
    font-size: 0.9rem;
    color: #2c3e50;
    font-weight: 500;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: none;
    border-left: 4px solid #f57c00;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08);
    font-family: inherit;
}

.toast-top-right {
    top: 20px;
    right: 20px;
}

.toast-top-left {
    top: 20px;
    left: 20px;
}

.toast-bottom-right {
    bottom: 20px;
    right: 20px;
}

.toast-bottom-left {
    bottom: 20px;
    left: 20px;
}

.toast-top-center {
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
}

.toast-content {
    font-weight: 500;
}

.toast-icon {
    font-size: 1.1rem;
}

.toast-close {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    opacity: 0.7;
    transition: all 0.2s ease;
    background: none;
    border: none;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

.toast-close:hover {
    background-color: rgba(0, 0, 0, 0.1);
    opacity: 1;
    transform: scale(1.1);
}

.toast-close:active {
    transform: scale(0.95);
}

.toast-enter-active,
.toast-leave-active {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.toast-enter-from {
    opacity: 0;
    transform: translateX(100%) scale(0.95);
}

.toast-leave-to {
    opacity: 0;
    transform: translateX(100%) scale(0.95);
}

.toast-enter-to,
.toast-leave-from {
    opacity: 1;
    transform: translateX(0) scale(1);
}

.toast-top-left .toast-enter-from,
.toast-top-left .toast-leave-to,
.toast-bottom-left .toast-enter-from,
.toast-bottom-left .toast-leave-to {
    transform: translateX(-100%) scale(0.95);
}

.toast-bottom-right .toast-enter-from,
.toast-bottom-right .toast-leave-to {
    transform: translateY(100%) scale(0.95);
}

.toast-top-center .toast-enter-from,
.toast-top-center .toast-leave-to {
    transform: translateX(-50%) translateY(-100%) scale(0.95);
}

.toast-top-center .toast-enter-to,
.toast-top-center .toast-leave-from {
    transform: translateX(-50%) translateY(0) scale(1);
}
</style>

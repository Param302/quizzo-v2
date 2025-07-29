import { ref, createApp } from 'vue'
import Toast from '@/components/Toast.vue'

const toasts = ref([])
let toastId = 0

export function useToast() {
    const showToast = (message, options = {}) => {
        const id = ++toastId
        const defaultOptions = {
            variant: 'success',
            duration: 4000,
            dismissible: true,
            position: 'top-right'
        }
        
        const toastOptions = { ...defaultOptions, ...options }
        
        // Create a container for this specific toast
        const container = document.createElement('div')
        document.body.appendChild(container)
        
        // Create the toast app instance
        const toastApp = createApp(Toast, {
            message,
            ...toastOptions,
            onClose: () => {
                toastApp.unmount()
                if (container.parentNode) {
                    container.parentNode.removeChild(container)
                }
                // Remove from toasts array
                const index = toasts.value.findIndex(t => t.id === id)
                if (index > -1) {
                    toasts.value.splice(index, 1)
                }
            }
        })
        
        // Mount the toast
        toastApp.mount(container)
        
        // Add to toasts array for tracking
        const toast = {
            id,
            message,
            ...toastOptions,
            app: toastApp,
            container
        }
        
        toasts.value.push(toast)
        
        return id
    }
    
    const showSuccess = (message, options = {}) => {
        return showToast(message, { ...options, variant: 'success' })
    }
    
    const showError = (message, options = {}) => {
        return showToast(message, { ...options, variant: 'error' })
    }
    
    const showWarning = (message, options = {}) => {
        return showToast(message, { ...options, variant: 'warning' })
    }
    
    const showInfo = (message, options = {}) => {
        return showToast(message, { ...options, variant: 'info' })
    }
    
    const clearAllToasts = () => {
        toasts.value.forEach(toast => {
            toast.app.unmount()
            if (toast.container.parentNode) {
                toast.container.parentNode.removeChild(toast.container)
            }
        })
        toasts.value = []
    }
    
    const removeToast = (id) => {
        const toast = toasts.value.find(t => t.id === id)
        if (toast) {
            toast.app.unmount()
            if (toast.container.parentNode) {
                toast.container.parentNode.removeChild(toast.container)
            }
            const index = toasts.value.findIndex(t => t.id === id)
            if (index > -1) {
                toasts.value.splice(index, 1)
            }
        }
    }
    
    return {
        showToast,
        showSuccess,
        showError,
        showWarning,
        showInfo,
        clearAllToasts,
        removeToast,
        toasts: toasts.value
    }
}

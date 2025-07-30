<template>
    <div class="action-card h-100">
        <div class="card glass-card h-100">
            <div class="card-body d-flex flex-column">
                <div class="action-icon mb-3">
                    <i :class="icon" class="fs-1"></i>
                </div>
                <h5 class="action-title fw-bold mb-2">{{ title }}</h5>
                <p class="action-description text-muted mb-3 flex-grow-1">{{ description }}</p>
                <button 
                    class="btn btn-action w-100" 
                    @click="$emit('click')"
                    :disabled="disabled"
                >
                    <i :class="buttonIcon" class="me-2"></i>
                    {{ buttonText }}
                </button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'ActionCard',
    props: {
        icon: {
            type: String,
            required: true
        },
        title: {
            type: String,
            required: true
        },
        description: {
            type: String,
            required: true
        },
        buttonText: {
            type: String,
            required: true
        },
        buttonIcon: {
            type: String,
            default: 'bi bi-arrow-right'
        },
        disabled: {
            type: Boolean,
            default: false
        }
    },
    emits: ['click']
}
</script>

<style scoped>
.glass-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(245, 124, 0, 0.1);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
    transition: all 0.3s ease;
}

.glass-card:hover {
    box-shadow: 0 12px 40px rgba(245, 124, 0, 0.15);
    border-color: rgba(245, 124, 0, 0.2);
}

.action-icon i {
    color: #f57c00 !important;
}

.action-title {
    color: #f57c00;
}

.btn-action {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    border-radius: 12px;
    color: white;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    transition: all 0.3s ease;
}

.btn-action:hover:not(:disabled) {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.4);
}

.btn-action:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}
</style>

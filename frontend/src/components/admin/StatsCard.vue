<template>
    <div class="stats-card h-100">
        <div class="card glass-card h-100">
            <div class="card-body text-center">
                <div class="stats-icon mb-3">
                    <i :class="icon" class="fs-1"></i>
                </div>
                <h3 class="stats-number fw-bold mb-2">{{ formattedValue }}</h3>
                <p class="stats-label text-muted mb-0">{{ label }}</p>
                <div v-if="trend" class="stats-trend mt-2">
                    <span :class="trendClass">
                        <i :class="trendIcon" class="me-1"></i>
                        {{ trend }}
                    </span>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'StatsCard',
    props: {
        icon: {
            type: String,
            required: true
        },
        value: {
            type: [Number, String],
            required: true
        },
        label: {
            type: String,
            required: true
        },
        trend: {
            type: String,
            default: null
        },
        color: {
            type: String,
            default: 'orange'
        }
    },
    computed: {
        formattedValue() {
            if (typeof this.value === 'number') {
                return this.value.toLocaleString()
            }
            return this.value
        },
        trendClass() {
            if (!this.trend) return ''
            const isPositive = this.trend.includes('+') || this.trend.includes('up')
            return isPositive ? 'text-success' : 'text-danger'
        },
        trendIcon() {
            if (!this.trend) return ''
            const isPositive = this.trend.includes('+') || this.trend.includes('up')
            return isPositive ? 'bi bi-arrow-up' : 'bi bi-arrow-down'
        }
    }
}
</script>

<style scoped>
.stats-card {
    transition: all 0.3s ease;
}

.stats-card:hover {
    transform: translateY(-5px);
}

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

.stats-icon i {
    color: #f57c00 !important;
    text-shadow: 0 2px 4px rgba(245, 124, 0, 0.2);
}

.stats-number {
    color: #f57c00;
    font-size: 2.5rem;
}

.stats-label {
    font-weight: 600;
    letter-spacing: 0.5px;
}

.stats-trend {
    font-size: 0.9rem;
    font-weight: 600;
}

@media (max-width: 768px) {
    .stats-number {
        font-size: 2rem;
    }
    
    .stats-icon i {
        font-size: 2rem !important;
    }
}
</style>

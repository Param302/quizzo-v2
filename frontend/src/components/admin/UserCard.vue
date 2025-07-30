<template>
    <div class="user-card h-100">
        <div class="card glass-card h-100">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div class="user-info">
                        <h6 class="user-name fw-bold mb-1">{{ user.username }}</h6>
                        <p class="user-email text-muted mb-0">{{ user.email }}</p>
                    </div>
                    <div class="user-avatar">
                        <div class="avatar-circle">
                            <i class="bi bi-person-fill"></i>
                        </div>
                    </div>
                </div>

                <div class="user-stats mb-3">
                    <div class="row g-2">
                        <div class="col-4">
                            <div class="stat-item text-center">
                                <div class="stat-number">{{ user.stats.quiz_attempts }}</div>
                                <div class="stat-label">Attempts</div>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="stat-item text-center">
                                <div class="stat-number">{{ user.stats.subscriptions }}</div>
                                <div class="stat-label">Subscriptions</div>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="stat-item text-center">
                                <div class="stat-number">{{ user.stats.average_score }}%</div>
                                <div class="stat-label">Avg Score</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="user-meta mb-3">
                    <small class="text-muted">
                        <i class="bi bi-calendar-plus me-1"></i>
                        Joined {{ formatDate(user.created_at) }}
                    </small>
                </div>

                <button 
                    class="btn btn-danger w-100" 
                    @click="$emit('delete-user', user.id)"
                    :disabled="deleting"
                >
                    <i class="bi bi-trash me-2"></i>
                    {{ deleting ? 'Deleting...' : 'Delete User' }}
                </button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'UserCard',
    props: {
        user: {
            type: Object,
            required: true
        },
        deleting: {
            type: Boolean,
            default: false
        }
    },
    emits: ['delete-user'],
    methods: {
        formatDate(dateString) {
            if (!dateString) return 'Unknown'
            const date = new Date(dateString)
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            })
        }
    }
}
</script>

<style scoped>
.user-card {
    transition: all 0.3s ease;
}

.user-card:hover {
    transform: translateY(-3px);
}

.glass-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(245, 124, 0, 0.1);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
    transition: all 0.3s ease;
}

.glass-card:hover {
    box-shadow: 0 12px 40px rgba(245, 124, 0, 0.15);
    border-color: rgba(245, 124, 0, 0.2);
}

.user-name {
    color: #2c3e50;
    font-size: 1.1rem;
}

.user-email {
    font-size: 0.9rem;
}

.avatar-circle {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.2rem;
}

.stat-item {
    padding: 0.5rem;
}

.stat-number {
    font-weight: 700;
    font-size: 1.1rem;
    color: #f57c00;
}

.stat-label {
    font-size: 0.7rem;
    color: #6c757d;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.btn-danger {
    background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
    border: none;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.btn-danger:hover:not(:disabled) {
    background: linear-gradient(135deg, #c82333 0%, #a71e2a 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4);
}

@media (max-width: 576px) {
    .stat-number {
        font-size: 1rem;
    }
    
    .stat-label {
        font-size: 0.6rem;
    }
}
</style>

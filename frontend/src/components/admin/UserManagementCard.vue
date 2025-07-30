<template>
    <div class="user-management-card h-100">
        <div class="card glass-card h-100">
            <div class="card-body">
                <!-- User Header -->
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div class="user-info flex-grow-1">
                        <h4 class="user-name fw-bold mb-1">{{ user.name }}</h4>
                        <p class="user-username text-muted mb-1">@{{ user.username }}</p>
                        <p class="user-email small text-muted mb-0">{{ user.email }}</p>
                    </div>
                    <div class="user-avatar-section">
                        <div class="avatar-circle">
                            <i class="bi bi-person-fill"></i>
                        </div>
                        <!-- Join Date -->
                        <div class="user-meta mt-1">
                            <small class="text-muted">
                                <i class="bi bi-calendar-plus me-1"></i>
                                Joined {{ formatDate(user.created_at) }}
                            </small>
                        </div>
                    </div>
                </div>

                <!-- User Stats -->
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
                                <div class="stat-label">Subscribed</div>
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

                <!-- Action Buttons -->
                <div class="user-actions">
                    <div class="row g-3">
                        <div class="col-9">
                            <button class="btn btn-primary-orange w-100" @click="viewProfile" :disabled="loading">
                                <i class="bi bi-person-circle me-2"></i>
                                View Profile
                            </button>
                        </div>
                        <div class="col-3">
                            <button class="btn btn-danger-icon w-100" @click="$emit('delete-user', user.id)"
                                :disabled="deleting || loading" :title="deleting ? 'Deleting...' : 'Delete User'">
                                <i v-if="deleting" class="bi bi-hourglass-split"></i>
                                <i v-else class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'UserManagementCard',
    props: {
        user: {
            type: Object,
            required: true
        },
        deleting: {
            type: Boolean,
            default: false
        },
        loading: {
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
        },
        viewProfile() {
            // Navigate to public profile
            this.$router.push(`/u/@${this.user.username}`)
        }
    }
}
</script>

<style scoped>
.user-management-card {
    transition: all 0.3s ease;
}

.user-management-card:hover {
    transform: translateY(-5px);
}

.glass-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(245, 124, 0, 0.1);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
    transition: all 0.3s ease;
    overflow: hidden;
    min-height: 320px;
}

.glass-card:hover {
    box-shadow: 0 12px 40px rgba(245, 124, 0, 0.2);
    border-color: rgba(245, 124, 0, 0.25);
    background: rgba(255, 255, 255, 0.98);
}

.glass-card:hover .user-name {
    color: #f57c00;
}

.user-name {
    color: #2c3e50;
    font-size: 1.3rem;
    transition: color 0.3s ease;
}

.user-username {
    font-size: 1rem;
    font-weight: 600;
    color: #f57c00 !important;
}

.user-email {
    font-size: 0.9rem;
}

.avatar-circle {
    width: 55px;
    height: 55px;
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.5rem;
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.user-avatar-section {
    display: flex;
    flex-direction: column;
    align-items: end;
    min-width: 120px;
}

.user-meta {
    padding: 0.5rem;
    background: transparent;
    border-radius: 8px;
    text-align: center;
    font-size: 0.75rem;
}

.stat-item {
    padding: 1rem 0.75rem;
    border-radius: 12px;
    background: rgba(245, 124, 0, 0.05);
    border: 1px solid rgba(245, 124, 0, 0.1);
    transition: all 0.3s ease;
}

.stat-item:hover {
    background: rgba(245, 124, 0, 0.1);
    border-color: rgba(245, 124, 0, 0.2);
}

.stat-number {
    font-weight: 700;
    font-size: 1.4rem;
    color: #f57c00;
    line-height: 1;
}

.stat-label {
    font-size: 0.75rem;
    color: #6c757d;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 0.5rem;
}

.btn-primary-orange {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    color: white;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    font-size: 1rem;
    padding: 0.75rem 1.5rem;
}

.btn-primary-orange:hover:not(:disabled) {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.4);
    color: white;
}

.btn-danger-icon {
    background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
    border: none;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    font-size: 1.1rem;
    padding: 0.75rem;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn-danger-icon:hover:not(:disabled) {
    background: linear-gradient(135deg, #c82333 0%, #a71e2a 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4);
    color: white;
}

.btn-outline-orange {
    border: 2px solid #f57c00;
    color: #f57c00;
    background: transparent;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    font-size: 0.9rem;
}

.btn-outline-orange:hover:not(:disabled) {
    background: #f57c00;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.btn-danger {
    background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
    border: none;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    font-size: 0.9rem;
}

.btn-danger:hover:not(:disabled) {
    background: linear-gradient(135deg, #c82333 0%, #a71e2a 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .stat-number {
        font-size: 1.2rem;
    }

    .stat-label {
        font-size: 0.7rem;
    }

    .user-name {
        font-size: 1.2rem;
    }

    .user-username {
        font-size: 0.9rem;
    }

    .avatar-circle {
        width: 50px;
        height: 50px;
        font-size: 1.3rem;
    }

    .user-avatar-section {
        min-width: 100px;
    }

    .user-meta {
        font-size: 0.7rem;
        padding: 0.4rem;
    }

    .glass-card {
        min-height: 380px;
    }
}

@media (max-width: 576px) {
    .stat-number {
        font-size: 1.1rem;
    }

    .stat-label {
        font-size: 0.65rem;
    }

    .user-name {
        font-size: 1.1rem;
    }

    .user-username {
        font-size: 0.85rem;
    }

    .btn-primary-orange {
        font-size: 0.9rem;
        padding: 0.6rem 1.2rem;
    }

    .btn-danger-icon {
        font-size: 1rem;
        padding: 0.6rem;
    }

    .avatar-circle {
        width: 45px;
        height: 45px;
        font-size: 1.2rem;
    }

    .user-avatar-section {
        min-width: 85px;
    }

    .user-meta {
        font-size: 0.65rem;
        padding: 0.3rem;
    }

    .glass-card {
        min-height: 360px;
    }
}
</style>

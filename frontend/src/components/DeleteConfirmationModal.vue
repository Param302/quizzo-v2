<template>
    <div class="modal modal-backdrop" style="display: block;" v-if="show" @click.self="$emit('close')">
        <div class="modal-dialog modal-custom modal-dialog-centered">
            <div class="modal-content delete-modal" :class="{ 'slide-up': show, 'slide-down': !show }">
                <div class="modal-header border-0">
                    <div class="w-100 d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <div class="d-flex align-items-center mb-2">
                                <div class="warning-icon me-3">
                                    <i class="bi bi-exclamation-triangle"></i>
                                </div>
                                <h4 class="modal-title fw-bold mb-0 delete-title">{{ title }}</h4>
                            </div>
                            <p class="text-muted mb-0">{{ message }}</p>
                        </div>
                        <button type="button" class="btn-close-custom" @click="$emit('close')">
                            <i class="bi bi-x"></i>
                        </button>
                    </div>
                </div>

                <div class="modal-body">
                    <!-- Item Details -->
                    <div class="item-details mb-4" v-if="itemDetails">
                        <div class="detail-card">
                            <div class="row g-3">
                                <div class="col-12" v-if="itemDetails.name">
                                    <div class="detail-item">
                                        <span class="detail-label">Name:</span>
                                        <span class="detail-value">{{ itemDetails.name }}</span>
                                    </div>
                                </div>
                                <div class="col-md-6" v-if="itemDetails.email">
                                    <div class="detail-item">
                                        <span class="detail-label">Email:</span>
                                        <span class="detail-value">{{ itemDetails.email }}</span>
                                    </div>
                                </div>
                                <div class="col-md-6" v-if="itemDetails.username">
                                    <div class="detail-item">
                                        <span class="detail-label">Username:</span>
                                        <span class="detail-value">@{{ itemDetails.username }}</span>
                                    </div>
                                </div>
                                <div class="col-md-6" v-if="itemDetails.created_at">
                                    <div class="detail-item">
                                        <span class="detail-label">Joined:</span>
                                        <span class="detail-value">{{ formatDate(itemDetails.created_at) }}</span>
                                    </div>
                                </div>
                                <div class="col-md-6" v-if="itemDetails.type">
                                    <div class="detail-item">
                                        <span class="detail-label">Type:</span>
                                        <span class="detail-value">{{ itemDetails.type }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    

                    <!-- Action Buttons -->
                    <div class="action-buttons">
                        <div class="row g-3">
                            <div class="col-6">
                                <button class="btn btn-secondary w-100" @click="$emit('close')" :disabled="loading">
                                    <i class="bi bi-x-circle me-2"></i>
                                    Cancel
                                </button>
                            </div>
                            <div class="col-6">
                                <button class="btn btn-danger w-100" @click="$emit('confirm')" :disabled="loading">
                                    <i v-if="loading" class="bi bi-hourglass-split me-2"></i>
                                    <i v-else class="bi bi-trash me-2"></i>
                                    {{ loading ? 'Deleting...' : 'Delete' }}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'DeleteConfirmationModal',
    props: {
        show: {
            type: Boolean,
            default: false
        },
        title: {
            type: String,
            default: 'Confirm Deletion'
        },
        message: {
            type: String,
            default: 'Are you sure you want to delete this item?'
        },
        itemDetails: {
            type: Object,
            default: null
        },
        loading: {
            type: Boolean,
            default: false
        }
    },
    emits: ['close', 'confirm'],
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
@keyframes slideUp {
    from {
        transform: translateY(100%);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

@keyframes slideDown {
    from {
        transform: translateY(0);
        opacity: 1;
    }
    to {
        transform: translateY(100%);
        opacity: 0;
    }
}

.modal-backdrop {
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(5px);
}

.modal-custom {
    max-width: 500px;
}

.delete-modal {
    border-radius: 20px;
    border: none;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
    background: #ffffff;
    overflow: hidden;
}

.slide-up {
    animation: slideUp 0.3s ease-out;
}

.slide-down {
    animation: slideDown 0.3s ease-in;
}

/* Header Styles */
.modal-header {
    padding: 2rem 2rem 0 2rem;
    background: transparent;
}

.modal-body {
    padding: 1rem 2rem 2rem 2rem;
}

.delete-title {
    color: #dc3545;
    font-size: 1.3rem;
}

.warning-icon {
    width: 50px;
    height: 50px;
    background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.5rem;
    flex-shrink: 0;
}


.btn-close-custom {
    border: none;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #6c757d;
    font-size: 1.2rem;
    transition: all 0.3s ease;
}

.btn-close-custom:hover {
    background: rgba(220, 53, 69, 0.1);
    color: #dc3545;
    transform: scale(1.1);
}

/* Detail Cards */
.detail-card {
    background: rgba(245, 124, 0, 0.05);
    border: 1px solid rgba(245, 124, 0, 0.1);
    border-radius: 16px;
    padding: 1.5rem;
}

.detail-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.detail-label {
    font-size: 0.8rem;
    color: #6c757d;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.detail-value {
    font-size: 1rem;
    color: #2c3e50;
    font-weight: 600;
}




/* Buttons */
.btn {
    border-radius: 12px;
    font-weight: 600;
    padding: 0.75rem 1rem;
    transition: all 0.3s ease;
    font-size: 1rem;
}

.btn-secondary {
    background: #6c757d;
    border: none;
    color: white;
}

.btn-secondary:hover:not(:disabled) {
    background: #5a6268;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
    color: white;
}

.btn-danger {
    background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
    border: none;
    color: white;
}

.btn-danger:hover:not(:disabled) {
    background: linear-gradient(135deg, #c82333 0%, #a71e2a 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(220, 53, 69, 0.4);
    color: white;
}

.btn:disabled {
    opacity: 0.6;
    transform: none !important;
    box-shadow: none !important;
}

/* Responsive */
@media (max-width: 768px) {
    .modal-custom {
        max-width: 95%;
    }

    .modal-header,
    .modal-body {
        padding: 1.5rem;
    }

    .delete-title {
        font-size: 1.2rem;
    }

    .warning-icon {
        width: 45px;
        height: 45px;
        font-size: 1.3rem;
    }


    .detail-card {
        padding: 1rem;
    }
}
</style>

<template>
    <div class="modal modal-backdrop d-flex align-items-center justify-content-center" v-if="show">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content time-up-modal">
                <div class="modal-body text-center p-5">
                    <div class="time-up-icon mb-4">
                        <i class="bi bi-clock-history"></i>
                    </div>
                    
                    <h3 class="modal-title fw-bold mb-3 text-danger">Time's Up!</h3>
                    
                    <p class="modal-text mb-4">
                        The quiz time has ended. Your answers have been automatically submitted.
                        <span v-if="unansweredQuestions > 0" class="d-block mt-2 text-muted">
                            <strong>{{ unansweredQuestions }}</strong> question{{ unansweredQuestions !== 1 ? 's' : '' }} 
                            {{ unansweredQuestions !== 1 ? 'were' : 'was' }} left unanswered.
                        </span>
                    </p>
                    
                    <button 
                        class="btn btn-primary btn-lg px-4"
                        @click="acknowledge"
                        :disabled="submitting">
                        <i v-if="submitting" class="bi bi-hourglass-split me-2"></i>
                        <i v-else class="bi bi-check-circle me-2"></i>
                        {{ submitting ? 'Processing...' : 'View Results' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'QuizTimeUpModal',
    props: {
        show: {
            type: Boolean,
            default: false
        },
        unansweredQuestions: {
            type: Number,
            default: 0
        },
        submitting: {
            type: Boolean,
            default: false
        }
    },
    emits: ['acknowledge'],
    methods: {
        acknowledge() {
            this.$emit('acknowledge')
        }
    }
}
</script>

<style scoped>
.modal-backdrop {
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(5px);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1050;
}

.time-up-modal {
    border: none;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    animation: slideUp 0.3s ease-out;
}

.time-up-icon {
    font-size: 4rem;
    color: #dc3545;
    animation: pulse 2s infinite;
}

.modal-title {
    font-size: 2rem;
    color: #dc3545;
}

.modal-text {
    font-size: 1.1rem;
    line-height: 1.6;
    color: #6c757d;
    max-width: 400px;
    margin: 0 auto;
}

.btn-primary {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.btn-primary:hover:not(:disabled) {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(245, 124, 0, 0.4);
}

.btn-primary:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
}

@keyframes slideUp {
    from {
        transform: translateY(100px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

@keyframes pulse {
    0% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.1);
    }
    100% {
        transform: scale(1);
    }
}

/* Responsive Design */
@media (max-width: 768px) {
    .modal-body {
        padding: 2rem 1.5rem !important;
    }
    
    .time-up-icon {
        font-size: 3rem;
    }
    
    .modal-title {
        font-size: 1.75rem;
    }
    
    .modal-text {
        font-size: 1rem;
    }
}
</style>

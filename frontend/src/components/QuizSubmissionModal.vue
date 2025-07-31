<template>
    <div v-if="show" class="modal-overlay" @click.self="$emit('cancel')">
        <div class="modal-container">
            <div class="modal-header">
                <h4 class="modal-title">
                    <i class="bi bi-check-circle me-2"></i>
                    Submit Quiz?
                </h4>
                <button type="button" class="btn-close" @click="$emit('cancel')">
                    <i class="bi bi-x-lg"></i>
                </button>
            </div>

            <div class="modal-body">
                <div class="submission-summary mb-4">
                    <div class="summary-stats">
                        <div class="stat-item">
                            <span class="stat-number answered">{{ answeredCount }}</span>
                            <span class="stat-label">Answered</span>
                        </div>
                        <div class="stat-divider">/</div>
                        <div class="stat-item">
                            <span class="stat-number total">{{ totalQuestions }}</span>
                            <span class="stat-label">Total</span>
                        </div>
                    </div>

                    <div v-if="unansweredCount > 0" class="warning-message">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        You have {{ unansweredCount }} unanswered question{{ unansweredCount !== 1 ? 's' : '' }}
                    </div>
                </div>

                <div class="questions-grid">
                    <div class="grid-header">
                        <span class="grid-title">Question Status</span>
                        <div class="legend">
                            <div class="legend-item">
                                <div class="legend-circle answered"></div>
                                <span>Answered</span>
                            </div>
                            <div class="legend-item">
                                <div class="legend-circle unanswered"></div>
                                <span>Unanswered</span>
                            </div>
                        </div>
                    </div>

                    <div class="questions-status">
                        <div v-for="(question, index) in questions" :key="question.id" class="question-circle" :class="{
                            'answered': isQuestionAnswered(question.id),
                            'current': index === currentQuestionIndex
                        }" @click="$emit('goToQuestion', index)">
                            {{ index + 1 }}
                        </div>
                    </div>
                </div>
            </div>

            <div class="modal-footer">
                <button type="button" class="btn btn-secondary me-3" @click="$emit('cancel')">
                    <i class="bi bi-arrow-left me-2"></i>
                    Review Questions
                </button>
                <button type="button" class="btn btn-primary" @click="$emit('confirm')" :disabled="submitting">
                    <i v-if="submitting" class="bi bi-hourglass-split me-2"></i>
                    <i v-else class="bi bi-check-circle me-2"></i>
                    {{ submitting ? 'Submitting...' : 'Submit Quiz' }}
                </button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'QuizSubmissionModal',
    props: {
        show: {
            type: Boolean,
            default: false
        },
        questions: {
            type: Array,
            required: true
        },
        answers: {
            type: Object,
            required: true
        },
        currentQuestionIndex: {
            type: Number,
            required: true
        },
        submitting: {
            type: Boolean,
            default: false
        }
    },
    emits: ['confirm', 'cancel', 'goToQuestion'],
    computed: {
        totalQuestions() {
            return this.questions.length
        },
        answeredCount() {
            return this.questions.filter(question =>
                this.isQuestionAnswered(question.id)
            ).length
        },
        unansweredCount() {
            return this.totalQuestions - this.answeredCount
        }
    },
    methods: {
        isQuestionAnswered(questionId) {
            const answer = this.answers[questionId]
            return answer && answer.length > 0
        }
    }
}
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(5px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    padding: 1rem;
}

.modal-container {
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    max-width: 600px;
    width: 100%;
    max-height: 80vh;
    overflow: hidden;
    animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
    from {
        opacity: 0;
        transform: translateY(-30px) scale(0.95);
    }

    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem;
    border-bottom: 2px solid rgba(245, 124, 0, 0.1);
    background: linear-gradient(135deg, rgba(245, 124, 0, 0.05) 0%, rgba(245, 124, 0, 0.02) 100%);
}

.modal-title {
    color: #2c3e50;
    font-weight: 700;
    font-size: 1.25rem;
    margin: 0;
    display: flex;
    align-items: center;
}

.modal-title i {
    color: #f57c00;
}

.btn-close {
    background: none;
    border: none;
    font-size: 1.2rem;
    color: #6c757d;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 50%;
    transition: all 0.3s ease;
}

.btn-close:hover {
    background: rgba(108, 117, 125, 0.1);
    color: #495057;
}

.modal-body {
    padding: 1.5rem;
    max-height: 60vh;
    overflow-y: auto;
}

.submission-summary {
    text-align: center;
}

.summary-stats {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stat-number {
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
}

.stat-number.answered {
    color: #f57c00;
}

.stat-number.total {
    color: #6c757d;
}

.stat-label {
    font-size: 0.875rem;
    color: #6c757d;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stat-divider {
    font-size: 1.5rem;
    color: #dee2e6;
    font-weight: 300;
}

.warning-message {
    background: rgba(220, 53, 69, 0.1);
    color: #dc3545;
    padding: 0.75rem 1rem;
    border-radius: 10px;
    font-weight: 600;
    border: 1px solid rgba(220, 53, 69, 0.2);
}

.questions-grid {
    margin-top: 1.5rem;
}

.grid-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.grid-title {
    font-weight: 600;
    color: #2c3e50;
    font-size: 1rem;
}

.legend {
    display: flex;
    gap: 1rem;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: #6c757d;
}

.legend-circle {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    border: 2px solid #dee2e6;
}

.legend-circle.answered {
    background: #f57c00;
    border-color: #f57c00;
}

.questions-status {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(45px, 1fr));
    gap: 0.75rem;
    max-height: 200px;
    overflow-y: auto;
    padding: 0.5rem;
    background: rgba(248, 249, 250, 0.5);
    border-radius: 10px;
}

.question-circle {
    width: 45px;
    height: 45px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2px solid #dee2e6;
    background: white;
    color: #6c757d;
}

.question-circle:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.question-circle.answered {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border-color: #f57c00;
    color: white;
}

.question-circle.current {
    border-color: #007bff;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
}

.modal-footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding: 1.5rem;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    background: rgba(248, 249, 250, 0.5);
}

.btn {
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background: #5a6268;
    transform: translateY(-1px);
}

.btn-primary {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.btn-primary:hover:not(:disabled) {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(245, 124, 0, 0.4);
}

.btn-primary:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
}

/* Responsive Design */
@media (max-width: 576px) {
    .modal-container {
        margin: 0.5rem;
        max-height: 85vh;
    }

    .questions-status {
        grid-template-columns: repeat(auto-fill, minmax(40px, 1fr));
        gap: 0.5rem;
    }

    .question-circle {
        width: 40px;
        height: 40px;
        font-size: 0.8rem;
    }

    .modal-footer {
        flex-direction: column;
        gap: 0.75rem;
    }

    .btn {
        width: 100%;
        justify-content: center;
    }

    .summary-stats {
        flex-direction: column;
        gap: 0.5rem;
    }

    .stat-divider {
        transform: rotate(90deg);
    }
}
</style>

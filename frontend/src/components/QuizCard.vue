<template>
    <div class="quiz-card h-100">
        <div class="card glass-card h-100">
            <div class="card-body d-flex flex-column">
                <!-- Quiz Header -->
                <div class="quiz-header mb-3">
                    <div class="d-flex align-items-start justify-content-between mb-2">
                        <h6 class="quiz-title mb-0">{{ quiz.title }}</h6>
                        <div class="quiz-status-badge">
                            <span class="badge" :class="getStatusBadgeClass()">
                                <i :class="getStatusIcon()" class="me-1"></i>
                                {{ getStatusText() }}
                            </span>
                        </div>
                    </div>

                    <div v-if="quiz.remarks" class="quiz-remarks">
                        <p class="text-muted small mb-0">{{ quiz.remarks }}</p>
                    </div>
                </div>

                <!-- Quiz Details -->
                <div class="quiz-details mb-3">
                    <div class="row g-2">
                        <div class="col-6">
                            <div class="detail-item">
                                <i class="bi bi-question-circle text-primary"></i>
                                <span class="ms-1">{{ quiz.question_count }} Questions</span>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="detail-item">
                                <i class="bi bi-award text-success"></i>
                                <span class="ms-1">{{ quiz.total_marks }} Marks</span>
                            </div>
                        </div>
                        <div v-if="quiz.time_duration" class="col-12">
                            <div class="detail-item">
                                <i class="bi bi-clock text-info"></i>
                                <span class="ms-1">{{ quiz.time_duration }} Duration</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Date/Time Information -->
                <div v-if="quiz.date_of_quiz" class="quiz-datetime mb-3">
                    <div class="datetime-card">
                        <div class="d-flex align-items-center">
                            <i class="bi bi-calendar-event text-primary me-2"></i>
                            <div>
                                <div class="fw-semibold">{{ formatDate(quiz.date_of_quiz) }}</div>
                                <div class="text-muted small">{{ getTimeInfo() }}</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- User Score (for completed quizzes) -->
                <div v-if="quiz.user_score && tabType === 'completed'" class="user-score mb-3">
                    <div class="score-card">
                        <div class="d-flex align-items-center justify-content-between">
                            <div>
                                <div class="score-label">Your Score</div>
                                <div class="score-value">
                                    {{ quiz.user_score.obtained_marks }}/{{ quiz.user_score.total_marks }}
                                </div>
                            </div>
                            <div class="score-percentage">
                                <div class="circular-progress" :style="{ '--percentage': quiz.user_score.percentage }">
                                    <span>{{ Math.round(quiz.user_score.percentage) }}%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Actions -->
                <div class="mt-auto">
                    <div class="quiz-actions">
                        <!-- Live Quiz Actions -->
                        <template v-if="tabType === 'live'">
                            <button class="btn btn-success w-100" @click="$emit('start-quiz', quiz.id)"
                                :disabled="quiz.is_completed">
                                <i class="bi bi-play-circle me-2"></i>
                                {{ quiz.is_completed ? 'Already Completed' : 'Start Quiz' }}
                            </button>
                        </template>

                        <!-- General Quiz Actions -->
                        <template v-else-if="tabType === 'general'">
                            <button class="btn btn-primary w-100" @click="$emit('start-quiz', quiz.id)"
                                :disabled="quiz.is_completed">
                                <i class="bi bi-play-circle me-2"></i>
                                {{ quiz.is_completed ? 'Already Completed' : 'Start Quiz' }}
                            </button>
                        </template>

                        <!-- Upcoming Quiz Actions -->
                        <template v-else-if="tabType === 'upcoming'">
                            <button class="btn btn-outline-secondary w-100" disabled>
                                <i class="bi bi-clock me-2"></i>
                                {{ getCountdownText() }}
                            </button>
                        </template>

                        <!-- Ended Quiz Actions -->
                        <template v-else-if="tabType === 'ended'">
                            <button class="btn btn-outline-danger w-100" disabled>
                                <i class="bi bi-x-circle me-2"></i>
                                {{ getEndedText() }}
                            </button>
                        </template>

                        <!-- Completed Quiz Actions -->
                        <template v-else-if="tabType === 'completed'">
                            <button class="btn btn-outline-primary w-100" @click="$emit('view-details', quiz.id)">
                                <i class="bi bi-eye me-2"></i>
                                View Details
                            </button>
                        </template>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'QuizCard',
    props: {
        quiz: {
            type: Object,
            required: true
        },
        tabType: {
            type: String,
            required: true
        }
    },
    emits: ['start-quiz', 'view-details'],
    methods: {
        getStatusBadgeClass() {
            switch (this.tabType) {
                case 'live':
                    return 'bg-success'
                case 'upcoming':
                    return 'bg-info'
                case 'general':
                    return 'bg-warning'
                case 'ended':
                    return 'bg-danger'
                case 'completed':
                    return 'bg-primary'
                default:
                    return 'bg-secondary'
            }
        },

        getStatusIcon() {
            switch (this.tabType) {
                case 'live':
                    return 'bi-broadcast'
                case 'upcoming':
                    return 'bi-clock'
                case 'general':
                    return 'bi-infinity'
                case 'ended':
                    return 'bi-calendar-x'
                case 'completed':
                    return 'bi-check-circle'
                default:
                    return 'bi-question-circle'
            }
        },

        getStatusText() {
            switch (this.tabType) {
                case 'live':
                    return 'Live Now'
                case 'upcoming':
                    return 'Upcoming'
                case 'general':
                    return 'Available'
                case 'ended':
                    return 'Ended'
                case 'completed':
                    return 'Completed'
                default:
                    return 'Unknown'
            }
        },

        formatDate(dateString) {
            const date = new Date(dateString)
            return date.toLocaleDateString('en-US', {
                weekday: 'short',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            })
        },

        getTimeInfo() {
            if (this.tabType === 'upcoming' && this.quiz.days_until !== undefined) {
                const days = this.quiz.days_until
                if (days === 0) return 'Today'
                if (days === 1) return 'Tomorrow'
                return `In ${days} days`
            }
            if (this.tabType === 'ended' && this.quiz.days_past !== undefined) {
                const days = this.quiz.days_past
                if (days === 0) return 'Today'
                if (days === 1) return 'Yesterday'
                return `${days} days ago`
            }
            return ''
        },

        getCountdownText() {
            if (this.quiz.days_until !== undefined) {
                const days = this.quiz.days_until
                if (days === 0) return 'Starting Today'
                if (days === 1) return 'Starting Tomorrow'
                return `${days} days left`
            }
            return 'Coming Soon'
        },

        getEndedText() {
            if (this.quiz.days_past !== undefined) {
                const days = this.quiz.days_past
                if (days === 0) return 'Ended Today'
                if (days === 1) return 'Ended Yesterday'
                return `Ended ${days} days ago`
            }
            return 'Quiz Ended'
        }
    }
}
</script>

<style scoped>
.quiz-card {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.quiz-card:hover {
    transform: translateY(-3px);
}

.glass-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(245, 124, 0, 0.1);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
    box-shadow: 0 12px 40px rgba(245, 124, 0, 0.15);
    border-color: rgba(245, 124, 0, 0.2);
}

.quiz-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #2c3e50;
    line-height: 1.3;
}

.quiz-remarks {
    font-style: italic;
}

.detail-item {
    display: flex;
    align-items: center;
    font-size: 0.85rem;
    font-weight: 500;
    color: #6c757d;
}

.detail-item i {
    font-size: 1rem;
}

.datetime-card {
    background: rgba(13, 110, 253, 0.05);
    border: 1px solid rgba(13, 110, 253, 0.15);
    border-radius: 12px;
    padding: 0.75rem;
}

.score-card {
    background: rgba(25, 135, 84, 0.05);
    border: 1px solid rgba(25, 135, 84, 0.15);
    border-radius: 12px;
    padding: 1rem;
}

.score-label {
    font-size: 0.85rem;
    color: #6c757d;
    font-weight: 500;
}

.score-value {
    font-size: 1.1rem;
    font-weight: 700;
    color: #198754;
}

.circular-progress {
    position: relative;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: conic-gradient(#198754 0deg,
            #198754 calc(var(--percentage) * 3.6deg),
            #e9ecef calc(var(--percentage) * 3.6deg),
            #e9ecef 360deg);
    display: flex;
    align-items: center;
    justify-content: center;
}

.circular-progress::before {
    content: '';
    position: absolute;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: white;
}

.circular-progress span {
    position: relative;
    z-index: 1;
    font-size: 0.7rem;
    font-weight: 600;
    color: #198754;
}

.btn {
    border-radius: 12px;
    font-weight: 600;
    padding: 0.75rem 1rem;
    transition: all 0.3s ease;
    font-size: 0.9rem;
}

.btn-success {
    background: linear-gradient(135deg, #198754 0%, #20c997 100%);
    border: none;
    box-shadow: 0 2px 8px rgba(25, 135, 84, 0.3);
}

.btn-success:hover:not(:disabled) {
    background: linear-gradient(135deg, #146c43 0%, #198754 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(25, 135, 84, 0.4);
}

.btn-primary {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    box-shadow: 0 2px 8px rgba(245, 124, 0, 0.3);
}

.btn-primary:hover:not(:disabled) {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(245, 124, 0, 0.4);
}

.btn-outline-primary {
    border-color: rgba(245, 124, 0, 0.3);
    color: #f57c00;
}

.btn-outline-primary:hover {
    background-color: #f57c00;
    border-color: #f57c00;
    color: white;
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.badge {
    font-size: 0.7rem;
    padding: 0.4rem 0.6rem;
    border-radius: 8px;
    font-weight: 600;
}

@media (max-width: 768px) {
    .quiz-title {
        font-size: 1rem;
    }

    .btn {
        font-size: 0.85rem;
        padding: 0.6rem 0.8rem;
    }

    .circular-progress {
        width: 35px;
        height: 35px;
    }

    .circular-progress::before {
        width: 25px;
        height: 25px;
    }
}
</style>

<template>
    <div class="admin-quiz-card h-100">
        <div class="card glass-card h-100">
            <div class="card-body p-4">
                <!-- Quiz Header -->
                <div class="quiz-header mb-3">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h5 class="quiz-title fw-bold mb-0 flex-grow-1">{{ quiz.title }}</h5>
                        <div class="quiz-actions">
                            <button v-if="canEdit" class="btn btn-sm btn-primary-icon me-1"
                                @click="$emit('edit-quiz', quiz.id)" title="Edit Quiz">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-danger-icon" @click="$emit('delete-quiz', quiz.id)"
                                title="Delete Quiz">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                    <p class="quiz-remarks text-muted mb-0" v-if="quiz.remarks">{{ quiz.remarks }}</p>
                </div>

                <!-- Quiz Stats -->
                <div class="quiz-stats mb-3">
                    <div class="row g-2">
                        <div class="col-4">
                            <div class="stat-item text-center">
                                <div class="stat-number">{{ quiz.question_count || 0 }}</div>
                                <div class="stat-label">Questions</div>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="stat-item text-center">
                                <div class="stat-number">{{ formatDuration(quiz.time_duration) }}</div>
                                <div class="stat-label">Duration</div>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="stat-item text-center">
                                <div class="stat-number">{{ quiz.total_marks || 0 }}</div>
                                <div class="stat-label">Marks</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Quiz Schedule Info -->
                <div class="quiz-schedule mb-3" v-if="quiz.is_scheduled && quiz.date_of_quiz">
                    <div class="schedule-card">
                        <i class="bi bi-calendar-event schedule-icon me-2"></i>
                        <div class="schedule-info">
                            <div class="schedule-date fw-semibold">{{ formatDate(quiz.date_of_quiz) }}</div>
                            <div class="schedule-time text-muted">{{ formatTime(quiz.date_of_quiz) }}</div>
                        </div>
                    </div>
                </div>

                <!-- User Score (if completed) -->
                <div class="user-score mb-3" v-if="quiz.user_score">
                    <div class="score-card">
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="score-label">Your Score:</span>
                            <span class="score-value fw-bold">
                                {{ quiz.user_score.obtained_marks }}/{{ quiz.user_score.total_marks }}
                                ({{ quiz.user_score.percentage }}%)
                            </span>
                        </div>
                        <div class="progress mt-2" style="height: 6px;">
                            <div class="progress-bar" :style="{ width: quiz.user_score.percentage + '%' }"
                                :class="getScoreProgressClass(quiz.user_score.percentage)"></div>
                        </div>
                    </div>
                </div>

                <!-- Action Buttons -->
                <div class="quiz-actions-bottom mt-auto">
                    <button class="btn btn-primary-orange w-100" @click="$emit('preview-quiz', quiz.id)">
                        <i class="bi bi-eye me-2"></i>
                        Preview Quiz
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'AdminQuizCard',
    props: {
        quiz: {
            type: Object,
            required: true
        },
        activeTab: {
            type: String,
            default: ''
        }
    },
    emits: ['edit-quiz', 'delete-quiz', 'preview-quiz'],
    computed: {
        canEdit() {
            // Only allow editing for upcoming and general quizzes
            return this.activeTab === 'upcoming' || this.activeTab === 'general'
        }
    },
    methods: {
        getStatusBadgeClass() {
            if (!this.quiz.is_scheduled) {
                return 'bg-success'
            }

            const now = new Date()
            const quizDate = new Date(this.quiz.date_of_quiz)

            if (quizDate > now) {
                return 'bg-warning'
            } else if (quizDate <= now) {
                // Check if it's still within the duration
                if (this.quiz.time_duration) {
                    const [hours, minutes] = this.quiz.time_duration.split(':').map(Number)
                    const durationMs = (hours * 60 + minutes) * 60 * 1000
                    const endTime = new Date(quizDate.getTime() + durationMs)

                    if (now <= endTime) {
                        return 'bg-danger' // Live
                    }
                }
                return 'bg-secondary' // Ended
            }

            return 'bg-secondary'
        },

        getStatusText() {
            if (!this.quiz.is_scheduled) {
                return 'General'
            }

            const now = new Date()
            const quizDate = new Date(this.quiz.date_of_quiz)

            if (quizDate > now) {
                return 'Upcoming'
            } else if (quizDate <= now) {
                // Check if it's still within the duration
                if (this.quiz.time_duration) {
                    const [hours, minutes] = this.quiz.time_duration.split(':').map(Number)
                    const durationMs = (hours * 60 + minutes) * 60 * 1000
                    const endTime = new Date(quizDate.getTime() + durationMs)

                    if (now <= endTime) {
                        return 'Live'
                    }
                }
                return 'Ended'
            }

            return 'Unknown'
        },

        getScoreProgressClass(percentage) {
            if (percentage >= 80) return 'bg-success'
            if (percentage >= 60) return 'bg-warning'
            return 'bg-danger'
        },

        formatDate(dateString) {
            if (!dateString) return ''
            const date = new Date(dateString)
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            })
        },

        formatTime(dateString) {
            if (!dateString) return ''
            const date = new Date(dateString)
            return date.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit'
            })
        },

        formatDuration(timeString) {
            if (!timeString) return 'N/A'
            const [hours, minutes] = timeString.split(':').map(Number)
            const totalMinutes = hours * 60 + minutes
            if (totalMinutes === 0) return 'N/A'
            if (totalMinutes < 60) {
                return `${totalMinutes} min${totalMinutes !== 1 ? 's' : ''}`
            } else {
                const hrs = Math.floor(totalMinutes / 60)
                const mins = totalMinutes % 60
                if (mins === 0) {
                    return `${hrs} hour${hrs !== 1 ? 's' : ''}`
                } else {
                    return `${hrs}h ${mins}m`
                }
            }
        },

        viewQuizDetails() {
            // TODO: Implement quiz details view
            console.log('View quiz details:', this.quiz.id)
        }
    }
}
</script>

<style scoped>
.admin-quiz-card {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.admin-quiz-card:hover {
    transform: translateY(-4px);
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
    background: rgba(255, 255, 255, 0.95);
}

.quiz-title {
    color: #2c3e50;
    font-size: 1.1rem;
    line-height: 1.4;
    transition: color 0.3s ease;
}

.glass-card:hover .quiz-title {
    color: #f57c00;
}

.quiz-remarks {
    font-size: 0.9rem;
    line-height: 1.4;
}

.quiz-actions {
    display: flex;
    align-items: center;
}

.btn-primary-icon {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    color: white;
    border-radius: 6px;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    transition: all 0.3s ease;
}

.btn-primary-icon:hover {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: scale(1.05);
}

.btn-danger-icon {
    background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
    border: none;
    color: white;
    border-radius: 6px;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    transition: all 0.3s ease;
}

.btn-danger-icon:hover {
    background: linear-gradient(135deg, #c82333 0%, #a71e2a 100%);
    transform: scale(1.05);
}

.stat-item {
    background: rgba(245, 124, 0, 0.05);
    border-radius: 8px;
    padding: 0.75rem 0.5rem;
}

.stat-number {
    font-weight: 700;
    font-size: 1.1rem;
    color: #f57c00;
}

.stat-label {
    font-size: 0.75rem;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.schedule-card {
    display: flex;
    align-items: center;
    background: rgba(13, 110, 253, 0.05);
    border: 1px solid rgba(13, 110, 253, 0.2);
    border-radius: 8px;
    padding: 0.75rem;
}

.schedule-icon {
    color: #0d6efd;
    font-size: 1.2rem;
}

.schedule-date {
    color: #0d6efd;
    font-size: 0.9rem;
}

.schedule-time {
    font-size: 0.8rem;
}

.score-card {
    background: rgba(40, 167, 69, 0.05);
    border: 1px solid rgba(40, 167, 69, 0.2);
    border-radius: 8px;
    padding: 0.75rem;
}

.score-label {
    color: #6c757d;
    font-size: 0.9rem;
}

.score-value {
    color: #28a745;
    font-size: 0.9rem;
}

.btn-primary-orange {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    color: white;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    padding: 0.6rem 1rem;
}

.btn-primary-orange:hover {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(245, 124, 0, 0.3);
}

.btn-outline-secondary {
    border: 2px solid #6c757d;
    color: #6c757d;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
    padding: 0.6rem 1rem;
}

.btn-outline-secondary:hover {
    background: #6c757d;
    color: white;
    transform: translateY(-1px);
}

.progress {
    background: rgba(255, 255, 255, 0.5);
    border-radius: 3px;
}

.progress-bar {
    transition: width 0.3s ease;
    border-radius: 3px;
}
</style>

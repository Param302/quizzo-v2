<template>
    <div class="modal modal-backdrop" style="display: block;" v-if="show" @click.self="$emit('close')">
        <div class="modal-dialog modal-custom modal-dialog-centered">
            <div class="modal-content course-modal" :class="{ 'slide-up': show, 'slide-down': !show }">
                <div class="modal-header border-0">
                    <div class="w-100 d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h4 class="modal-title fw-bold mb-2 course-title-orange">{{ course.name }}</h4>
                            <p class="text-muted mb-0">{{ course.description }}</p>
                        </div>
                        <div class="d-flex gap-2 align-items-center">
                            <button class="btn subscription-btn" :class="isSubscribed ? 'btn-danger' : 'btn-warning'"
                                @click="$emit('subscribe-course', course.id)"
                                :title="isSubscribed ? 'Unsubscribe from all chapters' : 'Subscribe to all chapters'">
                                <i :class="isSubscribed ? 'bi bi-dash-circle me-2' : 'bi bi-plus-circle me-2'"></i>
                                {{ isSubscribed ? 'Unsubscribe All' : 'Subscribe All' }}
                            </button>
                            <button type="button" class="btn-close-custom" @click="$emit('close')">
                                <i class="bi bi-x"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <div class="modal-body">
                    <div class="course-overview mb-4">
                        <div class="row g-3">
                            <div class="col-md-3 col-6">
                                <div class="stat-card text-center">
                                    <i class="bi bi-collection stat-icon"></i>
                                    <div class="stat-number">{{ course.chapters.length }}</div>
                                    <div class="stat-label">Chapters</div>
                                </div>
                            </div>
                            <div class="col-md-3 col-6">
                                <div class="stat-card text-center">
                                    <i class="bi bi-question-circle stat-icon"></i>
                                    <div class="stat-number">{{ totalQuizzes }}</div>
                                    <div class="stat-label">Total Quizzes</div>
                                </div>
                            </div>
                            <div class="col-md-3 col-6">
                                <div class="stat-card text-center">
                                    <i class="bi bi-lightning stat-icon"></i>
                                    <div class="stat-number">{{ liveQuizzes }}</div>
                                    <div class="stat-label">Live Quizzes</div>
                                </div>
                            </div>
                            <div class="col-md-3 col-6">
                                <div class="stat-card text-center">
                                    <i class="bi bi-clock stat-icon"></i>
                                    <div class="stat-number">{{ upcomingQuizzes }}</div>
                                    <div class="stat-label">Upcoming</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="chapters-list">
                        <h5 class="fw-bold mb-3">Chapters</h5>

                        <div class="row g-3">
                            <div v-for="chapter in course.chapters" :key="chapter.id" class="col-lg-6 col-12">
                                <div class="chapter-card">
                                    <div class="chapter-header">
                                        <div class="d-flex justify-content-between align-items-start mb-2">
                                            <h6 class="chapter-title mb-0 flex-grow-1">{{ chapter.name }}</h6>
                                            <button class="btn subscription-btn-small"
                                                :class="isChapterSubscribed(chapter.id) ? 'btn-danger' : 'btn-warning'"
                                                @click="$emit('subscribe-chapter', chapter.id)"
                                                :title="isChapterSubscribed(chapter.id) ? 'Unsubscribe from chapter' : 'Subscribe to chapter'">
                                                <i
                                                    :class="isChapterSubscribed(chapter.id) ? 'bi bi-dash' : 'bi bi-plus'"></i>
                                            </button>
                                        </div>
                                        <p class="chapter-description text-muted mb-2">{{ chapter.description }}</p>
                                    </div>

                                    <div class="chapter-stats mb-3">
                                        <div class="row g-2">
                                            <div class="col-6 col-md-3">
                                                <div class="mini-stat">
                                                    <span class="mini-stat-number">{{ chapter.quiz_counts?.total || 0
                                                    }}</span>
                                                    <span class="mini-stat-label">Quizzes</span>
                                                </div>
                                            </div>
                                            <div class="col-6 col-md-3">
                                                <div class="mini-stat">
                                                    <span class="mini-stat-number">{{ chapter.quiz_counts?.live || 0
                                                    }}</span>
                                                    <span class="mini-stat-label">Live</span>
                                                </div>
                                            </div>
                                            <div class="col-6 col-md-3">
                                                <div class="mini-stat">
                                                    <span class="mini-stat-number">{{ chapter.quiz_counts?.upcoming || 0
                                                    }}</span>
                                                    <span class="mini-stat-label">Upcoming</span>
                                                </div>
                                            </div>
                                            <div class="col-6 col-md-3">
                                                <div class="mini-stat">
                                                    <span class="mini-stat-number">{{ chapter.quiz_counts?.general || 0
                                                    }}</span>
                                                    <span class="mini-stat-label">General</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div v-if="chapter.next_upcoming_quiz" class="upcoming-quiz mb-3">
                                        <div class="upcoming-quiz-card">
                                            <div class="d-flex align-items-start">
                                                <div class="flex-grow-1">
                                                    <div class="fw-semibold mb-1">{{ chapter.next_upcoming_quiz.title }}</div>
                                                    <div class="d-flex align-items-center text-muted small">
                                                        <i class="bi bi-calendar-event upcoming-quiz-icon me-2"></i>
                                                        <span>{{ formatDate(chapter.next_upcoming_quiz.date) }}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="chapter-actions">
                                        <button class="btn btn-primary w-100"
                                            @click="$emit('view-chapter', course.id, chapter.id)">
                                            <i class="bi bi-eye me-2"></i>
                                            View Chapter
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { computed } from 'vue'

export default {
    name: 'CourseModal',
    props: {
        course: {
            type: Object,
            required: true
        },
        show: {
            type: Boolean,
            default: false
        },
        isSubscribed: {
            type: Boolean,
            default: false
        },
        userSubscriptions: {
            type: Array,
            default: () => []
        }
    },
    emits: ['close', 'subscribe-chapter', 'subscribe-course', 'view-chapter'],
    setup(props) {
        const totalQuizzes = computed(() => {
            return props.course.chapters.reduce((total, chapter) => {
                return total + (chapter.quiz_counts?.total || 0)
            }, 0)
        })

        const liveQuizzes = computed(() => {
            return props.course.chapters.reduce((total, chapter) => {
                return total + (chapter.quiz_counts?.live || 0)
            }, 0)
        })

        const upcomingQuizzes = computed(() => {
            return props.course.chapters.reduce((total, chapter) => {
                return total + (chapter.quiz_counts?.upcoming || 0)
            }, 0)
        })

        const isChapterSubscribed = (chapterId) => {
            return props.userSubscriptions.some(sub => sub.chapter_id === chapterId)
        }

        const formatDate = (dateString) => {
            const date = new Date(dateString)
            return date.toLocaleDateString('en-US', {
                weekday: 'short',
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            })
        }

        return {
            totalQuizzes,
            liveQuizzes,
            upcomingQuizzes,
            isChapterSubscribed,
            formatDate
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
    max-width: 80%;
    max-height: 85%;
}

.course-modal {
    border-radius: 20px;
    border: none;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
    background: #ffffff;
    max-height: 85vh;
    overflow-y: auto;
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

.course-title-orange {
    color: #f57c00;
    font-size: 1.5rem;
}

.subscription-btn {
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    padding: 0.5rem 1rem;
}

.subscription-btn.btn-warning {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    color: white;
}

.subscription-btn.btn-danger {
    background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
    border: none;
    color: white;
}

.subscription-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.subscription-btn-small {
    border: none;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    padding: 0;
}

.subscription-btn-small.btn-warning {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    color: white;
}

.subscription-btn-small.btn-danger {
    background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
    color: white;
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

/* Stat Cards */
.stat-card {
    background: rgba(245, 124, 0, 0.05);
    border: 1px solid rgba(245, 124, 0, 0.1);
    border-radius: 16px;
    padding: 1.5rem 1rem;
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(245, 124, 0, 0.1);
}

.stat-icon {
    font-size: 2rem;
    color: #f57c00;
    margin-bottom: 0.5rem;
}

.stat-number {
    font-size: 1.5rem;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 0.25rem;
    display: block;
}

.stat-label {
    font-size: 0.85rem;
    color: #6c757d;
    font-weight: 500;
}

/* Chapter Cards */
.chapter-card {
    background: #ffffff;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(245, 124, 0, 0.1);
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.3s ease;
    height: 100%;
}

.chapter-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(245, 124, 0, 0.15);
    border-color: rgba(245, 124, 0, 0.2);
}

.chapter-card:hover .chapter-title {
    color: #f57c00;
}

.chapter-title {
    color: #2c3e50;
    font-size: 1.1rem;
    font-weight: 600;
    transition: color 0.3s ease;
}

.chapter-description {
    font-size: 0.9rem;
    line-height: 1.4;
}

/* Mini Stats */
.mini-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.mini-stat-number {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f57c00;
    display: block;
}

.mini-stat-label {
    font-size: 0.75rem;
    color: #6c757d;
    font-weight: 500;
}

/* Upcoming Quiz */
.upcoming-quiz-card {
    background: rgba(245, 124, 0, 0.1);
    border: 1px solid rgba(245, 124, 0, 0.2);
    border-radius: 12px;
    padding: 0.75rem 1rem;
    color: #f57c00;
    font-weight: 600;
    font-size: 0.95rem;
    text-decoration: none;
    transition: all 0.3s ease;
    text-align: left;
}

.upcoming-quiz-card:hover {
    background: rgba(245, 124, 0, 0.15);
    color: #e65100;
    text-decoration: none;
    transform: translateY(-1px);
}

.upcoming-quiz-icon {
    color: #f57c00;
    font-size: 1.1rem;
}

/* Buttons */
.btn {
    border-radius: 12px;
    font-weight: 600;
    padding: 0.5rem 1rem;
    transition: all 0.3s ease;
}

.btn-primary {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    box-shadow: 0 2px 8px rgba(245, 124, 0, 0.3);
}

.btn-primary:hover {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(245, 124, 0, 0.4);
}

.btn-lg {
    padding: 0.75rem 1.5rem;
    font-size: 1.1rem;
}

/* Responsive */
@media (max-width: 992px) {
    .modal-custom {
        max-width: 90%;
        max-height: 80%;
    }
}

@media (max-width: 768px) {
    .modal-custom {
        max-width: 95%;
        max-height: 85%;
    }

    .modal-header,
    .modal-body {
        padding: 1.5rem;
    }

    .course-title-orange {
        font-size: 1.2rem;
    }

    .stat-card {
        padding: 1rem 0.5rem;
    }

    .stat-icon {
        font-size: 1.5rem;
    }

    .chapter-card:hover {
        transform: none;
    }

    .stat-card:hover {
        transform: none;
    }
}
</style>

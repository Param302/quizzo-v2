<template>
    <div class="course-card h-100">
        <div class="card glass-card h-100 course-card-inner">
            <div class="card-body d-flex flex-column p-4">
                <div class="course-header mb-3">
                    <div class="d-flex align-items-start justify-content-between mb-2">
                        <h5 class="card-title fw-bold mb-0 course-title">{{ course.name }}</h5>
                        <button class="btn subscription-btn" :class="isSubscribed ? 'btn-danger' : 'btn-warning'"
                            @click="$emit('subscribe-course', course.id)"
                            :title="isSubscribed ? 'Unsubscribe from all chapters' : 'Subscribe to all chapters'">
                            <i :class="isSubscribed ? 'bi bi-dash-circle' : 'bi bi-plus-circle'"></i>
                        </button>
                    </div>
                    <p class="card-text text-muted mb-3">{{ course.description }}</p>
                </div>

                <div class="course-stats mb-3">
                    <div class="row g-2">
                        <div class="col-6">
                            <div class="stat-item">
                                <i class="bi bi-collection stat-icon"></i>
                                <span class="ms-1">{{ course.chapters.length }} Chapters</span>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="stat-item">
                                <i class="bi bi-question-circle stat-icon"></i>
                                <span class="ms-1">{{ totalQuizzes }} Quizzes</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="course-preview mb-3">
                    <div class="chapters-preview">
                        <h6 class="fw-semibold mb-2">Chapters:</h6>
                        <div class="chapter-tags">
                            <span v-for="chapter in course.chapters.slice(0, 3)" :key="chapter.id"
                                class="badge chapter-badge me-1 mb-1">
                                {{ chapter.name }}
                            </span>
                            <span v-if="course.chapters.length > 3" class="badge chapter-badge-more me-1 mb-1">
                                +{{ course.chapters.length - 3 }} more
                            </span>
                        </div>
                    </div>
                </div>

                <div class="mt-auto">
                    <button class="btn-auth-secondary view-details-btn w-100" @click="$emit('view-course', course)">
                        <i class="bi bi-eye me-2"></i>
                        View Details
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'CourseCard',
    props: {
        course: {
            type: Object,
            required: true
        },
        isSubscribed: {
            type: Boolean,
            default: false
        }
    },
    emits: ['view-course', 'subscribe-course'],
    computed: {
        totalQuizzes() {
            return this.course.chapters.reduce((total, chapter) => {
                return total + (chapter.quiz_counts?.total || 0);
            }, 0);
        }
    }
}
</script>

<style scoped>
.course-card {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.course-card:hover {
    transform: translateY(-8px);
}

.course-card-inner {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(245, 124, 0, 0.1);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.course-card-inner:hover {
    box-shadow: 0 12px 40px rgba(245, 124, 0, 0.15);
    border-color: rgba(245, 124, 0, 0.2);
    background: rgba(255, 255, 255, 0.95);
}

.course-card-inner:hover .course-title {
    color: #f57c00;
    transition: color 0.3s ease;
}

.course-title {
    color: #2c3e50;
    font-size: 1.1rem;
    line-height: 1.4;
    transition: color 0.3s ease;
}

.card-text {
    font-size: 0.9rem;
    line-height: 1.5;
}

.stat-item {
    display: flex;
    align-items: center;
    font-size: 0.85rem;
    font-weight: 500;
    color: #6c757d;
}

.stat-item i {
    font-size: 1rem;
    color: #ff8c00 !important;
}

.subscription-btn {
    border: none;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.subscription-btn.btn-warning {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
}

.subscription-btn.btn-danger {
    background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
}

.subscription-btn:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-auth-secondary {
    background: rgba(245, 124, 0, 0.1);
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    color: #f57c00;
    font-weight: 600;
    font-size: 0.95rem;
    text-decoration: none;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn-auth-secondary:hover {
    background: rgba(245, 124, 0, 0.15);
    color: #e65100;
    text-decoration: none;
    transform: translateY(-1px);
}

.chapter-badge {
    background: rgba(245, 124, 0, 0.1);
    color: #f57c00;
    border: 1px solid rgba(245, 124, 0, 0.2);
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-weight: 500;
}

.chapter-badge-more {
    background: rgba(108, 117, 125, 0.1);
    color: #6c757d;
    border: 1px solid rgba(108, 117, 125, 0.2);
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-weight: 500;
}

.chapters-preview h6 {
    color: #495057;
    font-size: 0.9rem;
}

.chapter-tags {
    line-height: 1.8;
}

@media (max-width: 768px) {
    .course-card:hover {
        transform: none;
    }

    .subscription-btn:hover {
        transform: none;
    }

    .view-details-btn:hover {
        transform: none;
    }
}
</style>

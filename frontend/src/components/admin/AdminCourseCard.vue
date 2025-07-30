<template>
    <div class="admin-course-card h-100">
        <div class="card glass-card h-100">
            <div class="card-body d-flex flex-column p-4">
                <!-- Course Header -->
                <div class="course-header mb-3">
                    <div class="d-flex align-items-start justify-content-between mb-2">
                        <h5 class="card-title fw-bold mb-0 course-title">{{ course.name }}</h5>
                        <div class="course-actions">
                            <button type="button" class="btn btn-primary-icon me-2" @click="editCourse"
                                :disabled="loading" title="Edit Course">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button type="button" class="btn btn-danger-icon" @click="deleteCourse"
                                :disabled="deleting || loading" :title="deleting ? 'Deleting...' : 'Delete Course'">
                                <i v-if="deleting" class="bi bi-hourglass-split"></i>
                                <i v-else class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                    <p class="card-text text-muted mb-3">{{ course.description || 'No description provided' }}</p>
                </div>

                <!-- Course Stats -->
                <div class="course-stats mb-3">
                    <div class="row g-2">
                        <div class="col-6">
                            <div class="stat-item">
                                <i class="bi bi-collection stat-icon"></i>
                                <span class="ms-1">{{ course.chapters_count }} Chapter{{ course.chapters_count !== 1 ?
                                    's' : '' }}</span>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="stat-item">
                                <i class="bi bi-question-circle stat-icon"></i>
                                <span class="ms-1">{{ course.total_quizzes || 0 }} Quiz{{ (course.total_quizzes || 0)
                                    !== 1 ? 'es' : '' }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Chapters Preview -->
                <div class="course-preview mb-3" v-if="course.chapters && course.chapters.length > 0">
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

                <!-- No Chapters Message -->
                <div v-else class="no-chapters-message mb-3">
                    <div class="text-center py-3">
                        <i class="bi bi-collection text-muted mb-2 d-block" style="font-size: 2rem;"></i>
                        <small class="text-muted">No chapters yet</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
    name: 'AdminCourseCard',
    props: {
        course: {
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
    emits: ['edit-course', 'delete-course'],
    methods: {
        editCourse() {
            this.$emit('edit-course', this.course.id)
        },
        deleteCourse() {
            this.$emit('delete-course', this.course.id)
        }
    }
})
</script>

<style scoped>
.admin-course-card {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.admin-course-card:hover {
    transform: translateY(-8px);
}

.glass-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(245, 124, 0, 0.1);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
    box-shadow: 0 12px 40px rgba(245, 124, 0, 0.15);
    border-color: rgba(245, 124, 0, 0.2);
    background: rgba(255, 255, 255, 0.95);
}

.glass-card:hover .course-title {
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

.course-actions {
    display: flex;
    align-items: center;
}

.btn-primary-icon {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    color: white !important;
    border-radius: 8px;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(245, 124, 0, 0.2);
    cursor: pointer;
}

.btn-primary-icon:hover {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(245, 124, 0, 0.3);
    color: white !important;
}

.btn-primary-icon:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

.btn-danger-icon {
    background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
    border: none;
    color: white !important;
    border-radius: 8px;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(220, 53, 69, 0.2);
    cursor: pointer;
}

.btn-danger-icon:hover {
    background: linear-gradient(135deg, #c82333 0%, #a71e2a 100%);
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
    color: white !important;
}

.btn-danger-icon:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

.btn-danger-icon:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
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

.stat-item i.text-danger {
    color: #dc3545 !important;
}

.stat-item i.text-warning {
    color: #ffc107 !important;
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

.no-chapters-message {
    background: rgba(108, 117, 125, 0.05);
    border: 1px dashed rgba(108, 117, 125, 0.2);
    border-radius: 12px;
}
</style>

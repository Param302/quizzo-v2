<template>
    <div class="modal modal-backdrop" style="display: block;" v-if="show" @click.self="$emit('close')">
        <div class="modal-dialog modal-custom modal-dialog-centered modal-lg">
            <div class="modal-content course-modal" :class="{ 'slide-up': show, 'slide-down': !show }">
                <div class="modal-header border-0">
                    <div class="w-100 d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h4 class="modal-title fw-bold mb-2 course-title-orange">
                                {{ isAddMode ? 'Add New Course' : 'Edit Course' }}
                            </h4>
                            <p class="text-muted mb-0">
                                {{ isAddMode ? 'Create a new course with chapters' :
                                    'Modify course details and chapters' }}
                            </p>
                        </div>
                        <div class="d-flex gap-2 align-items-center">
                            <button class="btn btn-orange" @click="saveCourse" :disabled="loading || !isFormValid">
                                <i v-if="loading" class="bi bi-hourglass-split me-2"></i>
                                <i v-else class="bi bi-floppy me-2"></i>
                                {{ loading ? 'Saving...' : 'Save' }}
                            </button>
                            <button type="button" class="btn-close-custom" @click="$emit('close')">
                                <i class="bi bi-x"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <div class="modal-body">
                    <!-- Course Details Form -->
                    <!-- Course Name -->
                    <div class="mb-4">
                        <label for="courseName" class="form-label fw-semibold text-dark mb-2">Course Name</label>
                        <div class="input-group-modern">
                            <div class="input-wrapper">
                                <i class="bi bi-book input-icon"></i>
                                <input id="courseName" v-model="formData.name" type="text" class="form-input"
                                    placeholder="Enter course name..." required />
                            </div>
                        </div>
                    </div>

                    <!-- Course Description -->
                    <div class="mb-4">
                        <label for="courseDescription" class="form-label fw-semibold text-dark mb-2">Course
                            Description</label>
                        <div class="input-group-modern">
                            <div class="input-wrapper">
                                <i class="bi bi-textarea-t input-icon"></i>
                                <textarea id="courseDescription" v-model="formData.description" class="form-input"
                                    rows="4" placeholder="Enter course description..." required></textarea>
                            </div>
                        </div>
                    </div> <!-- Chapters Section -->
                    <div class="chapters-section">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="fw-bold mb-0 text-orange">
                                <i class="bi bi-journals me-2"></i>
                                Chapters ({{ formData.chapters.length }})
                            </h5>
                            <button class="btn btn-orange" @click="addChapter">
                                <i class="bi bi-plus-circle me-2"></i>
                                Add Chapter
                            </button>
                        </div>

                        <!-- No Chapters State -->
                        <div v-if="formData.chapters.length === 0" class="empty-chapters text-center py-4">
                            <i class="bi bi-collection text-muted mb-3" style="font-size: 3rem;"></i>
                            <h6 class="text-muted mb-2">No chapters yet</h6>
                            <p class="text-muted mb-3">Add chapters to organize your course content</p>
                            <button class="btn btn-orange" @click="addChapter">
                                <i class="bi bi-plus-circle me-2"></i>
                                Add First Chapter
                            </button>
                        </div>

                        <!-- Chapters List -->
                        <div v-else class="chapters-list">
                            <div v-for="(chapter, index) in formData.chapters" :key="chapter.tempId || chapter.id"
                                class="chapter-item mb-3">
                                <div class="chapter-card">
                                    <div class="chapter-header">
                                        <div class="mb-3">
                                            <!-- Chapter Name Input -->
                                            <div class="mb-3">
                                                <label class="form-label fw-semibold text-dark mb-2">Chapter
                                                    Name</label>
                                                <div class="input-group-modern">
                                                    <div class="input-wrapper">
                                                        <i class="bi bi-journal-text input-icon"></i>
                                                        <input type="text" class="form-input chapter-name-input"
                                                            v-model="chapter.name" placeholder="Enter chapter name..."
                                                            required>
                                                    </div>
                                                </div>
                                            </div>

                                            <!-- Chapter Description Input -->
                                            <div class="mb-3">
                                                <label class="form-label fw-semibold text-dark mb-2">Chapter
                                                    Description</label>
                                                <div class="input-group-modern">
                                                    <div class="input-wrapper">
                                                        <i class="bi bi-textarea-t input-icon"></i>
                                                        <textarea class="form-input chapter-description-input" rows="3"
                                                            v-model="chapter.description"
                                                            placeholder="Enter chapter description..."></textarea>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Chapter Actions -->
                                        <div class="d-flex justify-content-between align-items-center">
                                            <div v-if="chapter.quiz_counts" class="chapter-quiz-count">
                                                <span class="badge bg-orange">
                                                    {{ chapter.quiz_counts.total || 0 }} Quiz{{
                                                        (chapter.quiz_counts.total || 0) !== 1 ? 'es' : '' }}
                                                </span>
                                            </div>
                                            <div v-else class="chapter-quiz-count">
                                                <span class="badge bg-secondary">New Chapter</span>
                                            </div>

                                            <div class="chapter-actions d-flex gap-2">
                                                <router-link
                                                    :to="`/admin/manage/course/${course.id}/chapter/${chapter.id}`"
                                                    class="btn btn-sm btn-orange text-white"
                                                    v-if="!isAddMode && chapter.id">
                                                    <i class="bi bi-pencil me-1"></i>
                                                    Modify
                                                </router-link>
                                                <button class="btn btn-sm btn-danger"
                                                    @click="confirmRemoveChapter(index)" title="Delete Chapter">
                                                    <i class="bi bi-trash"></i>
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
        </div>
    </div>

    <!-- Chapter Delete Confirmation Modal -->
    <DeleteConfirmationModal :show="showDeleteChapterModal" title="Delete Chapter"
        message="You are about to permanently delete this chapter. This will remove all associated quizzes and questions."
        :itemDetails="chapterToDelete" :loading="deletingChapter" @close="closeDeleteChapterModal"
        @confirm="deleteChapter" />
</template>

<script>
import { ref, computed, watch } from 'vue'
import DeleteConfirmationModal from '@/components/DeleteConfirmationModal.vue'

export default {
    name: 'AdminCourseModal',
    components: {
        DeleteConfirmationModal
    },
    props: {
        course: {
            type: Object,
            required: true
        },
        show: {
            type: Boolean,
            default: false
        },
        loading: {
            type: Boolean,
            default: false
        }
    },
    emits: ['close', 'save'],
    setup(props, { emit }) {
        const formData = ref({
            name: '',
            description: '',
            chapters: []
        })

        const showDeleteChapterModal = ref(false)
        const chapterToDelete = ref(null)
        const chapterIndexToDelete = ref(null)
        const deletingChapter = ref(false)

        let nextTempId = 1

        const isAddMode = computed(() => {
            return !props.course.id
        })

        const isFormValid = computed(() => {
            return formData.value.name.trim().length > 0
        })

        const initializeForm = () => {
            if (props.course) {
                formData.value = {
                    name: props.course.name || '',
                    description: props.course.description || '',
                    chapters: props.course.chapters ? JSON.parse(JSON.stringify(props.course.chapters)) : []
                }
            }
        }

        const addChapter = () => {
            formData.value.chapters.push({
                tempId: nextTempId++,
                name: '',
                description: ''
            })
        }

        const removeChapter = (index) => {
            formData.value.chapters.splice(index, 1)
        }

        const confirmRemoveChapter = (index) => {
            const chapter = formData.value.chapters[index]
            chapterToDelete.value = {
                name: chapter.name || 'Untitled Chapter',
                description: chapter.description || 'No description provided'
            }
            chapterIndexToDelete.value = index
            showDeleteChapterModal.value = true
        }

        const closeDeleteChapterModal = () => {
            showDeleteChapterModal.value = false
            chapterToDelete.value = null
            chapterIndexToDelete.value = null
        }

        const deleteChapter = () => {
            if (chapterIndexToDelete.value !== null) {
                deletingChapter.value = true

                // Simulate brief loading for UX consistency
                setTimeout(() => {
                    removeChapter(chapterIndexToDelete.value)
                    closeDeleteChapterModal()
                    deletingChapter.value = false
                }, 300)
            }
        }

        const saveCourse = () => {
            if (!isFormValid.value) return

            const courseData = {
                name: formData.value.name.trim(),
                description: formData.value.description.trim(),
                chapters: formData.value.chapters.map(chapter => ({
                    id: chapter.id || null,
                    name: chapter.name.trim(),
                    description: chapter.description.trim()
                }))
            }

            emit('save', courseData)
        }

        // Watch for course changes to reinitialize form
        watch(() => props.course, () => {
            initializeForm()
        }, { immediate: true })

        return {
            formData,
            isAddMode,
            isFormValid,
            addChapter,
            removeChapter,
            confirmRemoveChapter,
            showDeleteChapterModal,
            chapterToDelete,
            deletingChapter,
            closeDeleteChapterModal,
            deleteChapter,
            saveCourse
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

.slide-up {
    animation: slideUp 0.3s ease-out;
}

.slide-down {
    animation: slideDown 0.3s ease-in;
}

.modal-backdrop {
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(5px);
}

.modal-custom {
    max-width: 800px;
}

.modal-content {
    border-radius: 20px;
    border: none;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
    background: #ffffff;
}

.course-title-orange {
    color: #f57c00;
}

.btn-orange {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    color: white;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    padding: 0.75rem 1.5rem;
}

.btn-orange:hover {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.4);
}

.btn-outline-orange {
    border: 2px solid #f57c00;
    color: #f57c00;
    background: transparent;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.btn-outline-orange:hover {
    background: #f57c00;
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.btn-close-custom {
    background: rgba(220, 53, 69, 0.1);
    border: 1px solid rgba(220, 53, 69, 0.2);
    color: #dc3545;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    transition: all 0.3s ease;
}

.btn-close-custom:hover {
    background: rgba(220, 53, 69, 0.2);
    transform: scale(1.1);
}

.form-control {
    border: 2px solid rgba(0, 0, 0, 0.1);
    border-radius: 12px;
    padding: 0.75rem 1rem;
    transition: all 0.3s ease;
}

.form-control:focus {
    border-color: #f57c00;
    box-shadow: 0 0 0 0.25rem rgba(245, 124, 0, 0.15);
}

.empty-chapters {
    background: rgba(245, 124, 0, 0.05);
    border: 2px dashed rgba(245, 124, 0, 0.2);
    border-radius: 16px;
}

.chapter-card {
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 16px;
    padding: 1rem;
    transition: all 0.3s ease;
}

.chapter-card:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    border-color: rgba(245, 124, 0, 0.3);
}

.chapter-actions {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.mini-stat {
    text-align: center;
    padding: 0.5rem;
    background: rgba(245, 124, 0, 0.05);
    border-radius: 8px;
}

.mini-stat-number {
    display: block;
    font-weight: 700;
    font-size: 1.1rem;
    color: #f57c00;
}

.mini-stat-label {
    font-size: 0.75rem;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.modify-chapter-action .btn {
    border-radius: 8px;
    font-size: 0.85rem;
    padding: 0.5rem 1rem;
}

/* Auth-style Input Fields */
.input-group-modern {
    position: relative;
}

.input-wrapper {
    position: relative;
    display: flex;
    align-items: flex-start;
}

.form-input {
    width: 100%;
    padding: 0.875rem 1rem 0.875rem 3rem;
    border: none;
    background: rgba(245, 124, 0, 0.05);
    border-radius: 12px;
    font-size: 0.95rem;
    transition: all 0.3s ease;
    outline: none;
    resize: vertical;
}

.form-input:focus {
    background: rgba(245, 124, 0, 0.1);
    box-shadow: 0 0 0 3px rgba(245, 124, 0, 0.1);
    transform: translateY(-1px);
}

.form-input::placeholder {
    color: #adb5bd;
    font-weight: 400;
}

.input-icon {
    position: absolute;
    left: 1rem;
    top: 0.875rem;
    color: #f57c00;
    font-size: 1.1rem;
    z-index: 2;
}

/* Chapter specific styles */
.chapter-quiz-count .badge {
    font-size: 0.8rem;
    padding: 0.5rem 0.75rem;
}

.chapter-actions .btn {
    height: 36px;
    display: flex;
    align-items: center;
    padding: 0.5rem 1rem;
}

.chapter-actions .btn-orange {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    color: white !important;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
    text-decoration: none;
}

.chapter-actions .btn-orange:hover {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
    color: white !important;
    text-decoration: none;
}

.bg-orange {
    background-color: #f57c00 !important;
    color: white;
}

.btn-orange {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    color: white;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.btn-orange:hover {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
    color: white;
}

@media (max-width: 768px) {
    .modal-custom {
        max-width: 95%;
        margin: 1rem;
    }

    .chapter-actions .btn {
        font-size: 0.8rem;
        padding: 0.5rem 1rem;
    }
}
</style>

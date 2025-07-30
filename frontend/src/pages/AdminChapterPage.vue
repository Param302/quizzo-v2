<template>
    <div class="admin-chapter-page">
        <!-- Loading State -->
        <div v-if="loading" class="loading-section">
            <div class="text-center py-5">
                <div class="spinner-border text-orange mb-3" role="status" style="width: 3rem; height: 3rem;">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h5 class="text-muted">Loading chapter data...</h5>
            </div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="error-section">
            <div class="text-center py-5">
                <i class="bi bi-exclamation-triangle text-danger mb-3" style="font-size: 4rem;"></i>
                <h4 class="text-danger mb-2">Error Loading Chapter</h4>
                <p class="text-muted">{{ error }}</p>
                <button class="btn btn-orange" @click="fetchChapterData">
                    <i class="bi bi-arrow-clockwise me-2"></i>
                    Try Again
                </button>
            </div>
        </div>

        <!-- Main Content -->
        <div v-else-if="chapterData">
            <!-- Header Section -->
            <section class="chapter-header py-4 bg-blur">
                <div class="container">
                    <div class="row">
                        <div class="col-12">
                            <!-- Back to Course Link -->
                            <div class="mb-3">
                                <a href="#" class="btn-back-link" @click.prevent="goBackToCourse">
                                    <i class="bi bi-arrow-left me-2"></i>
                                    Back to Course
                                </a>
                            </div>

                            <!-- Header Content -->
                            <div class="row align-items-center">
                                <div class="col-md-8">
                                    <h1 class="display-6 fw-bold mb-2 text-orange">Quiz Management</h1>
                                    <h3 class="chapter-name mb-2">{{ chapterData.chapter.name }}</h3>
                                    <p v-if="chapterData.chapter.description"
                                        class="lead fw-medium mb-3 chapter-description">{{
                                            chapterData.chapter.description }}</p>
                                    <div class="course-info">
                                        <span class="badge course-badge">
                                            <i class="bi bi-book me-1"></i>
                                            {{ chapterData.course.name }}
                                        </span>
                                    </div>
                                </div>
                                <div class="col-md-4 text-md-end mt-3 mt-md-0">
                                    <div class="quiz-count-badge mb-3">
                                        <i class="bi bi-patch-question me-2"></i>
                                        <span class="fw-bold">{{ totalQuizzes }}</span>
                                        <span> Quiz{{ totalQuizzes !== 1 ? 'zes' : '' }}</span>
                                    </div>
                                    <div class="text-center text-md-end">
                                        <button class="btn btn-orange" @click="showAddQuizModal = true">
                                            <i class="bi bi-plus-circle me-2"></i>
                                            Add New Quiz
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Quizzes Section -->
            <section class="quizzes-section py-5">
                <div class="container">
                    <!-- Quiz Tabs -->
                    <div class="quiz-tabs-container mb-4">
                        <ul class="nav nav-pills quiz-tabs w-100">
                            <li class="nav-item flex-fill">
                                <button class="nav-link live-tab w-100" :class="{ active: activeTab === 'live' }"
                                    @click="activeTab = 'live'">
                                    <i class="bi bi-broadcast me-2"></i>
                                    <span>Live</span>
                                    <span v-if="chapterData.quizzes.live.length" class="badge quiz-tab-badge ms-2">
                                        {{ chapterData.quizzes.live.length }}
                                    </span>
                                </button>
                            </li>
                            <li class="nav-item flex-fill">
                                <button class="nav-link upcoming-tab w-100"
                                    :class="{ active: activeTab === 'upcoming' }" @click="activeTab = 'upcoming'">
                                    <i class="bi bi-clock me-2"></i>
                                    <span>Upcoming</span>
                                    <span v-if="chapterData.quizzes.upcoming.length" class="badge quiz-tab-badge ms-2">
                                        {{ chapterData.quizzes.upcoming.length }}
                                    </span>
                                </button>
                            </li>
                            <li class="nav-item flex-fill">
                                <button class="nav-link general-tab w-100" :class="{ active: activeTab === 'general' }"
                                    @click="activeTab = 'general'">
                                    <i class="bi bi-infinity me-2"></i>
                                    <span>General</span>
                                    <span v-if="chapterData.quizzes.general.length" class="badge quiz-tab-badge ms-2">
                                        {{ chapterData.quizzes.general.length }}
                                    </span>
                                </button>
                            </li>
                            <li class="nav-item flex-fill">
                                <button class="nav-link ended-tab w-100" :class="{ active: activeTab === 'ended' }"
                                    @click="activeTab = 'ended'">
                                    <i class="bi bi-calendar-x me-2"></i>
                                    <span>Ended</span>
                                    <span v-if="chapterData.quizzes.ended.length" class="badge quiz-tab-badge ms-2">
                                        {{ chapterData.quizzes.ended.length }}
                                    </span>
                                </button>
                            </li>
                        </ul>
                    </div>

                    <!-- Tab Content -->
                    <div class="quiz-tab-content">
                        <div v-if="activeQuizzes.length === 0" class="empty-state text-center py-5">
                            <i class="bi bi-inbox empty-icon mb-3"></i>
                            <h4 class="text-muted">No {{ activeTab }} quizzes</h4>
                            <p class="text-muted">{{ getEmptyMessage() }}</p>
                            <button class="btn btn-orange" @click="showAddQuizModal = true">
                                <i class="bi bi-plus-circle me-2"></i>
                                Add Quiz
                            </button>
                        </div>

                        <div v-else class="row g-4">
                            <div v-for="quiz in activeQuizzes" :key="quiz.id" class="col-lg-4 col-md-6">
                                <AdminQuizCard :quiz="quiz" :activeTab="activeTab" @edit-quiz="editQuiz"
                                    @delete-quiz="confirmDeleteQuiz" @preview-quiz="previewQuiz" />
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>

        <!-- Quiz Modal -->
        <AdminQuizModal :show="showAddQuizModal || showEditQuizModal" :quiz="currentQuiz" :chapterId="chapterId"
            :loading="savingQuiz" @close="closeQuizModal" @save="saveQuiz" />

        <!-- Delete Confirmation Modal -->
        <DeleteConfirmationModal :show="showDeleteModal" title="Delete Quiz"
            message="You are about to permanently delete this quiz. This will remove all associated questions and submissions."
            :itemDetails="quizToDelete" :loading="deletingQuizId" @close="showDeleteModal = false"
            @confirm="deleteQuiz" />

        <!-- Toast Notifications -->
        <Toast v-if="toast.show" :message="toast.message" :variant="toast.type" @close="toast.show = false" />
    </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AdminQuizCard from '@/components/admin/AdminQuizCard.vue'
import AdminQuizModal from '@/components/admin/AdminQuizModal.vue'
import DeleteConfirmationModal from '@/components/DeleteConfirmationModal.vue'
import Toast from '@/components/Toast.vue'
import axios from 'axios'

export default {
    name: 'AdminChapterPage',
    components: {
        AdminQuizCard,
        AdminQuizModal,
        DeleteConfirmationModal,
        Toast
    },
    setup() {
        const route = useRoute()
        const router = useRouter()

        const chapterData = ref(null)
        const loading = ref(true)
        const error = ref(null)
        const activeTab = ref('live')
        const showAddQuizModal = ref(false)
        const showEditQuizModal = ref(false)
        const showDeleteModal = ref(false)
        const quizToDelete = ref(null)
        const deletingQuizId = ref(null)
        const currentQuiz = ref({})
        const savingQuiz = ref(false)

        const toast = ref({
            show: false,
            message: '',
            type: 'success'
        })

        const courseId = computed(() => parseInt(route.params.courseId))
        const chapterId = computed(() => parseInt(route.params.chapterId))

        const totalQuizzes = computed(() => {
            if (!chapterData.value) return 0
            return chapterData.value.quizzes.live.length +
                chapterData.value.quizzes.upcoming.length +
                chapterData.value.quizzes.general.length +
                chapterData.value.quizzes.ended.length
        })

        const activeQuizzes = computed(() => {
            if (!chapterData.value) return []
            return chapterData.value.quizzes[activeTab.value] || []
        })

        const fetchChapterData = async () => {
            try {
                loading.value = true
                error.value = null

                // Use the public endpoint to get chapter quizzes for now
                // TODO: Create admin-specific endpoint if needed
                const response = await axios.get(`/public/courses/${courseId.value}/chapters/${chapterId.value}/quizzes`)
                chapterData.value = response.data
            } catch (err) {
                console.error('Error fetching chapter data:', err)
                error.value = err.response?.data?.message || 'Failed to load chapter data'
            } finally {
                loading.value = false
            }
        }

        const editQuiz = async (quizId) => {
            try {
                // Fetch quiz details with questions
                const response = await axios.get(`/admin/quizzes/${quizId}`)
                currentQuiz.value = response.data.quiz
                showEditQuizModal.value = true
            } catch (error) {
                console.error('Error fetching quiz details:', error)
                showToast(error.response?.data?.message || 'Failed to load quiz details', 'error')
            }
        }

        const previewQuiz = (quizId) => {
            router.push(`/quiz/${quizId}`)
        }

        const closeQuizModal = () => {
            showAddQuizModal.value = false
            showEditQuizModal.value = false
            currentQuiz.value = {}
        }

        const saveQuiz = async (quizData) => {
            try {
                savingQuiz.value = true

                if (showEditQuizModal.value) {
                    // Update existing quiz
                    const response = await axios.put(`/admin/quizzes/${currentQuiz.value.id}`, quizData)
                    showToast('Quiz updated successfully', 'success')
                } else {
                    // Create new quiz
                    const response = await axios.post('/admin/quizzes', {
                        ...quizData,
                        chapter_id: chapterId.value
                    })
                    showToast('Quiz created successfully', 'success')
                }

                // Refresh chapter data
                await fetchChapterData()
                closeQuizModal()
            } catch (error) {
                console.error('Error saving quiz:', error)
                showToast(error.response?.data?.message || 'Failed to save quiz', 'error')
            } finally {
                savingQuiz.value = false
            }
        }

        const confirmDeleteQuiz = (quizId) => {
            const quiz = activeQuizzes.value.find(q => q.id === quizId)
            if (!quiz) return

            quizToDelete.value = quiz
            showDeleteModal.value = true
        }

        const deleteQuiz = async () => {
            if (!quizToDelete.value) return

            deletingQuizId.value = quizToDelete.value.id
            try {
                const response = await axios.delete(`/admin/quizzes/${quizToDelete.value.id}`)

                // Remove quiz from local data
                Object.keys(chapterData.value.quizzes).forEach(tabKey => {
                    chapterData.value.quizzes[tabKey] = chapterData.value.quizzes[tabKey].filter(
                        quiz => quiz.id !== quizToDelete.value.id
                    )
                })

                showToast(response.data.message, 'success')
                showDeleteModal.value = false
                quizToDelete.value = null
            } catch (error) {
                console.error('Error deleting quiz:', error)
                showToast(error.response?.data?.message || 'Failed to delete quiz', 'error')
            } finally {
                deletingQuizId.value = null
            }
        }

        const goBackToCourse = () => {
            // TODO: Navigate back to course edit modal or course management page
            router.push('/admin/manage/course')
        }

        const getEmptyMessage = () => {
            switch (activeTab.value) {
                case 'live':
                    return 'No quizzes are currently live.'
                case 'upcoming':
                    return 'No upcoming quizzes scheduled.'
                case 'general':
                    return 'No general quizzes available.'
                case 'ended':
                    return 'No quizzes have ended recently.'
                default:
                    return 'No quizzes available.'
            }
        }

        const showToast = (message, type = 'success') => {
            toast.value = { show: true, message, type }
            setTimeout(() => {
                toast.value.show = false
            }, 5000)
        }

        // Watch for route changes to refetch data
        watch(() => [courseId.value, chapterId.value], () => {
            fetchChapterData()
        })

        onMounted(() => {
            fetchChapterData()
        })

        return {
            chapterData,
            loading,
            error,
            activeTab,
            showAddQuizModal,
            showEditQuizModal,
            showDeleteModal,
            quizToDelete,
            deletingQuizId,
            currentQuiz,
            savingQuiz,
            totalQuizzes,
            activeQuizzes,
            toast,
            fetchChapterData,
            editQuiz,
            previewQuiz,
            closeQuizModal,
            saveQuiz,
            confirmDeleteQuiz,
            deleteQuiz,
            goBackToCourse,
            getEmptyMessage,
            showToast
        }
    }
}
</script>

<style scoped>
.admin-chapter-page {
    min-height: 100vh;
    background: linear-gradient(135deg, rgba(245, 124, 0, 0.05) 0%, rgba(245, 124, 0, 0.02) 100%);
}

.chapter-header {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(245, 124, 0, 0.1);
}

.course-badge {
    background: rgba(245, 124, 0, 0.1);
    color: #f57c00;
    border: 1px solid rgba(245, 124, 0, 0.2);
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-weight: 600;
    font-size: 0.9rem;
}

.text-orange {
    color: #f57c00 !important;
}

.btn-back-link {
    color: #f57c00;
    text-decoration: none;
    font-weight: 600;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    transition: all 0.3s ease;
    background: rgba(245, 124, 0, 0.1);
    border: 1px solid rgba(245, 124, 0, 0.2);
    display: inline-block;
}

.btn-back-link:hover {
    background: rgba(245, 124, 0, 0.15);
    color: #e65100;
    text-decoration: none;
    transform: translateX(-2px);
}

.chapter-name {
    font-size: 1.5rem;
    color: #495057;
    font-weight: 600;
}

.chapter-description {
    color: #6c757d;
    font-size: 1rem;
    margin-bottom: 0;
}

.quiz-count-badge {
    background: linear-gradient(135deg, rgba(245, 124, 0, 0.1) 0%, rgba(245, 124, 0, 0.05) 100%);
    border: 2px solid rgba(245, 124, 0, 0.2);
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    color: #f57c00;
    font-size: 1.1rem;
    display: inline-flex;
    align-items: center;
    transition: all 0.3s ease;
}

.quiz-count-badge:hover {
    background: linear-gradient(135deg, rgba(245, 124, 0, 0.15) 0%, rgba(245, 124, 0, 0.08) 100%);
    border-color: rgba(245, 124, 0, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.2);
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
    padding: 0.75rem 1.5rem;
}

.btn-outline-orange:hover {
    background: #f57c00;
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.quiz-tabs-container {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 1rem;
    box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
}

.quiz-tabs {
    border-bottom: none;
}

.quiz-tabs .nav-link {
    border: none;
    background: transparent;
    color: #6c757d;
    border-radius: 15px;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    margin: 0 0.25rem;
    transition: all 0.3s ease;
    position: relative;
}

.quiz-tabs .nav-link:hover {
    background: rgba(245, 124, 0, 0.1);
    color: #f57c00;
}

.quiz-tabs .nav-link.active {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    color: white !important;
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.quiz-tab-badge {
    background: rgba(255, 255, 255, 0.3);
    color: inherit;
    border-radius: 10px;
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
}

.quiz-tabs .nav-link.active .quiz-tab-badge {
    background: rgba(255, 255, 255, 0.3);
    color: white;
}

.empty-state {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    margin: 2rem auto;
    max-width: 500px;
}

.empty-icon {
    font-size: 4rem;
    color: #dee2e6;
}

.loading-section,
.error-section {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    margin: 2rem auto;
    max-width: 500px;
}

.modal-backdrop {
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(5px);
}

.modal-content {
    border-radius: 20px;
    border: none;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.bg-blur {
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(10px);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .chapter-header .display-6 {
        font-size: 1.75rem;
    }

    .chapter-name {
        font-size: 1.25rem;
    }

    .quiz-tabs .nav-link {
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
    }

    .course-badge {
        font-size: 0.8rem;
        padding: 0.4rem 0.8rem;
    }

    .btn-outline-orange {
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
    }
}

@media (max-width: 576px) {
    .chapter-header .d-flex {
        flex-direction: column;
        align-items: stretch !important;
    }

    .chapter-header .text-center {
        text-align: left !important;
        margin-bottom: 1rem;
        margin-top: 1rem;
    }

    .chapter-name {
        font-size: 1.1rem;
    }

    .quiz-tabs {
        flex-direction: column;
        gap: 0.5rem;
    }

    .quiz-tabs .nav-link {
        margin: 0;
        text-align: center;
    }
}
</style>

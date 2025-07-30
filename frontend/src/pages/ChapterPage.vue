<template>
    <div class="chapter-page">
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger mx-3 mt-3">
            {{ error }}
        </div>

        <!-- Chapter Content -->
        <div v-else-if="chapterData" class="chapter-content">
            <!-- Header Section -->
            <section class="chapter-header py-4 bg-blur">
                <div class="container">
                    <nav aria-label="breadcrumb" class="mb-3">
                        <ol class="breadcrumb">
                            <li class="breadcrumb-item">
                                <router-link to="/courses" class="text-decoration-none">Courses</router-link>
                            </li>
                            <li class="breadcrumb-item active">{{ chapterData.course.name }}</li>
                            <li class="breadcrumb-item active">{{ chapterData.chapter.name }}</li>
                        </ol>
                    </nav>

                    <div class="row align-items-center">
                        <div class="col-lg-8">
                            <h1 class="display-6 fw-bold mb-2">{{ chapterData.chapter.name }}</h1>
                            <p class="lead text-muted mb-3">{{ chapterData.chapter.description }}</p>
                            <div class="course-info">
                                <span class="badge course-badge me-2">
                                    <i class="bi bi-book me-1"></i>
                                    {{ chapterData.course.name }}
                                </span>
                                <span class="badge quiz-count-badge">
                                    <i class="bi bi-question-circle me-1"></i>
                                    {{ totalQuizzes }} Quizzes
                                </span>
                            </div>
                        </div>
                        <div class="col-lg-4 text-lg-end mt-3 mt-lg-0">
                            <button class="btn subscription-btn" :class="isSubscribed ? 'btn-danger' : 'btn-warning'"
                                @click="toggleSubscription" v-if="authStore.isAuthenticated">
                                <i :class="isSubscribed ? 'bi bi-dash-circle me-1' : 'bi bi-plus-circle me-1'"></i>
                                {{ isSubscribed ? 'Unsubscribe' : 'Subscribe' }}
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Quiz Tabs Section -->
            <section class="quiz-tabs-section py-4">
                <div class="container">
                    <!-- Tab Navigation -->
                    <div class="quiz-tabs-nav mb-4">
                        <ul class="nav nav-pills nav-fill quiz-nav">
                            <li class="nav-item">
                                <button class="nav-link live-tab" :class="{ active: activeTab === 'live' }"
                                    @click="activeTab = 'live'">
                                    <i class="bi bi-broadcast me-2"></i>
                                    <span>Live</span>
                                    <span v-if="chapterData.quizzes.live.length" class="badge quiz-tab-badge ms-2">
                                        {{ chapterData.quizzes.live.length }}
                                    </span>
                                </button>
                            </li>
                            <li class="nav-item">
                                <button class="nav-link upcoming-tab" :class="{ active: activeTab === 'upcoming' }"
                                    @click="activeTab = 'upcoming'">
                                    <i class="bi bi-clock me-2"></i>
                                    <span>Upcoming</span>
                                    <span v-if="chapterData.quizzes.upcoming.length" class="badge quiz-tab-badge ms-2">
                                        {{ chapterData.quizzes.upcoming.length }}
                                    </span>
                                </button>
                            </li>
                            <li class="nav-item">
                                <button class="nav-link general-tab" :class="{ active: activeTab === 'general' }"
                                    @click="activeTab = 'general'">
                                    <i class="bi bi-infinity me-2"></i>
                                    <span>Available</span>
                                    <span v-if="chapterData.quizzes.general.length" class="badge quiz-tab-badge ms-2">
                                        {{ chapterData.quizzes.general.length }}
                                    </span>
                                </button>
                            </li>
                            <li class="nav-item">
                                <button class="nav-link ended-tab" :class="{ active: activeTab === 'ended' }"
                                    @click="activeTab = 'ended'">
                                    <i class="bi bi-calendar-x me-2"></i>
                                    <span>Ended</span>
                                    <span v-if="chapterData.quizzes.ended.length" class="badge quiz-tab-badge ms-2">
                                        {{ chapterData.quizzes.ended.length }}
                                    </span>
                                </button>
                            </li>
                            <li class="nav-item">
                                <button class="nav-link completed-tab" :class="{ active: activeTab === 'completed' }"
                                    @click="activeTab = 'completed'">
                                    <i class="bi bi-check-circle me-2"></i>
                                    <span>Completed</span>
                                    <span v-if="chapterData.quizzes.completed.length" class="badge quiz-tab-badge ms-2">
                                        {{ chapterData.quizzes.completed.length }}
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
                        </div>

                        <div v-else class="row g-4">
                            <div v-for="quiz in activeQuizzes" :key="quiz.id" class="col-lg-6 col-xl-4">
                                <QuizCard :quiz="quiz" :tab-type="activeTab" @start-quiz="startQuiz"
                                    @view-details="viewQuizDetails" @download-certificate="downloadCertificate" />
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>

        <!-- Toast Notifications -->
        <!-- Toast Notifications -->
        <Toast v-if="toast.show" :message="toast.message" :variant="toast.type" @close="toast.show = false" />
    </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import QuizCard from '@/components/QuizCard.vue'
import Toast from '@/components/Toast.vue'
import axios from 'axios'

export default {
    name: 'ChapterPage',
    components: {
        QuizCard,
        Toast
    },
    setup() {
        const route = useRoute()
        const router = useRouter()
        const authStore = useAuthStore()

        const chapterData = ref(null)
        const loading = ref(true)
        const error = ref(null)
        const activeTab = ref('live')
        const userSubscriptions = ref([])

        const toast = ref({
            show: false,
            message: '',
            type: 'success'
        })

        const courseId = computed(() => parseInt(route.params.courseId))
        const chapterId = computed(() => parseInt(route.params.chapterId))

        const totalQuizzes = computed(() => {
            if (!chapterData.value) return 0
            return Object.values(chapterData.value.quizzes).reduce((total, quizArray) => {
                return total + quizArray.length
            }, 0) - (chapterData.value.quizzes.completed?.length || 0) // Don't double count completed
        })

        const activeQuizzes = computed(() => {
            if (!chapterData.value) return []
            return chapterData.value.quizzes[activeTab.value] || []
        })

        const isSubscribed = computed(() => {
            return userSubscriptions.value.some(sub => sub.chapter_id === chapterId.value)
        })

        const fetchChapterData = async () => {
            try {
                loading.value = true
                error.value = null

                let endpoint
                if (authStore.isAuthenticated) {
                    endpoint = `/quiz/courses/${courseId.value}/chapters/${chapterId.value}`
                } else {
                    endpoint = `/public/courses/${courseId.value}/chapters/${chapterId.value}/quizzes`
                }

                const response = await axios.get(endpoint)
                chapterData.value = response.data

                // Fetch user subscriptions if authenticated
                if (authStore.isAuthenticated) {
                    await fetchUserSubscriptions()
                }
            } catch (err) {
                console.error('Error fetching chapter data:', err)
                error.value = err.response?.data?.message || 'Failed to load chapter data'
            } finally {
                loading.value = false
            }
        }

        const fetchUserSubscriptions = async () => {
            try {
                const response = await axios.get('/user/subscriptions')
                userSubscriptions.value = response.data.subscriptions
            } catch (error) {
                console.error('Error fetching subscriptions:', error)
            }
        }

        const toggleSubscription = async () => {
            if (!authStore.isAuthenticated) {
                router.push('/login')
                return
            }

            try {
                if (isSubscribed.value) {
                    // Unsubscribe
                    await axios.delete(`/user/subscriptions/${chapterId.value}`)
                    showToast('Successfully unsubscribed from chapter!', 'success')
                } else {
                    // Subscribe
                    await axios.post('/user/subscriptions', { chapter_id: chapterId.value })
                    showToast('Successfully subscribed to chapter!', 'success')
                }

                await fetchUserSubscriptions()
                // Refresh data to show updated quiz access
                fetchChapterData()
            } catch (error) {
                const message = error.response?.data?.message || 'Failed to update subscription'
                showToast(message, 'error')
            }
        }

        const startQuiz = (quizId) => {
            if (!authStore.isAuthenticated) {
                router.push('/login')
                return
            }
            router.push(`/quiz/${quizId}`)
        }

        const viewQuizDetails = (quizId) => {
            if (!authStore.isAuthenticated) {
                router.push('/login')
                return
            }
            router.push(`/quiz/${quizId}/result`)
        }

        const downloadCertificate = async (quizId) => {
            if (!authStore.isAuthenticated) {
                router.push('/login')
                return
            }

            try {
                const response = await axios.get(`/user/quiz/${quizId}/certificate`, {
                    responseType: 'blob'
                })

                const url = window.URL.createObjectURL(new Blob([response.data]))
                const link = document.createElement('a')
                link.href = url
                link.setAttribute('download', `quiz-${quizId}-certificate.pdf`)
                document.body.appendChild(link)
                link.click()
                link.remove()
                window.URL.revokeObjectURL(url)

                showToast('Certificate downloaded successfully!', 'success')
            } catch (error) {
                const message = error.response?.data?.message || 'Failed to download certificate'
                showToast(message, 'error')
            }
        }

        const getEmptyMessage = () => {
            switch (activeTab.value) {
                case 'live':
                    return 'No quizzes are currently live. Check back later!'
                case 'upcoming':
                    return 'No upcoming quizzes scheduled. Subscribe to get notified!'
                case 'general':
                    return 'No general quizzes available at the moment.'
                case 'ended':
                    return 'No quizzes have ended recently.'
                case 'completed':
                    return 'You haven\'t completed any quizzes in this chapter yet.'
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
            totalQuizzes,
            activeQuizzes,
            isSubscribed,
            toast,
            authStore,
            toggleSubscription,
            startQuiz,
            viewQuizDetails,
            downloadCertificate,
            getEmptyMessage
        }
    }
}
</script>

<style scoped>
.chapter-page {
    min-height: 100vh;
    background: linear-gradient(135deg, rgba(245, 124, 0, 0.05) 0%, rgba(245, 124, 0, 0.02) 100%);
}

.chapter-header {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(245, 124, 0, 0.1);
}

.breadcrumb {
    background: transparent;
    margin-bottom: 0;
}

.breadcrumb-item a {
    color: #f57c00;
}

.breadcrumb-item.active {
    color: #6c757d;
}

.course-badge {
    background: rgba(245, 124, 0, 0.1);
    color: #f57c00;
    border: 1px solid rgba(245, 124, 0, 0.2);
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-size: 0.9rem;
}

.quiz-count-badge {
    background: rgba(40, 167, 69, 0.1);
    color: #28a745;
    border: 1px solid rgba(40, 167, 69, 0.2);
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-size: 0.9rem;
}

.quiz-tabs-nav {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 0.5rem;
    box-shadow: 0 4px 20px rgba(245, 124, 0, 0.1);
}

.quiz-nav .nav-link {
    border-radius: 15px;
    border: none;
    background: transparent;
    color: #6c757d;
    font-weight: 600;
    padding: 1rem 1.5rem;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.25rem;
}

.quiz-nav .nav-link:hover {
    background: rgba(245, 124, 0, 0.1);
    color: #f57c00;
    transform: translateY(-1px);
}

.quiz-nav .nav-link.active {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    color: white !important;
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

/* Tab-specific icon colors */
.live-tab i {
    color: #dc3545;
}

.upcoming-tab i {
    color: #f57c00;
}

.general-tab i {
    color: #28a745;
}

.ended-tab i {
    color: #6c757d;
}

.completed-tab i {
    color: #28a745;
}

/* Active tab icons should be white */
.quiz-nav .nav-link.active i {
    color: white !important;
}

.quiz-tab-badge {
    background: rgba(255, 255, 255, 0.2);
    color: inherit;
    font-size: 0.7rem;
    padding: 0.2rem 0.5rem;
    border-radius: 10px;
}

.quiz-nav .nav-link.active .quiz-tab-badge {
    background: rgba(255, 255, 255, 0.3);
    color: white;
}

.empty-state {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    border: 1px solid rgba(245, 124, 0, 0.1);
    padding: 3rem;
}

.empty-icon {
    font-size: 3rem;
    color: #dee2e6;
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

.btn-primary {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    border-radius: 15px;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
    transition: all 0.3s ease;
}

.btn-primary:hover {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(245, 124, 0, 0.4);
}

.bg-blur {
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(10px);
}

@media (max-width: 768px) {
    .quiz-nav .nav-link {
        padding: 0.75rem 1rem;
        font-size: 0.9rem;
    }

    .quiz-nav .nav-link i {
        font-size: 0.9rem;
    }

    .display-6 {
        font-size: 1.75rem;
    }
}

@media (max-width: 576px) {
    .quiz-nav .nav-link span {
        display: none;
    }

    .quiz-nav .nav-link i {
        margin: 0 !important;
    }

    .quiz-nav .nav-link {
        padding: 0.75rem 0.5rem;
    }
}
</style>

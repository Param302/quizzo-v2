<template>
    <div class="courses-page">
        <!-- Hero Section with Search -->
        <section class="hero-section py-5 bg-blur">
            <div class="container">
                <div class="row align-items-center justify-content-center min-vh-50">
                    <div class="col-lg-8 text-center">
                        <h1 class="display-4 fw-bold mb-4 hero-title">
                            Discover Your Next
                            <span class="text-gradient">Quiz Challenge</span>
                        </h1>
                        <p class="lead mb-5 text fw-medium">
                            Explore courses, subscribe to chapters, and test your knowledge with interactive quizzes.
                        </p>

                        <!-- Search Bar -->
                        <div class="search-container mx-auto mb-4">
                            <div class="search-wrapper position-relative">
                                <i class="bi bi-search search-icon"></i>
                                <input type="text" class="form-control search-input"
                                    placeholder="Search courses, topics, quizzes..." v-model="searchQuery"
                                    @input="handleSearch">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <!-- Courses Section -->
        <section class="courses-section py-5" v-else>
            <div class="container">
                <div v-if="filteredCourses.length === 0" class="text-center py-5">
                    <div class="empty-state">
                        <i class="bi bi-search fs-1 text-muted mb-3"></i>
                        <h4 class="text-muted">No courses found</h4>
                        <p class="text-muted">Try adjusting your search criteria</p>
                    </div>
                </div>

                <div v-else class="row g-4">
                    <div v-for="course in filteredCourses" :key="course.id" class="col-lg-4 col-md-6">
                        <CourseCard :course="course" :is-subscribed="isUserSubscribedToAllChapters(course.id)"
                            @view-course="openCourseModal" @subscribe-course="subscribeToCourse" />
                    </div>
                </div>
            </div>
        </section>

        <!-- Course Modal -->
        <CourseModal v-if="selectedCourse" :course="selectedCourse" :show="showCourseModal"
            :is-subscribed="isUserSubscribedToAllChapters(selectedCourse.id)" :user-subscriptions="userSubscriptions"
            @close="closeCourseModal" @subscribe-chapter="subscribeToChapter" @subscribe-course="subscribeToCourse"
            @view-chapter="viewChapter" />

        <!-- Toast Notifications -->
        <Toast v-if="toast.show" :message="toast.message" :variant="toast.type" @close="toast.show = false" />
    </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import CourseCard from '@/components/CourseCard.vue'
import CourseModal from '@/components/CourseModal.vue'
import Toast from '@/components/Toast.vue'
import axios from 'axios'

export default {
    name: 'Courses',
    components: {
        CourseCard,
        CourseModal,
        Toast
    },
    setup() {
        const router = useRouter()
        const authStore = useAuthStore()

        const courses = ref([])
        const userSubscriptions = ref([])
        const loading = ref(true)
        const searchQuery = ref('')
        const selectedCourse = ref(null)
        const showCourseModal = ref(false)
        const searchTimeout = ref(null)

        const toast = ref({
            show: false,
            message: '',
            type: 'success'
        })

        const filteredCourses = computed(() => {
            if (!searchQuery.value) return courses.value

            const query = searchQuery.value.toLowerCase()
            return courses.value.filter(course =>
                course.name.toLowerCase().includes(query) ||
                course.description.toLowerCase().includes(query) ||
                course.chapters.some(chapter =>
                    chapter.name.toLowerCase().includes(query) ||
                    chapter.description.toLowerCase().includes(query)
                )
            )
        })

        const fetchCourses = async (search = '') => {
            try {
                loading.value = true
                let url = '/public/courses'
                if (search) {
                    url += `?search=${encodeURIComponent(search)}`
                }

                const response = await axios.get(url)
                courses.value = response.data.courses

                // Fetch user subscriptions if authenticated
                if (authStore.isAuthenticated) {
                    await fetchUserSubscriptions()
                }
            } catch (error) {
                console.error('Error fetching courses:', error)
                showToast('Failed to load courses', 'error')
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

        const isUserSubscribedToAllChapters = (courseId) => {
            if (!authStore.isAuthenticated || !userSubscriptions.value.length) return false

            const course = courses.value.find(c => c.id === courseId)
            if (!course) return false

            const subscribedChapterIds = userSubscriptions.value.map(sub => sub.chapter_id)
            return course.chapters.every(chapter => subscribedChapterIds.includes(chapter.id))
        }

        const handleSearch = () => {
            if (searchTimeout.value) {
                clearTimeout(searchTimeout.value)
            }

            searchTimeout.value = setTimeout(() => {
                fetchCourses(searchQuery.value)
            }, 300)
        }

        const openCourseModal = (course) => {
            selectedCourse.value = course
            showCourseModal.value = true
        }

        const closeCourseModal = () => {
            selectedCourse.value = null
            showCourseModal.value = false
        }

        const subscribeToChapter = async (chapterId) => {
            if (!authStore.isAuthenticated) {
                router.push('/login')
                return
            }

            try {
                // Check if user is already subscribed to this chapter
                const isSubscribed = userSubscriptions.value.some(sub => sub.chapter_id === chapterId)

                if (isSubscribed) {
                    // Unsubscribe from chapter
                    await axios.delete(`/user/subscriptions/${chapterId}`)
                    showToast('Successfully unsubscribed from chapter!', 'success')
                } else {
                    // Subscribe to chapter
                    await axios.post('/user/subscriptions', { chapter_id: chapterId })
                    showToast('Successfully subscribed to chapter!', 'success')
                }

                await fetchUserSubscriptions()
            } catch (error) {
                const message = error.response?.data?.message || 'Failed to update chapter subscription'
                showToast(message, 'error')
            }
        }

        const subscribeToCourse = async (courseId) => {
            if (!authStore.isAuthenticated) {
                router.push('/login')
                return
            }

            const course = courses.value.find(c => c.id === courseId)
            const isSubscribed = isUserSubscribedToAllChapters(courseId)

            try {
                if (isSubscribed) {
                    // Unsubscribe from all chapters
                    await Promise.all(course.chapters.map(chapter =>
                        axios.delete(`/user/subscriptions/${chapter.id}`)
                    ))
                    showToast('Successfully unsubscribed from all chapters!', 'success')
                } else {
                    // Subscribe to all chapters
                    const response = await axios.post('/user/course-subscription', { course_id: courseId })
                    showToast(response.data.message, 'success')
                }

                await fetchUserSubscriptions()
                closeCourseModal()
            } catch (error) {
                const message = error.response?.data?.message || 'Failed to update subscription'
                showToast(message, 'error')
            }
        }

        const viewChapter = (courseId, chapterId) => {
            if (!authStore.isAuthenticated) {
                router.push('/login')
                return
            }
            router.push(`/course/${courseId}/chapter/${chapterId}`)
        }

        const showToast = (message, type = 'success') => {
            toast.value = { show: true, message, type }
            setTimeout(() => {
                toast.value.show = false
            }, 5000)
        }

        onMounted(() => {
            fetchCourses()
        })

        return {
            courses,
            userSubscriptions,
            loading,
            searchQuery,
            filteredCourses,
            selectedCourse,
            showCourseModal,
            toast,
            handleSearch,
            openCourseModal,
            closeCourseModal,
            subscribeToChapter,
            subscribeToCourse,
            viewChapter,
            isUserSubscribedToAllChapters,
            authStore
        }
    }
}
</script>

<style scoped>
.courses-page {
    min-height: 100vh;
    background: linear-gradient(135deg, rgba(245, 124, 0, 0.05) 0%, rgba(245, 124, 0, 0.02) 100%);
}

.hero-section {
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
}

.hero-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 30% 50%, rgba(245, 124, 0, 0.1) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

.hero-section>.container {
    position: relative;
    z-index: 1;
}

.hero-title {
    font-size: 3rem;
    line-height: 1.1;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.text-gradient {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 50%, #f57c00 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
}

.search-container {
    max-width: 600px;
}

.search-wrapper {
    position: relative;
}

.search-icon {
    position: absolute;
    left: 1.5rem;
    top: 50%;
    transform: translateY(-50%);
    color: #f57c00;
    font-size: 1.2rem;
    z-index: 2;
}

.search-input {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border: 2px solid rgba(245, 124, 0, 0.2);
    border-radius: 50px;
    padding: 1.2rem 1.5rem 1.2rem 4rem;
    font-size: 1.1rem;
    transition: all 0.3s ease;
    box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
}

.search-input:focus {
    border-color: #f57c00;
    box-shadow: 0 0 0 0.25rem rgba(245, 124, 0, 0.15), 0 12px 40px rgba(245, 124, 0, 0.2);
    background: rgba(255, 255, 255, 1);
    outline: none;
}

.search-input::placeholder {
    color: rgba(117, 117, 117, 0.8);
}

.min-vh-50 {
    min-height: 50vh;
}

.courses-section {
    background: transparent;
}

.empty-state {
    padding: 3rem;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(245, 124, 0, 0.1);
}

.bg-blur {
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(10px);
}

@media (max-width: 768px) {
    .hero-title {
        font-size: 2rem;
    }

    .search-container {
        max-width: 100%;
    }

    .search-input {
        font-size: 1rem;
        padding: 1rem 1.2rem 1rem 3.5rem;
    }

    .search-icon {
        left: 1.2rem;
        font-size: 1rem;
    }

    .min-vh-50 {
        min-height: 40vh;
    }
}
</style>

<template>
    <div class="admin-dashboard">
        <!-- Header Section -->
        <section class="dashboard-header py-4 bg-blur">
            <div class="container">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h1 class="display-6 fw-bold mb-2 text-orange">Admin Dashboard</h1>
                        <p class="lead fw-medium mb-0">Welcome back, {{ authStore.userName }}</p>
                    </div>
                    <div class="col-md-4 text-md-end mt-3 mt-md-0">
                        <div class="dashboard-date">
                            <span class="badge date-badge">
                                <i class="bi bi-calendar-event me-2"></i>
                                {{ currentDate }}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Stats Overview -->
        <section class="stats-section py-4">
            <div class="container">
                <div class="row g-4 mb-4">
                    <div class="col-lg-4 col-md-6">
                        <StatsCard icon="bi bi-people-fill" :value="dashboardStats.users?.total || 0"
                            label="Total Users" :trend="getUserTrend()" />
                    </div>
                    <div class="col-lg-4 col-md-6">
                        <StatsCard icon="bi bi-question-circle-fill" :value="dashboardStats.content?.quizzes || 0"
                            label="Total Quizzes" />
                    </div>
                    <div class="col-lg-4 col-md-6">
                        <StatsCard icon="bi bi-clipboard-check-fill"
                            :value="dashboardStats.activity?.total_submissions || 0" label="Quiz Attempts"
                            :trend="getSubmissionTrend()" />
                    </div>
                </div>

                <div class="row g-4 mb-4">
                    <div class="col-lg-6">
                        <ActionCard icon="bi bi-people-fill" title="Manage Users"
                            description="View, edit, and manage user accounts. Monitor user activity and engagement statistics."
                            button-text="Manage Users" button-icon="bi bi-people" @click="showUsersManagement = true" />
                    </div>
                    <div class="col-lg-6">
                        <ActionCard icon="bi bi-question-circle-fill" title="Manage Quizzes"
                            description="Create, edit, and organize quizzes across different courses and chapters."
                            button-text="Manage Quizzes" button-icon="bi bi-question-circle"
                            @click="showQuizzesManagement = true" />
                    </div>
                </div>
            </div>
        </section>

        <!-- Charts Section -->
        <section class="charts-section py-4">
            <div class="container">
                <div class="row mb-5">
                    <div class="col-12">
                        <div class="chart-header mb-4">
                            <h3 class="fw-bold mb-0">
                                <i class="bi bi-people me-2 text-orange"></i>
                                User Analytics
                            </h3>
                        </div>
                    </div>
                </div>

                <div class="row g-4 mb-5">
                    <div class="col-lg-6">
                        <div class="chart-card">
                            <h5 class="chart-title">User Signups (Last 30 Days)</h5>
                            <div class="chart-container">
                                <canvas ref="userSignupsChart"></canvas>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-6">
                        <div class="chart-card">
                            <h5 class="chart-title">User Engagement</h5>
                            <div class="chart-container">
                                <canvas ref="userEngagementChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Course Analytics Section -->
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="chart-header">
                            <div class="d-flex justify-content-between align-items-center">
                                <h3 class="fw-bold mb-0">
                                    <i class="bi bi-graph-up me-2 text-orange"></i>
                                    Course Analytics
                                </h3>
                                <div class="course-selector">
                                    <select v-model="selectedCourseId" @change="loadCourseAnalytics"
                                        class="form-select">
                                        <option value="">Select Course</option>
                                        <option v-for="course in courses" :key="course.id" :value="course.id">
                                            {{ course.name }}
                                        </option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Live Quizzes for Selected Course -->
                <div v-if="selectedCourseId && courseAnalytics" class="row mb-4">
                    <div class="col-12">
                        <div class="live-quizzes-card">
                            <h5 class="fw-bold mb-3">
                                <i class="bi bi-broadcast text-danger me-2"></i>
                                Available Quizzes - {{ courseAnalytics.course_name }}
                            </h5>
                            <div v-if="courseAnalytics.live_quizzes_today.length === 0"
                                class="text-muted text-center py-3">
                                <i class="bi bi-calendar-x fs-2 mb-2 d-block"></i>
                                No quizzes available
                            </div>
                            <div v-else class="row g-3">
                                <div v-for="quiz in courseAnalytics.live_quizzes_today" :key="quiz.id" class="col-md-4">
                                    <div class="live-quiz-card">
                                        <h6 class="fw-bold mb-1">{{ quiz.title }}</h6>
                                        <p class="text-muted mb-1">{{ quiz.chapter }}</p>
                                        <small class="text-success">
                                            <i class="bi bi-clock me-1"></i>
                                            {{ formatTimeIST(quiz.time) }}
                                        </small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Course Selection Prompt -->
                <div v-if="!selectedCourseId" class="row mb-4">
                    <div class="col-12">
                        <div class="live-quizzes-card text-center">
                            <i class="bi bi-graph-up fs-1 text-orange mb-3"></i>
                            <h5 class="fw-bold mb-2">Select a Course</h5>
                            <p class="text-muted">Choose a course from the dropdown above to view live quizzes and
                                analytics</p>
                        </div>
                    </div>
                </div>

                <!-- Course Performance Charts Grid -->
                <div class="row g-4">
                    <!-- Course Popularity Chart -->
                    <div class="col-lg-6">
                        <div class="chart-card">
                            <h5 class="chart-title">Course Popularity</h5>
                            <div class="chart-container">
                                <canvas ref="coursePopularityChart"></canvas>
                            </div>
                        </div>
                    </div>

                    <!-- Chapter Analytics (if course selected) -->
                    <div v-if="selectedCourseId && courseAnalytics" class="col-lg-6">
                        <div class="chart-card">
                            <h5 class="chart-title">{{ courseAnalytics.course_name }} - Chapter Performance</h5>
                            <div class="chart-container">
                                <canvas ref="chapterAnalyticsChart"></canvas>
                            </div>
                        </div>
                    </div>

                    <!-- Submission Volume Heatmap -->
                    <div class="col-12">
                        <div class="chart-card">
                            <h5 class="chart-title">Quiz Submission Volume (Last 30 Days)</h5>
                            <div class="chart-container">
                                <canvas ref="submissionHeatmapChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Users Management Modal -->
        <div v-if="showUsersManagement" class="modal fade show modal-backdrop" style="display: block;"
            @click.self="showUsersManagement = false">
            <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title fw-bold">
                            <i class="bi bi-people me-2 text-orange"></i>
                            Users Management
                        </h5>
                        <button type="button" class="btn-close" @click="showUsersManagement = false"></button>
                    </div>
                    <div class="modal-body">
                        <div v-if="loadingUsers" class="text-center py-5">
                            <div class="spinner-border text-orange" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                        <div v-else class="row g-3">
                            <div v-for="user in users" :key="user.id" class="col-lg-4 col-md-6">
                                <UserCard :user="user" :deleting="deletingUserId === user.id"
                                    @delete-user="confirmDeleteUser" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Quizzes Management Modal -->
        <div v-if="showQuizzesManagement" class="modal fade show modal-backdrop" style="display: block;"
            @click.self="showQuizzesManagement = false">
            <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title fw-bold">
                            <i class="bi bi-question-circle me-2 text-orange"></i>
                            Quizzes Management
                        </h5>
                        <button type="button" class="btn-close" @click="showQuizzesManagement = false"></button>
                    </div>
                    <div class="modal-body">
                        <!-- Course Selector -->
                        <div class="mb-4">
                            <select v-model="selectedQuizCourseId" @change="loadQuizzes" class="form-select">
                                <option value="">Select Course</option>
                                <option v-for="course in courses" :key="course.id" :value="course.id">
                                    {{ course.name }}
                                </option>
                            </select>
                        </div>

                        <div v-if="selectedQuizCourseId">
                            <!-- Quiz Tabs -->
                            <div class="quiz-tabs-nav mb-4">
                                <ul class="nav nav-pills nav-fill">
                                    <li class="nav-item">
                                        <button class="nav-link" :class="{ active: activeQuizTab === 'live' }"
                                            @click="activeQuizTab = 'live'">
                                            <i class="bi bi-broadcast me-2 text-danger"></i>
                                            Live
                                        </button>
                                    </li>
                                    <li class="nav-item">
                                        <button class="nav-link" :class="{ active: activeQuizTab === 'upcoming' }"
                                            @click="activeQuizTab = 'upcoming'">
                                            <i class="bi bi-clock me-2 text-warning"></i>
                                            Upcoming
                                        </button>
                                    </li>
                                    <li class="nav-item">
                                        <button class="nav-link" :class="{ active: activeQuizTab === 'general' }"
                                            @click="activeQuizTab = 'general'">
                                            <i class="bi bi-infinity me-2 text-success"></i>
                                            Available
                                        </button>
                                    </li>
                                    <li class="nav-item">
                                        <button class="nav-link" :class="{ active: activeQuizTab === 'ended' }"
                                            @click="activeQuizTab = 'ended'">
                                            <i class="bi bi-calendar-x me-2 text-secondary"></i>
                                            Ended
                                        </button>
                                    </li>
                                </ul>
                            </div>

                            <!-- Quiz Cards -->
                            <div v-if="activeQuizzes.length === 0" class="text-center py-5">
                                <i class="bi bi-inbox text-muted fs-1 mb-3 d-block"></i>
                                <h5 class="text-muted">No {{ activeQuizTab }} quizzes</h5>
                            </div>
                            <div v-else class="row g-3">
                                <div v-for="quiz in activeQuizzes" :key="quiz.id" class="col-lg-4 col-md-6">
                                    <QuizCard :quiz="quiz" :tab-type="activeQuizTab" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Toast Notifications -->
        <Toast v-if="toast.show" :message="toast.message" :variant="toast.type" @close="toast.show = false" />
    </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Chart, registerables } from 'chart.js'
import StatsCard from '@/components/admin/StatsCard.vue'
import ActionCard from '@/components/admin/ActionCard.vue'
import UserCard from '@/components/admin/UserCard.vue'
import QuizCard from '@/components/QuizCard.vue'
import Toast from '@/components/Toast.vue'
import axios from 'axios'

Chart.register(...registerables)

export default {
    name: 'AdminDashboard',
    components: {
        StatsCard,
        ActionCard,
        UserCard,
        QuizCard,
        Toast
    },
    setup() {
        const authStore = useAuthStore()

        const dashboardStats = ref({})
        const chartsData = ref({})
        const courses = ref([])
        const selectedCourseId = ref('')
        const selectedQuizCourseId = ref('')
        const courseAnalytics = ref(null)
        const users = ref([])
        const quizzes = ref({})
        const activeQuizTab = ref('live')

        const showUsersManagement = ref(false)
        const showQuizzesManagement = ref(false)
        const loadingUsers = ref(false)
        const deletingUserId = ref(null)

        const toast = ref({
            show: false,
            message: '',
            type: 'success'
        })

        const userSignupsChart = ref(null)
        const userEngagementChart = ref(null)
        const coursePopularityChart = ref(null)
        const chapterAnalyticsChart = ref(null)
        const submissionHeatmapChart = ref(null)

        let chartInstances = {}

        const currentDate = computed(() => {
            return new Date().toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            })
        })

        const getUserTrend = () => {
            if (dashboardStats.value.activity?.recent_submissions > 10) {
                return '+12% this week'
            }
            return null
        }

        const getSubmissionTrend = () => {
            if (dashboardStats.value.activity?.recent_submissions) {
                return `${dashboardStats.value.activity.recent_submissions} this week`
            }
            return null
        }

        const activeQuizzes = computed(() => {
            if (!quizzes.value || !activeQuizTab.value) return []
            return quizzes.value[activeQuizTab.value] || []
        })

        const loadDashboardStats = async () => {
            try {
                const response = await axios.get('/admin/dashboard/stats')
                dashboardStats.value = response.data.stats
            } catch (error) {
                console.error('Error loading dashboard stats:', error)
                showToast('Failed to load dashboard statistics', 'error')
            }
        }

        const loadChartsData = async () => {
            try {
                const response = await axios.get('/admin/dashboard/charts')
                chartsData.value = response.data
                renderCharts()
            } catch (error) {
                console.error('Error loading charts data:', error)
                showToast('Failed to load charts data', 'error')
            }
        }

        const loadCourses = async () => {
            try {
                const response = await axios.get('/admin/courses')
                courses.value = response.data.courses
                if (courses.value.length > 0) {
                    selectedQuizCourseId.value = courses.value[0].id
                }
            } catch (error) {
                console.error('Error loading courses:', error)
            }
        }

        const loadCourseAnalytics = async () => {
            if (!selectedCourseId.value) return

            try {
                const response = await axios.get(`/admin/courses/${selectedCourseId.value}/analytics`)
                courseAnalytics.value = response.data
                renderChapterAnalyticsChart()
            } catch (error) {
                console.error('Error loading course analytics:', error)
            }
        }

        const loadUsers = async () => {
            loadingUsers.value = true
            try {
                const response = await axios.get('/admin/users')
                users.value = response.data.users
            } catch (error) {
                console.error('Error loading users:', error)
                showToast('Failed to load users', 'error')
            } finally {
                loadingUsers.value = false
            }
        }

        const loadQuizzes = async () => {
            if (!selectedQuizCourseId.value) return

            try {
                const response = await axios.get(`/quiz/courses/${selectedQuizCourseId.value}/quizzes`)
                quizzes.value = response.data.quizzes
            } catch (error) {
                console.error('Error loading quizzes:', error)
                showToast('Failed to load quizzes', 'error')
            }
        }

        const confirmDeleteUser = async (userId) => {
            if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
                return
            }

            deletingUserId.value = userId
            try {
                await axios.delete('/admin/users', { data: { user_id: userId } })
                users.value = users.value.filter(user => user.id !== userId)
                showToast('User deleted successfully', 'success')
                await loadDashboardStats()
            } catch (error) {
                console.error('Error deleting user:', error)
                showToast('Failed to delete user', 'error')
            } finally {
                deletingUserId.value = null
            }
        }

        const renderCharts = () => {
            renderUserSignupsChart()
            renderUserEngagementChart()
            renderCoursePopularityChart()
            renderSubmissionHeatmapChart()
        }

        const renderUserSignupsChart = () => {
            if (!userSignupsChart.value || !chartsData.value.user_signups) return

            const ctx = userSignupsChart.value.getContext('2d')

            if (chartInstances.userSignups) {
                chartInstances.userSignups.destroy()
            }

            const labels = chartsData.value.user_signups.map(item =>
                new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
            )
            const data = chartsData.value.user_signups.map(item => item.count)

            chartInstances.userSignups = new Chart(ctx, {
                type: 'line',
                data: {
                    labels,
                    datasets: [{
                        label: 'New Users',
                        data,
                        borderColor: '#f57c00',
                        backgroundColor: 'rgba(245, 124, 0, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            })
        }

        const renderUserEngagementChart = () => {
            if (!userEngagementChart.value || !chartsData.value.user_engagement) return

            const ctx = userEngagementChart.value.getContext('2d')

            if (chartInstances.userEngagement) {
                chartInstances.userEngagement.destroy()
            }

            const engagement = chartsData.value.user_engagement

            chartInstances.userEngagement = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Subscribed Users', 'Unsubscribed Users'],
                    datasets: [{
                        data: [engagement.subscribed, engagement.unsubscribed],
                        backgroundColor: ['#f57c00', '#e0e0e0'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            })
        }

        const renderCoursePopularityChart = () => {
            if (!coursePopularityChart.value || !chartsData.value.course_popularity) return

            const ctx = coursePopularityChart.value.getContext('2d')

            if (chartInstances.coursePopularity) {
                chartInstances.coursePopularity.destroy()
            }

            const labels = chartsData.value.course_popularity.map(item => item.course)
            const data = chartsData.value.course_popularity.map(item => item.submissions)

            chartInstances.coursePopularity = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [{
                        label: 'Submissions',
                        data,
                        backgroundColor: 'rgba(245, 124, 0, 0.8)',
                        borderColor: '#f57c00',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            })
        }

        const renderChapterAnalyticsChart = () => {
            if (!chapterAnalyticsChart.value || !courseAnalytics.value?.chapter_analytics) return

            const ctx = chapterAnalyticsChart.value.getContext('2d')

            if (chartInstances.chapterAnalytics) {
                chartInstances.chapterAnalytics.destroy()
            }

            const data = courseAnalytics.value.chapter_analytics

            chartInstances.chapterAnalytics = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: data.map(item => item.chapter),
                    datasets: [{
                        data: data.map(item => item.attempts),
                        backgroundColor: [
                            '#f57c00',
                            '#ff9800',
                            '#ffb74d',
                            '#ffcc80',
                            '#ffe0b2',
                            '#fff3e0'
                        ].slice(0, data.length)
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            })
        }

        const renderSubmissionHeatmapChart = () => {
            if (!submissionHeatmapChart.value || !chartsData.value.submission_volume) return

            const ctx = submissionHeatmapChart.value.getContext('2d')

            if (chartInstances.submissionHeatmap) {
                chartInstances.submissionHeatmap.destroy()
            }

            const labels = chartsData.value.submission_volume.map(item =>
                new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
            )
            const data = chartsData.value.submission_volume.map(item => item.count)

            chartInstances.submissionHeatmap = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [{
                        label: 'Submissions',
                        data,
                        backgroundColor: data.map(value => {
                            const intensity = Math.min(value / Math.max(...data), 1)
                            return `rgba(245, 124, 0, ${0.3 + intensity * 0.7})`
                        }),
                        borderColor: '#f57c00',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            })
        }

        const showToast = (message, type = 'success') => {
            toast.value = { show: true, message, type }
            setTimeout(() => {
                toast.value.show = false
            }, 5000)
        }

        const formatTimeIST = (timeString) => {
            if (!timeString) return 'All day'

            try {
                const today = new Date()
                const [hours, minutes] = timeString.split(':').map(Number)
                const dateTime = new Date(today.getFullYear(), today.getMonth(), today.getDate(), hours, minutes)

                return dateTime.toLocaleString('en-IN', {
                    hour: 'numeric',
                    minute: '2-digit',
                    hour12: true,
                    timeZone: 'Asia/Kolkata'
                })
            } catch (error) {
                return timeString || 'All day'
            }
        }

        watch(showUsersManagement, (newVal) => {
            if (newVal) {
                loadUsers()
            }
        })

        watch(showQuizzesManagement, (newVal) => {
            if (newVal && selectedQuizCourseId.value) {
                loadQuizzes()
            }
        })

        watch(selectedCourseId, () => {
            if (selectedCourseId.value) {
                loadCourseAnalytics()
            }
        })

        watch(selectedQuizCourseId, () => {
            if (selectedQuizCourseId.value) {
                loadQuizzes()
            }
        })

        onMounted(async () => {
            await Promise.all([
                loadDashboardStats(),
                loadChartsData(),
                loadCourses()
            ])
        })

        return {
            authStore,
            dashboardStats,
            courses,
            selectedCourseId,
            selectedQuizCourseId,
            courseAnalytics,
            users,
            quizzes,
            activeQuizTab,
            activeQuizzes,
            showUsersManagement,
            showQuizzesManagement,
            loadingUsers,
            deletingUserId,
            currentDate,
            toast,
            userSignupsChart,
            userEngagementChart,
            coursePopularityChart,
            chapterAnalyticsChart,
            submissionHeatmapChart,
            getUserTrend,
            getSubmissionTrend,
            loadCourseAnalytics,
            loadQuizzes,
            confirmDeleteUser,
            formatTimeIST
        }
    }
}
</script>

<style scoped>
.admin-dashboard {
    min-height: 100vh;
    background: linear-gradient(135deg, rgba(245, 124, 0, 0.05) 0%, rgba(245, 124, 0, 0.02) 100%);
}

.dashboard-header {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(245, 124, 0, 0.1);
}

.text-orange {
    color: #f57c00;
}

.date-badge {
    background: rgba(245, 124, 0, 0.1);
    color: #f57c00;
    border: 1px solid rgba(245, 124, 0, 0.2);
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-size: 0.9rem;
}

.chart-header {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid rgba(245, 124, 0, 0.1);
    margin-bottom: 1rem;
}

.course-selector {
    position: relative;
}

.course-selector .form-select {
    border-radius: 12px;
    border: 2px solid rgba(245, 124, 0, 0.3);
    background: linear-gradient(135deg, rgba(245, 124, 0, 0.1) 0%, rgba(255, 152, 0, 0.1) 100%);
    backdrop-filter: blur(10px);
    color: #f57c00;
    font-weight: 600;
    padding: 0.75rem 1rem;
    min-width: 200px;
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.1);
    transition: all 0.3s ease;
}

.course-selector .form-select:focus {
    border-color: #f57c00;
    box-shadow: 0 0 0 0.25rem rgba(245, 124, 0, 0.25);
    background: linear-gradient(135deg, rgba(245, 124, 0, 0.15) 0%, rgba(255, 152, 0, 0.15) 100%);
}

.course-selector .form-select:hover {
    border-color: #f57c00;
    box-shadow: 0 6px 20px rgba(245, 124, 0, 0.2);
}

.live-quizzes-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(245, 124, 0, 0.1);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
    position: relative;
    z-index: 1;
}

.live-quiz-card {
    background: rgba(220, 53, 69, 0.1);
    border: 1px solid rgba(220, 53, 69, 0.2);
    border-radius: 12px;
    padding: 1rem;
    transition: all 0.3s ease;
}

.live-quiz-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(220, 53, 69, 0.2);
}

.chart-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(245, 124, 0, 0.1);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
    transition: all 0.3s ease;
}

.chart-card:hover {
    box-shadow: 0 12px 40px rgba(245, 124, 0, 0.15);
    border-color: rgba(245, 124, 0, 0.2);
}

.chart-title {
    color: #2c3e50;
    font-weight: 700;
    margin-bottom: 1.5rem;
    text-align: center;
}

.chart-container {
    position: relative;
    height: 300px;
}

.modal-backdrop {
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(5px);
}

.modal-content {
    border-radius: 20px;
    border: none;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
    background: #ffffff;
}

.modal-header {
    border-bottom: 1px solid rgba(245, 124, 0, 0.1);
    padding: 1.5rem 2rem;
}

.modal-body {
    padding: 2rem;
}

.quiz-tabs-nav {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 0.5rem;
    box-shadow: 0 4px 20px rgba(245, 124, 0, 0.1);
}

.quiz-tabs-nav .nav-link {
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
}

.quiz-tabs-nav .nav-link:hover {
    background: rgba(245, 124, 0, 0.1);
    color: #f57c00;
    transform: translateY(-1px);
}

.quiz-tabs-nav .nav-link.active {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    color: white !important;
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.quiz-tabs-nav .nav-link.active i {
    color: white !important;
}

.spinner-border.text-orange {
    color: #f57c00 !important;
}

.bg-blur {
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(10px);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .dashboard-header .display-6 {
        font-size: 1.75rem;
    }

    .chart-card {
        padding: 1rem;
    }

    .chart-container {
        height: 250px;
    }

    .modal-body {
        padding: 1rem;
    }

    .live-quizzes-card {
        padding: 1rem;
    }

    .quiz-tabs-nav .nav-link {
        padding: 0.75rem 1rem;
        font-size: 0.9rem;
    }
}

@media (max-width: 576px) {
    .chart-container {
        height: 200px;
    }

    .date-badge {
        font-size: 0.8rem;
        padding: 0.4rem 0.8rem;
    }

    .modal-dialog {
        margin: 0.5rem;
    }
}
</style>

<template>
    <div class="user-profile">
        <!-- Hero Header Section -->
        <section class="profile-header py-5 bg-blur">
            <div class="container">
                <div class="row align-items-center">
                    <div class="col-lg-8">
                        <h1 class="display-5 fw-bold mb-3 hero-title">
                            User Profile
                        </h1>
                        <h3 class="fw-semibold text-gradient mb-2">@{{ username }}</h3>
                        <div v-if="profileData.user" class="user-info">
                            <h5 class="text-muted mb-1">{{ profileData.user.name }}</h5>
                            <p v-if="profileData.user.email" class="text-muted">{{ profileData.user.email }}</p>
                        </div>
                    </div>
                    <div class="col-lg-4 text-lg-end mt-4 mt-lg-0">
                        <div v-if="profileData.is_own_profile" class="own-profile-badge">
                            <span class="badge bg-primary fs-6 px-3 py-2">
                                <i class="bi bi-person-check me-2"></i>Your Profile
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Stats Section -->
        <section class="stats-section pt-5 pb-5">
            <div class="container">
                <div v-if="loading" class="text-center py-5">
                    <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>

                <div v-else-if="error" class="alert alert-danger text-center">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    {{ error }}
                </div>

                <div v-else-if="profileData.user" class="row g-4">
                    <div class="col-lg-4">
                        <div class="stats-card h-100">
                            <div class="card glass-card h-100">
                                <div class="card-body text-center">
                                    <div class="stats-icon mb-3">
                                        <i class="bi bi-trophy-fill fs-1"></i>
                                    </div>
                                    <h3 class="stats-number fw-bold mb-2">{{ profileData.stats?.total_quizzes_taken || 0
                                        }}</h3>
                                    <p class="stats-label text-muted mb-0">Quizzes Completed</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-4">
                        <div class="stats-card h-100">
                            <div class="card glass-card h-100">
                                <div class="card-body text-center">
                                    <div class="stats-icon mb-3">
                                        <i class="bi bi-graph-up fs-1"></i>
                                    </div>
                                    <h3 class="stats-number fw-bold mb-2">{{
                                        formatPercentage(profileData.stats?.overall_accuracy) }}%</h3>
                                    <p class="stats-label text-muted mb-0">Average Score</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-4">
                        <div class="stats-card h-100">
                            <div class="card glass-card h-100">
                                <div class="card-body text-center">
                                    <div class="stats-icon mb-3">
                                        <i class="bi bi-clock-fill fs-1"></i>
                                    </div>
                                    <h3 class="stats-number fw-bold mb-2">{{
                                        formatTimeSpent(profileData.stats?.total_time_spent) }}</h3>
                                    <p class="stats-label text-muted mb-0">Time Spent</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Additional Info Section -->
                <div v-if="profileData.user && !loading && !error" class="row mt-5">
                    <div class="col-12">
                        <div class="info-card glass-card">
                            <div class="card-body text-center py-5">
                                <div class="user-avatar mb-4">
                                    <div class="avatar-circle">
                                        {{ userInitials }}
                                    </div>
                                </div>
                                <h4 class="fw-bold mb-2">{{ profileData.user.name }}</h4>
                                <p class="text-muted mb-3">@{{ profileData.user.username }}</p>

                                <div v-if="profileData.stats?.total_questions_answered" class="additional-stats">
                                    <div class="row justify-content-center">
                                        <div class="col-md-6 col-lg-4">
                                            <div class="stat-item">
                                                <div class="stat-value">{{ profileData.stats.total_questions_answered }}
                                                </div>
                                                <div class="stat-label">Total Questions Answered</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div v-if="!profileData.is_own_profile" class="mt-4">
                                    <button class="btn btn-outline-primary" @click="$router.push('/courses')">
                                        <i class="bi bi-arrow-left me-2"></i>
                                        Back to Courses
                                    </button>
                                </div>
                                <div v-else class="mt-4">
                                    <button class="btn btn-primary me-3" @click="$router.push('/dashboard')">
                                        <i class="bi bi-speedometer2 me-2"></i>
                                        Go to Dashboard
                                    </button>
                                    <button class="btn btn-outline-primary" @click="$router.push('/courses')">
                                        <i class="bi bi-book me-2"></i>
                                        Browse Courses
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const username = computed(() => route.params.username.replace('@', ''))
const profileData = ref({})
const loading = ref(true)
const error = ref('')

// API Service
const apiService = {
    async get(endpoint) {
        const token = authStore.token
        const response = await fetch(`http://localhost:5000/api${endpoint}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        })

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        return await response.json()
    }
}

// Load profile data
const loadProfileData = async () => {
    try {
        loading.value = true
        error.value = ''

        // Check if user is authenticated to use the detailed profile API
        if (authStore.isAuthenticated) {
            const data = await apiService.get(`/user/profile/${username.value}`)
            profileData.value = data
        } else {
            // Fall back to public profile API for unauthenticated users
            const response = await fetch(`http://localhost:5000/api/public/u/@${username.value}`)
            if (!response.ok) {
                throw new Error('User not found')
            }
            const data = await response.json()
            profileData.value = {
                user: data.user,
                stats: {
                    total_quizzes_taken: data.public_stats.total_quizzes_taken,
                    overall_accuracy: data.public_stats.overall_accuracy,
                    total_time_spent: data.public_stats.total_time_spent,
                    total_questions_answered: data.public_stats.total_questions_answered
                },
                is_own_profile: false
            }
        }
    } catch (err) {
        console.error('Error loading profile data:', err)
        error.value = 'Unable to load user profile. Please try again.'
    } finally {
        loading.value = false
    }
}

// Utility functions
const formatPercentage = (value) => {
    return Math.round(value || 0)
}

const formatTimeSpent = (minutes) => {
    if (!minutes) return '0m'

    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60

    if (hours > 0) {
        return `${hours}h ${mins}m`
    }
    return `${mins}m`
}

const userInitials = computed(() => {
    if (!profileData.value.user?.name) return '?'
    const name = profileData.value.user.name
    const parts = name.split(' ')
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase()
    }
    return name[0].toUpperCase()
})

// Initialize
onMounted(async () => {
    await loadProfileData()
})
</script>

<style scoped>
/* User Profile Styles - Matching UserDashboard */
.user-profile {
    min-height: 100vh;
    background: linear-gradient(135deg, rgba(245, 124, 0, 0.05) 0%, rgba(245, 124, 0, 0.02) 100%);
}

/* Hero Header Section */
.profile-header {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(245, 124, 0, 0.1);
}

.hero-title {
    color: #f57c00;
    font-family: 'Poppins', sans-serif;
    font-size: 3rem;
    font-weight: 800;
}

.text-gradient {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    transition: all 0.3s ease;
}

.user-info h5 {
    color: #2c3e50;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.own-profile-badge .badge {
    border-radius: 20px;
    font-weight: 600;
}

/* Stats Cards - Matching UserDashboard */
.stats-card {
    transition: all 0.3s ease;
}

.stats-card:hover {
    transform: translateY(-5px);
}

.glass-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(245, 124, 0, 0.1);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
    transition: all 0.3s ease;
}

.glass-card:hover {
    box-shadow: 0 12px 40px rgba(245, 124, 0, 0.15);
    border-color: rgba(245, 124, 0, 0.2);
}

.stats-icon i {
    color: #f57c00 !important;
    text-shadow: 0 2px 4px rgba(245, 124, 0, 0.2);
}

.stats-number {
    color: #f57c00;
    font-size: 2.5rem;
}

/* Info Card */
.info-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(245, 124, 0, 0.1);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
}

/* User Avatar */
.user-avatar {
    display: flex;
    justify-content: center;
    align-items: center;
}

.avatar-circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    font-weight: bold;
    box-shadow: 0 8px 32px rgba(245, 124, 0, 0.3);
    transition: all 0.3s ease;
}

.avatar-circle:hover {
    transform: scale(1.05);
    box-shadow: 0 12px 40px rgba(245, 124, 0, 0.4);
}

/* Additional Stats */
.additional-stats .stat-item {
    text-align: center;
    padding: 1rem;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: #f57c00;
    margin-bottom: 0.5rem;
}

.stat-label {
    color: #6c757d;
    font-size: 0.9rem;
    font-weight: 500;
}

/* Buttons */
.btn {
    border-radius: 12px;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    transition: all 0.3s ease;
}

.btn-primary {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    color: white;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(245, 124, 0, 0.3);
}

.btn-outline-primary {
    border: 2px solid #f57c00;
    color: #f57c00;
    background: transparent;
}

.btn-outline-primary:hover {
    background: #f57c00;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(245, 124, 0, 0.3);
}

/* Loading */
.spinner-border.text-primary {
    color: #f57c00 !important;
}

/* Responsive Design */
@media (max-width: 768px) {
    .hero-title {
        font-size: 2rem;
    }

    .stats-number {
        font-size: 2rem;
    }

    .avatar-circle {
        width: 100px;
        height: 100px;
        font-size: 2.5rem;
    }

    .btn {
        width: 100%;
        margin-bottom: 0.5rem;
    }
}

/* Animations */
.stats-card {
    animation: fadeInUp 0.6s ease-out;
}

.info-card {
    animation: fadeInUp 0.8s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>

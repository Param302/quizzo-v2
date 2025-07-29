<template>
    <div class="public-profile">
        <div class="container py-4">
            <div class="row">
                <div class="col-lg-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                                style="width: 100px; height: 100px; font-size: 2rem;">
                                {{ userInitials }}
                            </div>
                            <h4 class="fw-bold">{{ user.name }}</h4>
                            <p class="text-muted">@{{ user.username }}</p>
                            <p class="text-muted small">Member since {{ memberSince }}</p>

                            <div class="row g-3 mt-3">
                                <div class="col-4">
                                    <div class="text-center">
                                        <div class="fw-bold fs-5 text-primary">{{ user.stats.quizzesCompleted }}</div>
                                        <small class="text-muted">Quizzes</small>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="text-center">
                                        <div class="fw-bold fs-5 text-success">{{ user.stats.averageScore }}%</div>
                                        <small class="text-muted">Avg Score</small>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="text-center">
                                        <div class="fw-bold fs-5 text-warning">#{{ user.stats.rank }}</div>
                                        <small class="text-muted">Rank</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Recent Quiz Results</h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table">
                                    <thead>
                                        <tr>
                                            <th>Quiz</th>
                                            <th>Score</th>
                                            <th>Date</th>
                                            <th>Time</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="result in user.recentResults" :key="result.id">
                                            <td>{{ result.quizName }}</td>
                                            <td>
                                                <span class="badge" :class="getScoreBadgeClass(result.score)">
                                                    {{ result.score }}%
                                                </span>
                                            </td>
                                            <td>{{ formatDate(result.date) }}</td>
                                            <td>{{ result.duration }}</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    <div class="card mt-4">
                        <div class="card-header">
                            <h5 class="mb-0">Achievements</h5>
                        </div>
                        <div class="card-body">
                            <div class="row g-3">
                                <div v-for="achievement in user.achievements" :key="achievement.id" class="col-md-4">
                                    <div class="achievement-card text-center p-3 border rounded">
                                        <i :class="achievement.icon" class="fs-2 text-primary mb-2"></i>
                                        <h6 class="fw-semibold">{{ achievement.name }}</h6>
                                        <small class="text-muted">{{ achievement.description }}</small>
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

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const username = route.params.username.replace('@', '')

// Mock user data
const user = ref({
    name: 'John Doe',
    username: username,
    joinDate: '2024-01-15',
    stats: {
        quizzesCompleted: 45,
        averageScore: 87,
        rank: 23
    },
    recentResults: [
        { id: 1, quizName: 'JavaScript Basics', score: 92, date: '2024-07-28', duration: '8:45' },
        { id: 2, quizName: 'Python Fundamentals', score: 85, date: '2024-07-27', duration: '12:30' },
        { id: 3, quizName: 'Web Development', score: 78, date: '2024-07-26', duration: '15:20' },
        { id: 4, quizName: 'React Concepts', score: 94, date: '2024-07-25', duration: '10:15' }
    ],
    achievements: [
        { id: 1, name: 'Quiz Master', description: 'Completed 50+ quizzes', icon: 'bi bi-trophy-fill' },
        { id: 2, name: 'High Scorer', description: '90%+ average score', icon: 'bi bi-star-fill' },
        { id: 3, name: 'Consistent Learner', description: '7-day streak', icon: 'bi bi-calendar-check-fill' }
    ]
})

const userInitials = computed(() => {
    const name = user.value.name
    const parts = name.split(' ')
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase()
    }
    return name[0].toUpperCase()
})

const memberSince = computed(() => {
    return new Date(user.value.joinDate).toLocaleDateString('en-US', {
        month: 'long',
        year: 'numeric'
    })
})

const getScoreBadgeClass = (score) => {
    if (score >= 90) return 'bg-success'
    if (score >= 70) return 'bg-warning'
    return 'bg-danger'
}

const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
    })
}
</script>

<style scoped>
.achievement-card {
    transition: transform 0.2s ease;
}

.achievement-card:hover {
    transform: translateY(-2px);
}
</style>

<template>
	<div class="user-profile">
		<!-- Hero Header Section -->
		<section class="profile-header py-5 bg-blur">
			<div class="container">
				<div class="row align-items-center">
					<div class="col-lg-8">
						<h1 class="display-5 fw-bold mb-3 hero-title">
							{{ profileData.user?.name || 'User Profile' }}
						</h1>
						<h3 class="fw-semibold text-gradient mb-2">@{{ username }}</h3>
						<div v-if="profileData.user" class="user-info">
							<p v-if="profileData.user.email" class="text-muted mb-2">{{ profileData.user.email }}</p>
							<p class="text-muted">
								<i class="bi bi-calendar-plus me-2 text-warning"></i>
								Member since {{ formatMemberSince(profileData.user.created_at) }}
							</p>
						</div>
					</div>
					<div class="col-lg-4 text-lg-end mt-4 mt-lg-0">
						<button class="btn btn-outline-primary btn-lg modern-btn" @click="shareProfile">
							<i class="bi bi-share me-2" v-if="!urlCopied"></i>
							<i class="bi bi-check-circle me-2" v-if="urlCopied"></i>
							{{ urlCopied ? 'URL Copied' : 'Share Profile' }}
						</button>
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

				<!-- CTA Section -->
				<div v-if="profileData.user && !loading && !error" class="row mt-5">
					<div class="col-12">
						<section class="cta-section">
							<div class="container text-center animate-fade-in">
								<div class="row justify-content-center">
									<div class="col-lg-8 d-flex flex-column align-items-center gap-3">
										<h2 class="display-5 fw-bold mb-3 cta-title">Compete with {{
											profileData.user.name }}</h2>
										<div class="d-flex gap-3 justify-content-center flex-wrap w-100">
											<router-link :to="'/courses'"
												class="btn btn-primary btn-lg animate-bounce-in modern-btn">
												<i class="bi bi-play-circle me-2"></i>
												Explore Quizzes
											</router-link>
										</div>
									</div>
								</div>
							</div>
						</section>
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
const urlCopied = ref(false)

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

const formatMemberSince = (dateString) => {
	if (!dateString) return ''
	const date = new Date(dateString)
	return new Intl.DateTimeFormat('en-US', {
		year: 'numeric',
		month: 'long'
	}).format(date)
}

const shareProfile = async () => {
	const url = window.location.href
	try {
		await navigator.clipboard.writeText(url)
		urlCopied.value = true
		// Reset the button text after 2 seconds
		setTimeout(() => {
			urlCopied.value = false
		}, 2000)
	} catch (err) {
		// Fallback for older browsers
		const textArea = document.createElement('textarea')
		textArea.value = url
		document.body.appendChild(textArea)
		textArea.select()
		document.execCommand('copy')
		document.body.removeChild(textArea)
		urlCopied.value = true
		// Reset the button text after 2 seconds
		setTimeout(() => {
			urlCopied.value = false
		}, 2000)
	}
}

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

/* CTA Section */
.cta-section {
	position: relative;
	overflow: hidden;
	padding-top: 3rem;
	border-radius: 20px;
}

.cta-section::before {
	content: '';
	position: absolute;
	top: -50%;
	left: -50%;
	width: 200%;
	height: 200%;
	background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
	animation: float 8s ease-in-out infinite;
}

.cta-section .container {
	position: relative;
	z-index: 1;
}

.cta-title {
	color: #f57c00;
}

.cta-lead {
	color: #f57c00;
}

/* Modern Button - Matching Landing Page */
.modern-btn {
	border-radius: 50px;
	padding: 12px 32px;
	font-weight: 600;
	backdrop-filter: blur(10px);
	transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
	position: relative;
	overflow: hidden;
	box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.modern-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(245, 124, 0, 0.4);
}

.modern-btn::before {
	content: '';
	position: absolute;
	top: 0;
	left: -100%;
	width: 100%;
	height: 100%;
	background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
	transition: left 0.5s;
}

.modern-btn:hover::before {
	left: 100%;
}

.btn-light.modern-btn {
	background: rgba(255, 255, 255, 0.9);
	color: #f57c00;
	border: 2px solid rgba(245, 124, 0, 0.2);
}

.btn-light.modern-btn:hover {
	background: rgba(245, 124, 0, 0.1);
	color: #f57c00;
	border-color: #f57c00;
}

/* Buttons */
.btn {
	border-radius: 12px;
	font-weight: 600;
	padding: 0.75rem 1.5rem;
	transition: all 0.3s ease;
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
@media (max-width: 1200px) {
	.hero-title {
		font-size: 2.5rem;
	}

	.cta-section {
		padding: 4rem 0;
	}
}

@media (max-width: 992px) {
	.hero-title {
		font-size: 2.2rem;
	}

	.stats-number {
		font-size: 2.2rem;
	}

	.cta-section {
		padding: 3rem 0;
	}
}

@media (max-width: 768px) {
	.hero-title {
		font-size: 1.8rem;
		text-align: center;
	}

	.stats-number {
		font-size: 2rem;
	}

	.btn {
		width: 100%;
		margin-bottom: 0.5rem;
	}

	.modern-btn {
		width: 100%;
		margin: 0.5rem 0;
	}

	.profile-header .col-lg-8,
	.profile-header .col-lg-4 {
		text-align: center;
	}

	.text-lg-end {
		text-align: center !important;
	}

	.cta-section {
		padding: 2.5rem 0;
		border-radius: 15px;
	}
}

@media (max-width: 576px) {
	.hero-title {
		font-size: 1.5rem;
	}

	.stats-number {
		font-size: 1.8rem;
	}

	.user-info p {
		font-size: 0.9rem;
	}

	.cta-section {
		padding: 2rem 0;
		border-radius: 10px;
	}

	.modern-btn {
		padding: 10px 24px;
		font-size: 0.9rem;
	}
}

/* Utility Classes */
.w-fit {
	width: fit-content;
}

@media (min-width: 768px) {
	.w-md-auto {
		width: auto !important;
	}
}

/* Animations */
.stats-card {
	animation: fadeInUp 0.6s ease-out;
}

.cta-section {
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

@keyframes float {

	0%,
	100% {
		transform: translateY(0px);
	}

	50% {
		transform: translateY(-15px);
	}
}
</style>

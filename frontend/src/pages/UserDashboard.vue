<template>
	<div class="user-dashboard">
		<!-- Hero Header Section -->
		<section class="dashboard-header py-5 bg-blur">
			<div class="container">
				<div class="row align-items-center">
					<div class="col-lg-8">
						<h1 class="display-5 fw-bold mb-3 hero-title">
							My Dashboard
						</h1>
						<router-link :to="`/u/@${authStore.userName}`" class="username-link">
							<h3 class="fw-semibold text-gradient mb-2">@{{ authStore.userName || 'Welcome' }}</h3>
						</router-link>
					</div>
					<div class="col-lg-4 text-lg-end mt-4 mt-lg-0">
						<div
							class="d-flex flex-column gap-3 justify-content-lg-end justify-content-center align-items-lg-end align-items-center">
							<button class="btn btn-primary btn-lg modern-btn" @click="$router.push('/courses')">
								<i class="bi bi-compass me-2"></i>
								Explore Quizzes
							</button>
							<button class="btn btn-outline-primary btn-lg modern-btn" @click="exportUserData"
								:disabled="loading.export">
								<i class="bi bi-download me-2"></i>
								<span v-if="loading.export">Exporting...</span>
								<span v-else>Export Data</span>
							</button>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Stats Section -->
		<section class="stats-section pt-5">
			<div class="container">
				<div class="row g-4 mb-5">
					<div class="col-lg-4">
						<div class="stats-card h-100">
							<div class="card glass-card h-100">
								<div class="card-body text-center">
									<div class="stats-icon mb-3">
										<i class="bi bi-trophy-fill fs-1"></i>
									</div>
									<h3 class="stats-number fw-bold mb-2">{{ dashboardData.stats?.total_quizzes_taken ||
										0 }}</h3>
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
										formatPercentage(dashboardData.stats?.overall_accuracy) }}%
									</h3>
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
									<h3 class="stats-number fw-bold mb-2">{{ formatTimeSpent(totalTimeSpent) }}</h3>
									<p class="stats-label text-muted mb-0">Time Spent</p>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Main Content Section -->
		<section class="main-content pb-5">
			<div class="container">
				<!-- Tab Navigation -->
				<div class="quiz-tabs-nav mb-4">
					<ul class="nav nav-pills nav-fill">
						<li class="nav-item">
							<button class="nav-link" :class="{ active: activeTab === 'upcoming' }"
								@click="handleTabChange('upcoming')">
								<i class="bi bi-calendar-event me-2"></i>
								Upcoming Quizzes
							</button>
						</li>
						<li class="nav-item">
							<button class="nav-link" :class="{ active: activeTab === 'analytics' }"
								@click="handleTabChange('analytics')">
								<i class="bi bi-graph-up me-2"></i>
								Analytics
							</button>
						</li>
						<li class="nav-item">
							<button class="nav-link" :class="{ active: activeTab === 'subscriptions' }"
								@click="handleTabChange('subscriptions')">
								<i class="bi bi-bookmark-check me-2"></i>
								Subscriptions
							</button>
						</li>
						<li class="nav-item">
							<button class="nav-link" :class="{ active: activeTab === 'submissions' }"
								@click="handleTabChange('submissions')">
								<i class="bi bi-file-earmark-text me-2"></i>
								Submissions
							</button>
						</li>
					</ul>
				</div> <!-- Tab Content -->
				<div class="tab-content">
					<!-- Upcoming Quiz Tab -->
					<div v-if="activeTab === 'upcoming'" class="tab-pane-content animate-fade-in">

						<div v-if="loading.upcoming" class="text-center py-5">
							<div class="spinner-border text-primary" role="status">
								<span class="visually-hidden">Loading...</span>
							</div>
						</div>

						<div v-else-if="upcomingQuizzes.length === 0" class="empty-state-card glass-card">
							<div class="text-center py-5">
								<i class="bi bi-calendar-x text-muted mb-3" style="font-size: 4rem; opacity: 0.5;"></i>
								<h5 class="text-muted mb-3">No upcoming quizzes</h5>
								<p class="text-muted mb-4">Subscribe to more chapters to see upcoming quizzes</p>
								<button class="btn btn-outline-primary" @click="$router.push('/courses')">
									<i class="bi bi-plus-circle me-2"></i>
									Explore Courses
								</button>
							</div>
						</div>

						<div v-else class="row g-4">
							<div v-for="quiz in upcomingQuizzes" :key="quiz.id" class="col-xl-4 col-md-6">
								<div class="quiz-card glass-card" :class="{ 'live-quiz-card': quiz.is_live }">
									<div class="card-body p-4">
										<div class="d-flex justify-content-between align-items-start mb-3">
											<div class="flex-grow-1">
												<h6 class="card-title fw-bold mb-2 quiz-title">{{ quiz.title }}</h6>
												<p class="fw-medium small mb-2">{{ quiz.chapter }}</p>
												<div class="course-chip mb-2">
													<span>{{ quiz.course }}</span>
												</div>
											</div>
											<div v-if="quiz.is_live" class="live-badge">
												<span class="badge bg-danger pulse-animation">
													<i class="bi bi-record-circle me-1"></i>LIVE
												</span>
											</div>
										</div>

										<div class="quiz-meta mb-3 small text-muted">
											<div class="d-flex justify-content-between">
												<span><i class="bi bi-calendar me-1 text-warning"></i>{{
													formatDateTime(quiz.date_of_quiz) }}</span>
												<span><i class="bi bi-clock me-1 text-warning"></i>{{
													formatDuration(quiz.time_duration) }}</span>
											</div>
										</div>

										<div class="quiz-actions mb-3">
											<button v-if="quiz.is_live" class="btn btn-danger w-100 fw-semibold"
												@click="startQuiz(quiz.id)">
												<i class="bi bi-play-fill me-2"></i>Join Live Quiz
											</button>
											<div v-else class="quiz-start-info text-warning fw-bold small">
												<i class="bi bi-exclamation-circle text-warning me-2"></i>
												<span>Starts {{ getTimeUntil(quiz.date_of_quiz) }}</span>
											</div>
										</div>

										<button class="btn-auth-secondary w-100"
											@click="viewChapter(quiz.course_id, quiz.chapter_id)">
											<i class="bi bi-eye me-2"></i>View Details
										</button>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Analytics Tab -->
					<div v-if="activeTab === 'analytics'" class="tab-pane-content animate-fade-in">
						<div v-if="loading.analytics" class="text-center py-5">
							<div class="spinner-border text-primary" role="status">
								<span class="visually-hidden">Loading...</span>
							</div>
						</div>

						<div v-else-if="!analyticsData.quiz_scores || analyticsData.quiz_scores.length === 0"
							class="empty-state-card glass-card">
							<div class="text-center py-5">
								<i class="bi bi-graph-up text-muted mb-3" style="font-size: 4rem; opacity: 0.5;"></i>
								<h5 class="text-muted mb-3">No analytics data yet</h5>
								<p class="text-muted mb-4">Take some quizzes to see your analytics here</p>
								<button class="btn btn-outline-primary" @click="$router.push('/courses')">
									<i class="bi bi-play-circle me-2"></i>
									Take a Quiz
								</button>
							</div>
						</div>

						<div v-else class="row g-4">
							<div class="col-lg-8">
								<div class="chart-card glass-card">
									<div class="card-header">
										<h6 class="fw-bold mb-0">Quiz Score Distribution</h6>
									</div>
									<div class="card-body">
										<div class="chart-container">
											<canvas ref="scoresChart"></canvas>
										</div>
									</div>
								</div>
							</div>

							<div class="col-lg-4">
								<div class="chart-card glass-card">
									<div class="card-header">
										<h6 class="fw-bold mb-0">Attempts by Course</h6>
									</div>
									<div class="card-body">
										<div class="chart-container">
											<canvas ref="courseChart"></canvas>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Subscriptions Tab -->
					<div v-if="activeTab === 'subscriptions'" class="tab-pane-content animate-fade-in">
						<div v-if="loading.subscriptions" class="text-center py-5">
							<div class="spinner-border text-primary" role="status">
								<span class="visually-hidden">Loading...</span>
							</div>
						</div>

						<div v-else-if="subscriptions.length === 0" class="empty-state-card glass-card">
							<div class="text-center py-5">
								<i class="bi bi-bookmark-x text-muted mb-3" style="font-size: 4rem; opacity: 0.5;"></i>
								<h5 class="text-muted mb-3">No subscriptions yet</h5>
								<p class="text-muted mb-4">Subscribe to chapters to access their quizzes</p>
								<button class="btn btn-outline-primary" @click="$router.push('/courses')">
									<i class="bi bi-plus-circle me-2"></i>
									Browse Courses
								</button>
							</div>
						</div>

						<div v-else class="row g-4">
							<div v-for="subscription in subscriptions" :key="subscription.id" class="col-lg-6">
								<div class="subscription-card glass-card">
									<div class="card-body p-4">
										<div class="d-flex justify-content-between align-items-start">
											<div class="flex-grow-1">
												<h6 class="fw-bold mb-2 subscription-title">{{ subscription.chapter_name
												}}</h6>
												<div class="course-chip mb-2">
													<span>{{ subscription.course_name }}</span>
												</div>
												<div class="small mb-1 text-warning fw-semibold">{{
													subscription.quiz_count }} quizzes
												</div>
											</div>
											<div class="d-flex align-items-center gap-2">
												<button class="btn btn-outline-danger btn-sm unsubscribe-btn"
													@click="unsubscribeFromChapter(subscription.id)"
													title="Unsubscribe">
													<i class="bi bi-dash"></i>
												</button>
											</div>
										</div>
										<div class="subscription-meta mb-3">
											<small class="text-muted">
												<i class="bi bi-calendar-plus me-1 text-warning"></i>
												Subscribed on {{ formatDate(subscription.subscribed_on) }}
											</small>
										</div>
										<div class="subscription-footer">
											<button class="btn-auth-secondary w-100"
												@click="viewChapter(subscription.course_id, subscription.chapter_id)">
												<i class="bi bi-eye me-2"></i>View Details
											</button>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Submissions Tab -->
					<div v-if="activeTab === 'submissions'" class="tab-pane-content animate-fade-in">
						<div v-if="loading.submissions" class="text-center py-5">
							<div class="spinner-border text-primary" role="status">
								<span class="visually-hidden">Loading...</span>
							</div>
						</div>

						<div v-else-if="submissions.length === 0" class="empty-state-card glass-card">
							<div class="text-center py-5">
								<i class="bi bi-file-earmark-x text-muted mb-3"
									style="font-size: 4rem; opacity: 0.5;"></i>
								<h5 class="text-muted mb-3">No submissions yet</h5>
								<p class="text-muted mb-4">Take your first quiz to see submissions here</p>
								<button class="btn btn-outline-primary" @click="$router.push('/courses')">
									<i class="bi bi-play-circle me-2"></i>
									Start Quiz
								</button>
							</div>
						</div>

						<div v-else class="submissions-table-card glass-card">
							<div class="table-responsive">
								<table class="table table-hover submissions-table">
									<thead>
										<tr>
											<th>Quiz Name</th>
											<th>Course & Chapter</th>
											<th class="text-center">Score</th>
											<th class="text-center">Attempted On</th>
											<th class="text-center">Actions</th>
										</tr>
									</thead>
									<tbody>
										<tr v-for="submission in submissions" :key="submission.quiz_id">
											<td>
												<h6 class="mb-0 fw-semibold">{{ submission.quiz_title }}</h6>
											</td>
											<td>
												<div class="course-chapter-info">
													<div class="chapter-name mb-1"
														@click="goToChapter(submission.course_id, submission.chapter_id)"
														:title="submission.chapter_name">
														{{ submission.chapter_name }}
													</div>
													<div class="course-info">
														<span class="course-chip">
															<i class="bi bi-book me-1"></i>
															{{ submission.course_name }}
														</span>
													</div>
												</div>
											</td>
											<td class="text-center">
												<div class="score-display">
													<span class="fw-bold text-success">{{ submission.correct_answers
													}}</span>
													<span class="text-muted">/ {{ submission.total_questions }}</span>
													<div class="small text-muted">{{ formatPercentage(submission.score)
													}}%</div>
												</div>
											</td>
											<td class="text-center">
												<div class="date-display">
													<div class="fw-semibold">{{ formatDate(submission.attempted_on) }}
													</div>
													<small class="text-muted">{{
														formatTimeDuration(submission.time_duration) }}</small>
												</div>
											</td>
											<td class="text-center">
												<div class="action-buttons d-flex justify-content-center gap-2">
													<button class="btn btn-outline-primary btn-sm"
														@click="viewSubmission(submission.quiz_id)"
														title="View Submission">
														<i class="bi bi-eye"></i>
													</button>
													<button class="btn btn-primary btn-sm"
														@click="downloadCertificate(submission.quiz_id)"
														:disabled="!submission.certificate_available"
														title="Download Certificate">
														<i class="bi bi-download"></i>
													</button>
												</div>
											</td>
										</tr>
									</tbody>
								</table>
							</div>
						</div>
					</div>
				</div>
			</div>
		</section>
	</div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('upcoming')
const dashboardData = ref({})
const upcomingQuizzes = ref([])
const subscriptions = ref([])
const submissions = ref([])
const analyticsData = ref({})
const totalTimeSpent = ref(0)

const loading = reactive({
	dashboard: false,
	upcoming: false,
	analytics: false,
	subscriptions: false,
	submissions: false,
	export: false
})

const scoresChart = ref(null)
const courseChart = ref(null)
let scoresChartInstance = null
let courseChartInstance = null

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

// Load dashboard data
const loadDashboardData = async () => {
	try {
		loading.dashboard = true
		const data = await apiService.get('/user/dashboard')
		dashboardData.value = data
	} catch (error) {
		console.error('Error loading dashboard data:', error)
	} finally {
		loading.dashboard = false
	}
}

// Load upcoming quizzes
const loadUpcomingQuizzes = async () => {
	try {
		loading.upcoming = true
		const response = await apiService.get('/user/upcoming-quizzes')

		// Filter out quizzes that have already ended
		upcomingQuizzes.value = response.quizzes
			.filter(quiz => {
				// Check if quiz is still upcoming (hasn't ended)
				return isQuizUpcoming(quiz.date_of_quiz, quiz.time_duration)
			})
			.map(quiz => ({
				...quiz,
				is_live: isQuizLive(quiz.date_of_quiz, quiz.time_duration)
			}))
	} catch (error) {
		console.error('Error loading upcoming quizzes:', error)
		upcomingQuizzes.value = []
	} finally {
		loading.upcoming = false
	}
}

// Load analytics data
const loadAnalyticsData = async () => {
	try {
		loading.analytics = true
		console.log('Loading analytics data...')
		const response = await apiService.get('/user/analytics')
		console.log('Analytics response:', response)
		analyticsData.value = response

		// Wait for the DOM to be ready and charts to be available
		await nextTick()

		// Add a small delay to ensure canvas elements are fully rendered
		setTimeout(() => {
			console.log('Creating charts with data:', analyticsData.value)
			createCharts()
		}, 100)
	} catch (error) {
		console.error('Error loading analytics data:', error)
		// Set empty data to show the empty state
		analyticsData.value = {
			quiz_scores: [],
			course_attempts: []
		}
	} finally {
		loading.analytics = false
	}
}

// Load subscriptions
const loadSubscriptions = async () => {
	try {
		loading.subscriptions = true
		const response = await apiService.get('/user/subscriptions')
		subscriptions.value = response.subscriptions
	} catch (error) {
		console.error('Error loading subscriptions:', error)
		subscriptions.value = []
	} finally {
		loading.subscriptions = false
	}
}

// Load submissions
const loadSubmissions = async () => {
	try {
		loading.submissions = true
		const response = await apiService.get('/user/submissions')
		submissions.value = response.submissions
		totalTimeSpent.value = response.total_time_spent || 0
	} catch (error) {
		console.error('Error loading submissions:', error)
		submissions.value = []
	} finally {
		loading.submissions = false
	}
}

// Create charts for analytics
const createCharts = () => {
	console.log('createCharts called')
	console.log('scoresChart.value:', scoresChart.value)
	console.log('courseChart.value:', courseChart.value)
	console.log('analyticsData.value:', analyticsData.value)

	// Destroy existing charts
	if (scoresChartInstance) {
		scoresChartInstance.destroy()
		scoresChartInstance = null
	}
	if (courseChartInstance) {
		courseChartInstance.destroy()
		courseChartInstance = null
	}

	// Check if we have data
	if (!analyticsData.value) {
		console.log('No analytics data available')
		return
	}

	// Quiz Scores Bar Chart
	if (scoresChart.value && analyticsData.value.quiz_scores && analyticsData.value.quiz_scores.length > 0) {
		console.log('Creating scores chart with data:', analyticsData.value.quiz_scores)
		try {
			const ctx = scoresChart.value.getContext('2d')
			scoresChartInstance = new Chart(ctx, {
				type: 'bar',
				data: {
					labels: analyticsData.value.quiz_scores.map(q => q.quiz_title && q.quiz_title.length > 15 ?
						q.quiz_title.substring(0, 15) + '...' : q.quiz_title || 'Quiz'),
					datasets: [{
						label: 'Score (%)',
						data: analyticsData.value.quiz_scores.map(q => q.score || 0),
						backgroundColor: 'rgba(245, 124, 0, 0.7)',
						borderColor: '#f57c00',
						borderWidth: 2,
						borderRadius: 8,
						borderSkipped: false,
					}]
				},
				options: {
					responsive: true,
					maintainAspectRatio: false,
					plugins: {
						legend: {
							display: false
						}
					},
					scales: {
						y: {
							beginAtZero: true,
							max: 100,
							ticks: {
								callback: function (value) {
									return value + '%'
								}
							}
						},
						x: {
							ticks: {
								maxRotation: 45
							}
						}
					}
				}
			})
			console.log('Scores chart created successfully:', scoresChartInstance)
		} catch (error) {
			console.error('Error creating scores chart:', error)
		}
	} else {
		console.log('Cannot create scores chart - missing elements or data')
		console.log('scoresChart.value exists:', !!scoresChart.value)
		console.log('quiz_scores exists:', !!analyticsData.value?.quiz_scores)
		console.log('quiz_scores data:', analyticsData.value?.quiz_scores)
	}

	// Course Attempts Pie Chart
	if (courseChart.value && analyticsData.value.course_attempts && analyticsData.value.course_attempts.length > 0) {
		console.log('Creating course chart with data:', analyticsData.value.course_attempts)
		try {
			const ctx = courseChart.value.getContext('2d')
			const colors = ['#f57c00', '#ff9800', '#ffb74d', '#ffe0b2', '#fff3e0']

			courseChartInstance = new Chart(ctx, {
				type: 'doughnut',
				data: {
					labels: analyticsData.value.course_attempts.map(c => c.course_name || 'Course'),
					datasets: [{
						data: analyticsData.value.course_attempts.map(c => c.attempts || 0),
						backgroundColor: colors.slice(0, analyticsData.value.course_attempts.length),
						borderWidth: 2,
						borderColor: '#ffffff'
					}]
				},
				options: {
					responsive: true,
					maintainAspectRatio: false,
					plugins: {
						legend: {
							position: 'bottom',
							labels: {
								padding: 20,
								usePointStyle: true
							}
						}
					}
				}
			})
			console.log('Course chart created successfully:', courseChartInstance)
		} catch (error) {
			console.error('Error creating course chart:', error)
		}
	} else {
		console.log('Cannot create course chart - missing elements or data')
		console.log('courseChart.value exists:', !!courseChart.value)
		console.log('course_attempts exists:', !!analyticsData.value?.course_attempts)
		console.log('course_attempts data:', analyticsData.value?.course_attempts)
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

const formatDateTime = (dateString) => {
	const date = new Date(dateString)
	return new Intl.DateTimeFormat('en-US', {
		month: 'short',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit'
	}).format(date)
}

const formatDate = (dateString) => {
	const date = new Date(dateString)
	return new Intl.DateTimeFormat('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric'
	}).format(date)
}

const formatDuration = (timeString) => {
	if (!timeString) return 'All day'

	const [hours, minutes] = timeString.split(':').map(Number)
	const totalMinutes = (hours * 60) + minutes

	if (totalMinutes >= 60) {
		const h = Math.floor(totalMinutes / 60)
		const m = totalMinutes % 60
		return m > 0 ? `${h}h ${m}m` : `${h}h`
	}

	return `${totalMinutes} mins`
}

const isQuizLive = (dateString, duration) => {
	try {
		const quizStart = new Date(dateString)
		const now = new Date()

		// Parse duration properly
		let durationMinutes = 60 // Default 60 minutes
		if (duration) {
			const durationParts = duration.split(':')
			if (durationParts.length >= 2) {
				durationMinutes = parseInt(durationParts[0]) * 60 + parseInt(durationParts[1])
			} else {
				// If it's just a number, assume minutes
				durationMinutes = parseInt(duration) || 60
			}
		}

		const quizEnd = new Date(quizStart.getTime() + durationMinutes * 60000)

		return now >= quizStart && now <= quizEnd
	} catch (error) {
		console.error('Error checking if quiz is live:', error)
		return false
	}
}

const isQuizUpcoming = (dateString, duration) => {
	try {
		const quizStart = new Date(dateString)
		const now = new Date()

		// Parse duration properly
		let durationMinutes = 60 // Default 60 minutes
		if (duration) {
			const durationParts = duration.split(':')
			if (durationParts.length >= 2) {
				durationMinutes = parseInt(durationParts[0]) * 60 + parseInt(durationParts[1])
			} else {
				// If it's just a number, assume minutes
				durationMinutes = parseInt(duration) || 60
			}
		}

		const quizEnd = new Date(quizStart.getTime() + durationMinutes * 60000)

		// Quiz is upcoming if it hasn't ended yet
		return quizEnd > now
	} catch (error) {
		console.error('Error checking if quiz is upcoming:', error)
		return false
	}
}

const getTimeUntil = (dateString) => {
	try {
		const quizTime = new Date(dateString)
		const now = new Date()
		const diff = quizTime - now

		// If the quiz time has passed, it has started
		if (diff <= 0) return 'started'

		const days = Math.floor(diff / (1000 * 60 * 60 * 24))
		const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
		const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

		if (days > 0) return `in ${days}d ${hours}h`
		if (hours > 0) return `in ${hours}h ${minutes}m`
		if (minutes > 0) return `in ${minutes}m`
		return 'now'
	} catch (error) {
		console.error('Error calculating time until quiz:', error)
		return 'unknown'
	}
}

// Actions
const startQuiz = (quizId) => {
	router.push(`/quiz/${quizId}`)
}

const viewSubmission = (quizId) => {
	router.push(`/quiz/${quizId}/submission`)
}

const goToChapter = (courseId, chapterId) => {
	router.push(`/courses/${courseId}/chapters/${chapterId}`)
}

const formatTimeDuration = (durationString) => {
	if (!durationString) return 'N/A'

	// If it's already in the format we want, return it
	if (durationString.includes('min') || durationString.includes('sec')) {
		return durationString
	}

	// Try to parse different time formats
	try {
		// If it's in HH:MM:SS format
		if (durationString.includes(':')) {
			const parts = durationString.split(':')
			if (parts.length === 3) {
				const hours = parseInt(parts[0])
				const minutes = parseInt(parts[1])
				const seconds = parseInt(parts[2])

				const totalMinutes = hours * 60 + minutes
				const totalSeconds = totalMinutes * 60 + seconds

				if (totalMinutes > 0) {
					return `${totalMinutes}min ${seconds}sec`
				} else {
					return `${totalSeconds}sec`
				}
			}
		}

		// If it's a number (assuming seconds)
		const timeInSeconds = parseInt(durationString)
		if (!isNaN(timeInSeconds)) {
			const minutes = Math.floor(timeInSeconds / 60)
			const seconds = timeInSeconds % 60

			if (minutes > 0) {
				return `${minutes}min ${seconds}sec`
			} else {
				return `${timeInSeconds}sec`
			}
		}

		return durationString
	} catch (error) {
		return durationString
	}
}

const downloadCertificate = async (quizId) => {
	try {
		const token = authStore.token
		const response = await fetch(`http://localhost:5000/certificate/${quizId}/download`, {
			headers: {
				'Authorization': `Bearer ${token}`
			}
		})

		if (response.ok) {
			const blob = await response.blob()
			const url = window.URL.createObjectURL(blob)
			const a = document.createElement('a')
			a.href = url
			a.download = `certificate_quiz_${quizId}.pdf`
			document.body.appendChild(a)
			a.click()
			window.URL.revokeObjectURL(url)
			document.body.removeChild(a)
		} else {
			console.error('Failed to download certificate')
		}
	} catch (error) {
		console.error('Error downloading certificate:', error)
	}
}

const viewChapter = (courseId, chapterId) => {
	router.push(`/course/${courseId}/chapter/${chapterId}`)
}

const unsubscribeFromChapter = async (subscriptionId) => {
	if (!confirm('Are you sure you want to unsubscribe from this chapter?')) {
		return
	}

	try {
		const token = authStore.token
		const response = await fetch(`http://localhost:5000/api/user/unsubscribe/${subscriptionId}`, {
			method: 'DELETE',
			headers: {
				'Authorization': `Bearer ${token}`,
				'Content-Type': 'application/json'
			}
		})

		if (response.ok) {
			// Remove from local state
			subscriptions.value = subscriptions.value.filter(sub => sub.id !== subscriptionId)
			// Reload dashboard stats to reflect change
			await loadDashboardData()
		} else {
			console.error('Failed to unsubscribe')
		}
	} catch (error) {
		console.error('Error unsubscribing:', error)
	}
}

const exportUserData = async () => {
	try {
		loading.export = true
		const token = authStore.token
		const response = await fetch(`http://localhost:5000/api/user/export-data`, {
			headers: {
				'Authorization': `Bearer ${token}`
			}
		})

		if (response.ok) {
			const blob = await response.blob()
			const url = window.URL.createObjectURL(blob)
			const a = document.createElement('a')
			a.href = url
			a.download = `user_data_${authStore.userName}_${new Date().toISOString().split('T')[0]}.csv`
			document.body.appendChild(a)
			a.click()
			window.URL.revokeObjectURL(url)
			document.body.removeChild(a)
		} else {
			console.error('Failed to export user data')
			alert('Failed to export data. Please try again.')
		}
	} catch (error) {
		console.error('Error exporting user data:', error)
		alert('Error exporting data. Please try again.')
	} finally {
		loading.export = false
	}
}

// Load data based on active tab
const loadTabData = async (tab) => {
	switch (tab) {
		case 'upcoming':
			await loadUpcomingQuizzes()
			break
		case 'analytics':
			await loadAnalyticsData()
			break
		case 'subscriptions':
			await loadSubscriptions()
			break
		case 'submissions':
			await loadSubmissions()
			break
	}
}

// Watch for tab changes
const handleTabChange = async (tab) => {
	activeTab.value = tab
	await nextTick() // Wait for DOM to update
	await loadTabData(tab)
}

// Initialize dashboard
onMounted(async () => {
	await loadDashboardData()
	await loadUpcomingQuizzes()

	// Add window resize handler for charts
	window.addEventListener('resize', () => {
		if (scoresChartInstance) {
			scoresChartInstance.resize()
		}
		if (courseChartInstance) {
			courseChartInstance.resize()
		}
	})
})

// Cleanup on unmount
onUnmounted(() => {
	if (scoresChartInstance) {
		scoresChartInstance.destroy()
	}
	if (courseChartInstance) {
		courseChartInstance.destroy()
	}
	window.removeEventListener('resize', () => { })
})
</script>

<style scoped>
/* User Dashboard Styles - Matching Admin Dashboard */
.user-dashboard {
	min-height: 100vh;
	background: linear-gradient(135deg, rgba(245, 124, 0, 0.05) 0%, rgba(245, 124, 0, 0.02) 100%);
}

/* Hero Header Section */
.dashboard-header {
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

.username-link {
	text-decoration: none;
	color: inherit;
	transition: all 0.3s ease;
}

.username-link:hover {
	text-decoration: none;
	color: inherit;
}

.username-link:hover .text-gradient {
	transform: scale(1.02);
}

.text-gradient {
	background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
	-webkit-background-clip: text;
	-webkit-text-fill-color: transparent;
	background-clip: text;
	transition: all 0.3s ease;
}

/* Stats Cards - Matching Admin Dashboard */
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

/* Navigation Tabs - Matching Admin Quiz Management */
.quiz-tabs-nav {
	margin-bottom: 1.5rem;
}

.quiz-tabs-nav .nav-pills {
	background: rgba(255, 255, 255, 0.9);
	backdrop-filter: blur(20px);
	border: 1px solid rgba(245, 124, 0, 0.1);
	border-radius: 20px;
	padding: 0.5rem;
	box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
}

.quiz-tabs-nav .nav-link {
	border: none;
	border-radius: 15px;
	color: #6c757d;
	font-weight: 600;
	padding: 1rem 1.5rem;
	transition: all 0.3s ease;
	background: transparent;
	margin: 0 0.25rem;
}

.quiz-tabs-nav .nav-link:hover {
	background: rgba(245, 124, 0, 0.1);
	color: #f57c00;
	transform: translateY(-2px);
}

.quiz-tabs-nav .nav-link.active {
	background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
	color: white !important;
	box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
	transform: translateY(-2px);
}

.quiz-tabs-nav .nav-link.active i {
	color: white !important;
}

.quiz-tabs-nav .nav-link i {
	font-size: 1rem;
}

/* Empty State Cards */
.empty-state-card {
	background: rgba(255, 255, 255, 0.9);
	backdrop-filter: blur(20px);
	border: 1px solid rgba(245, 124, 0, 0.1);
	border-radius: 20px;
	box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
	padding: 3rem 2rem;
	text-align: center;
}

/* Quiz Cards */
.quiz-card {
	height: 100%;
	position: relative;
	transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.quiz-card:hover {
	transform: translateY(-8px);
	box-shadow: 0 25px 50px rgba(245, 124, 0, 0.15);
}

.quiz-card:hover .quiz-title {
	color: #f57c00;
}

.quiz-title {
	transition: color 0.3s ease;
}

.course-chip {
	display: inline-block;
}

.course-badge {
	background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
	color: white;
	padding: 0.25rem 0.75rem;
	border-radius: 20px;
	font-size: 0.75rem;
	font-weight: 600;
}

.quiz-start-info {
	border-radius: 8px;
	text-align: center;
	font-weight: 500;
	width: fit-content;
}


.live-quiz-card {
	border: 2px solid #dc3545 !important;
	animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
	0% {
		box-shadow: 0 8px 32px rgba(220, 53, 69, 0.3);
	}

	50% {
		box-shadow: 0 8px 32px rgba(220, 53, 69, 0.6);
	}

	100% {
		box-shadow: 0 8px 32px rgba(220, 53, 69, 0.3);
	}
}

.live-badge .pulse-animation {
	animation: pulse 1.5s infinite;
}

@keyframes pulse {
	0% {
		opacity: 1;
		transform: scale(1);
	}

	50% {
		opacity: 0.8;
		transform: scale(1.05);
	}

	100% {
		opacity: 1;
		transform: scale(1);
	}
}

/* Chart Cards */
.chart-card {
	background: rgba(255, 255, 255, 0.9);
	backdrop-filter: blur(20px);
	border: 1px solid rgba(245, 124, 0, 0.1);
	border-radius: 20px;
	padding: 2rem;
	box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
	transition: all 0.3s ease;
	height: 100%;
}

.chart-card:hover {
	box-shadow: 0 12px 40px rgba(245, 124, 0, 0.15);
	border-color: rgba(245, 124, 0, 0.2);
}

.chart-card .card-header {
	background: linear-gradient(135deg, rgba(248, 249, 250, 0.8) 0%, rgba(255, 255, 255, 0.9) 100%);
	border-bottom: 1px solid rgba(245, 124, 0, 0.1);
	padding: 1.5rem;
	margin: -2rem -2rem 1.5rem -2rem;
	border-radius: 20px 20px 0 0;
}

.chart-container {
	height: 350px;
	padding: 0;
}

/* Subscription Cards */
.subscription-card {
	height: 100%;
	transition: all 0.3s ease;
}

.subscription-card:hover {
	transform: translateY(-4px);
	box-shadow: 0 20px 40px rgba(245, 124, 0, 0.15);
}

.subscription-card:hover .subscription-title {
	color: #f57c00;
}

.subscription-title {
	transition: color 0.3s ease;
}

.quiz-count-info {
	background: rgba(245, 124, 0, 0.1);
	border: 1px solid rgba(245, 124, 0, 0.2);
	border-radius: 8px;
	padding: 0.5rem;
	min-width: 60px;
}

.quiz-count-number {
	font-size: 1.25rem;
	font-weight: bold;
	color: #f57c00;
	line-height: 1;
}

.unsubscribe-btn {
	border-radius: 50%;
	width: 32px;
	height: 32px;
	padding: 0;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.3s ease;
}

.unsubscribe-btn:hover {
	background-color: #dc3545;
	border-color: #dc3545;
	color: white;
	transform: scale(1.1);
}


.bi-calendar-plus.text-warning {
	color: #f57c00 !important;
}

/* Submissions Table */
.submissions-table-card {
	overflow: hidden;
}

.submissions-table {
	margin: 0;
	border: none;
}

.submissions-table thead {
	background: linear-gradient(135deg, rgba(248, 249, 250, 0.8) 0%, rgba(255, 255, 255, 0.9) 100%);
}

.submissions-table th {
	border: none;
	font-weight: 600;
	color: var(--text-primary);
	padding: 1.5rem 1rem;
	border-bottom: 2px solid rgba(245, 124, 0, 0.1);
	font-family: 'Poppins', sans-serif;
}

.submissions-table td {
	border: none;
	padding: 1.5rem 1rem;
	border-bottom: 1px solid rgba(0, 0, 0, 0.05);
	vertical-align: middle;
}

.submissions-table tr:hover {
	background: rgba(245, 124, 0, 0.05);
}

.score-display,
.date-display {
	text-align: center;
}

/* Modern Button Style (matching landing page) */
.modern-btn {
	border-radius: 16px;
	font-weight: 600;
	font-family: 'Inter', sans-serif;
	transition: all 0.3s ease;
	position: relative;
	overflow: hidden;
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
	z-index: 1;
}

.modern-btn:hover::before {
	left: 100%;
}

.btn-outline-primary.modern-btn {
	border: 2px solid #f57c00;
	color: #f57c00;
	background: transparent;
}

.btn-outline-primary.modern-btn:hover {
	background: #f57c00;
	color: white;
	border-color: #f57c00;
}

.btn-outline-primary.modern-btn:disabled {
	opacity: 0.6;
	cursor: not-allowed;
	border-color: #ccc;
	color: #ccc;
}

.btn-outline-primary.modern-btn:disabled:hover {
	background: transparent;
	color: #ccc;
	border-color: #ccc;
}

.badge {
	border-radius: 8px;
	font-weight: 500;
	padding: 0.5rem 0.75rem;
	font-size: 0.75rem;
}

.badge-primary {
	background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
	color: white;
}

.badge-secondary {
	background: #6c757d;
	color: white;
}

.badge-outline {
	background: transparent;
	border: 1px solid var(--primary);
	color: var(--primary);
}

/* Course Chapter Info */
.course-chapter-info {
	display: flex;
	flex-direction: column;
	gap: 0.5rem;
}

.chapter-name {
	font-size: 1rem;
	font-weight: 600;
	color: #2c3e50;
	cursor: pointer;
	transition: color 0.3s ease;
	line-height: 1.3;
}

.chapter-name:hover {
	color: #f57c00;
}

.course-chip {
	background: rgba(245, 124, 0, 0.1);
	color: #f57c00;
	border: 1px solid rgba(245, 124, 0, 0.2);
	padding: 0.25rem 0.75rem;
	border-radius: 20px;
	font-size: 0.8rem;
	font-weight: 600;
	display: inline-flex;
	align-items: center;
	max-width: fit-content;
}

/* Action Buttons */
.action-buttons .btn {
	border-radius: 8px;
	width: 36px;
	height: 36px;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.2s ease;
}

.action-buttons .btn:disabled {
	opacity: 0.4;
	cursor: not-allowed;
}

.action-buttons .btn:not(:disabled):hover {
	transform: scale(1.1);
}

/* Course Badge Styling */
.course-badge {
	background: rgba(245, 124, 0, 0.1);
	color: #f57c00;
	border: 1px solid rgba(245, 124, 0, 0.2);
	border-radius: 25px;
	font-size: 0.9rem;
	font-weight: 500;
	display: inline-block;
}

/* View Details Button Styling */
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

/* Responsive Design */
@media (max-width: 1200px) {
	.hero-title {
		font-size: 2.5rem;
	}

	.quiz-tabs-nav .nav-link {
		padding: 0.9rem 1.3rem;
		font-size: 0.95rem;
	}
}

@media (max-width: 992px) {
	.hero-title {
		font-size: 2.2rem;
	}

	.stats-number {
		font-size: 2.2rem;
	}

	.quiz-tabs-nav .nav-link {
		padding: 0.8rem 1.1rem;
		font-size: 0.9rem;
	}

	.chart-container {
		height: 300px;
	}

	/* Make dashboard header responsive */
	.dashboard-header .col-lg-8,
	.dashboard-header .col-lg-4 {
		text-align: center;
	}

	.text-lg-end {
		text-align: center !important;
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

	.quiz-tabs-nav .nav-link {
		padding: 0.75rem 1rem;
		font-size: 0.85rem;
	}

	.chart-container {
		height: 250px;
		padding: 1rem;
	}

	.submissions-table-card {
		overflow-x: auto;
	}

	.action-buttons {
		flex-direction: column;
		gap: 0.5rem !important;
	}

	/* Mobile: 1 card per row */
	.col-xl-4.col-md-6 {
		flex: 0 0 100%;
		max-width: 100%;
	}

	/* Make username link responsive */
	.username-link h3 {
		font-size: 1.5rem;
	}

	/* Stack dashboard header vertically */
	.dashboard-header .row {
		text-align: center;
	}

	.dashboard-header .col-lg-4 {
		margin-top: 1rem;
	}
}

@media (max-width: 576px) {
	.hero-title {
		font-size: 1.5rem;
	}

	.stats-number {
		font-size: 1.8rem;
	}

	.username-link h3 {
		font-size: 1.3rem;
	}

	.quiz-tabs-nav .nav-link {
		padding: 0.6rem 0.8rem;
		font-size: 0.8rem;
	}

	.quiz-tabs-nav .nav-link i {
		font-size: 0.9rem;
	}

	.modern-btn {
		padding: 10px 24px;
		font-size: 0.9rem;
	}

	.chart-container {
		height: 200px;
		padding: 0.5rem;
	}

	/* Reduce padding for small screens */
	.stats-section {
		padding-top: 2rem !important;
	}

	.main-content {
		padding-bottom: 2rem !important;
	}
}

@media (min-width: 768px) and (max-width: 1199px) {

	/* Tablet: 2 cards per row */
	.col-xl-4.col-md-6 {
		flex: 0 0 50%;
		max-width: 50%;
	}
}

@media (min-width: 1200px) {

	/* Desktop: 3 cards per row */
	.col-xl-4.col-md-6 {
		flex: 0 0 33.333333%;
		max-width: 33.333333%;
	}
}

/* Loading States */
.spinner-border.text-primary {
	width: 3rem;
	height: 3rem;
	color: var(--primary) !important;
}

/* Animations */
.animate-fade-in {
	animation: fadeIn 0.6s ease-out;
}

.animate-slide-up {
	animation: slideUp 0.8s ease-out;
}

@keyframes fadeIn {
	from {
		opacity: 0;
		transform: translateY(20px);
	}

	to {
		opacity: 1;
		transform: translateY(0);
	}
}

@keyframes slideUp {
	from {
		opacity: 0;
		transform: translateY(30px);
	}

	to {
		opacity: 1;
		transform: translateY(0);
	}
}

/* Additional Theme Consistency */
.text-primary {
	color: var(--primary) !important;
}

.bg-blur {
	backdrop-filter: blur(10px);
	-webkit-backdrop-filter: blur(10px);
}
</style>

<template>
    <div class="quiz-result-container">
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <!-- Result Header -->
                    <div class="result-header text-center mb-5">
                        <div class="result-icon mb-4">
                            <i class="bi bi-trophy" :class="getScoreClass()"></i>
                        </div>
                        <h2 class="result-title fw-bold mb-3">Quiz Completed!</h2>
                        <h4 class="quiz-name text-muted mb-4">{{ quizData.title }}</h4>

                        <!-- Score Display -->
                        <div class="score-display mb-4">
                            <div class="score-card">
                                <div class="score-main">
                                    <span class="score-obtained">{{ result.obtained_marks }}</span>
                                    <span class="score-separator">/</span>
                                    <span class="score-total">{{ result.total_marks }}</span>
                                </div>
                                <div class="score-percentage mt-2">
                                    <span class="percentage-value" :class="getScoreClass()">
                                        {{ Math.round(result.percentage) }}%
                                    </span>
                                </div>
                            </div>
                        </div>

                        <!-- Performance Message -->
                        <div class="performance-message mb-4">
                            <p class="performance-text" :class="getScoreClass()">
                                {{ getPerformanceMessage() }}
                            </p>
                        </div>
                    </div>

                    <!-- Actions -->
                    <div class="result-actions text-center mb-5">
                        <div class="row g-3 justify-content-center">
                            <div class="col-auto">
                                <button class="btn btn-cta btn-lg px-4" @click="viewSubmission">
                                    <i class="bi bi-eye me-2"></i>
                                    View Submission
                                </button>
                            </div>
                            <div class="col-auto">
                                <button class="btn btn-success btn-lg px-4" @click="downloadCertificate"
                                    :disabled="certificateLoading">
                                    <i v-if="certificateLoading" class="bi bi-hourglass-split me-2"></i>
                                    <i v-else class="bi bi-download me-2"></i>
                                    {{ certificateLoading ? 'Generating...' : 'Download Certificate' }}
                                </button>
                            </div>
                            <div class="col-auto">
                                <button class="btn btn-outline-primary btn-lg px-4" @click="goToDashboard">
                                    <i class="bi bi-house me-2"></i>
                                    Go to Dashboard
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Detailed Results -->
                    <div class="detailed-results">
                        <div class="results-card">
                            <h5 class="fw-bold mb-4">
                                <i class="bi bi-list-check me-2"></i>
                                Question Summary
                            </h5>

                            <div class="row g-4 mb-4">
                                <div class="col-md-3 col-6">
                                    <div class="stat-card text-center">
                                        <div class="stat-value text-success">{{ result.correct_answers }}</div>
                                        <div class="stat-label">Correct</div>
                                    </div>
                                </div>
                                <div class="col-md-3 col-6">
                                    <div class="stat-card text-center">
                                        <div class="stat-value text-danger">{{ result.incorrect_answers }}</div>
                                        <div class="stat-label">Incorrect</div>
                                    </div>
                                </div>
                                <div class="col-md-3 col-6">
                                    <div class="stat-card text-center">
                                        <div class="stat-value text-warning">{{ result.unanswered }}</div>
                                        <div class="stat-label">Unanswered</div>
                                    </div>
                                </div>
                                <div class="col-md-3 col-6">
                                    <div class="stat-card text-center">
                                        <div class="stat-value text-info">{{ result.total_questions }}</div>
                                        <div class="stat-label">Total</div>
                                    </div>
                                </div>
                            </div>

                            <!-- Performance Chart -->
                            <div class="performance-chart mb-4" v-if="result.total_questions > 0">
                                <div class="chart-header mb-3">
                                    <h6 class="fw-semibold mb-0">Performance Breakdown</h6>
                                </div>
                                <div class="progress-stack">
                                    <div class="progress mb-2" style="height: 20px;">
                                        <div class="progress-bar bg-success"
                                            :style="{ width: (result.correct_answers / result.total_questions * 100) + '%' }"
                                            :title="`Correct: ${result.correct_answers}`"></div>
                                        <div class="progress-bar bg-danger"
                                            :style="{ width: (result.incorrect_answers / result.total_questions * 100) + '%' }"
                                            :title="`Incorrect: ${result.incorrect_answers}`"></div>
                                        <div class="progress-bar bg-warning"
                                            :style="{ width: (result.unanswered / result.total_questions * 100) + '%' }"
                                            :title="`Unanswered: ${result.unanswered}`"></div>
                                    </div>
                                    <div class="progress-legend d-flex justify-content-between small">
                                        <span class="text-success">Correct ({{ Math.round(result.correct_answers /
                                            result.total_questions * 100) }}%)</span>
                                        <span class="text-danger">Incorrect ({{ Math.round(result.incorrect_answers /
                                            result.total_questions * 100) }}%)</span>
                                        <span class="text-warning">Unanswered ({{ Math.round(result.unanswered /
                                            result.total_questions * 100) }}%)</span>
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

<script>
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
    name: 'QuizResult',
    props: {
        result: {
            type: Object,
            required: true
        },
        quizData: {
            type: Object,
            required: true
        }
    },
    setup() {
        const router = useRouter()
        return { router }
    },
    data() {
        return {
            certificateLoading: false
        }
    },
    methods: {
        getScoreClass() {
            const percentage = this.result.percentage
            if (percentage >= 80) return 'text-success'
            if (percentage >= 60) return 'text-warning'
            return 'text-danger'
        },

        getPerformanceMessage() {
            const percentage = this.result.percentage
            if (percentage >= 90) return '🎉 Excellent performance! Outstanding work!'
            if (percentage >= 80) return '👏 Great job! You did very well!'
            if (percentage >= 70) return '👍 Good work! Well done!'
            if (percentage >= 60) return '🔄 Not bad! You can improve with practice!'
            return '📚 Keep practicing! You\'ll get better with time!'
        },

        async downloadCertificate() {
            try {
                this.certificateLoading = true

                console.log('Downloading certificate for quiz:', this.quizData.id)
                const response = await axios.get(`/user/quiz/${this.quizData.id}/certificate`, {
                    responseType: 'blob'
                })

                console.log('Certificate response:', response)

                // Check if response is actually a PDF
                if (response.headers['content-type'] !== 'application/pdf') {
                    throw new Error('Invalid response format - expected PDF')
                }

                // Create download link
                const url = window.URL.createObjectURL(new Blob([response.data]))
                const link = document.createElement('a')
                link.href = url
                link.setAttribute('download', `${this.quizData.title.replace(/[^a-zA-Z0-9]/g, '_')}_certificate.pdf`)
                document.body.appendChild(link)
                link.click()
                link.remove()
                window.URL.revokeObjectURL(url)

                console.log('Certificate downloaded successfully')

            } catch (error) {
                console.error('Error downloading certificate:', error)
                alert('Failed to download certificate: ' + (error.response?.data?.message || error.message || 'Unknown error'))
            } finally {
                this.certificateLoading = false
            }
        },

        viewSubmission() {
            // Navigate to a detailed submission view or show quiz details
            this.router.push(`/quiz/${this.quizData.id}/result`)
        },

        goToDashboard() {
            this.router.push('/dashboard')
        }
    }
}
</script>

<style scoped>
.quiz-result-container {
    min-height: 100vh;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    padding-top: 2rem;
}

.result-header {
    background: white;
    border-radius: 20px;
    padding: 3rem 2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
}

.result-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}

.result-title {
    font-size: 2.5rem;
    color: #2c3e50;
}

.quiz-name {
    font-size: 1.2rem;
    color: #6c757d;
}

.score-display {
    margin: 2rem 0;
}

.score-card {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 16px;
    padding: 2rem;
    display: inline-block;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.score-main {
    font-size: 3rem;
    font-weight: 700;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    color: #2c3e50;
}

.score-obtained {
    color: #f57c00;
}

.score-separator {
    color: #6c757d;
    margin: 0 0.5rem;
}

.score-total {
    color: #6c757d;
}

.score-percentage {
    font-size: 1.5rem;
    font-weight: 600;
}

.percentage-value {
    font-size: 2rem;
    font-weight: 700;
}

.performance-message {
    font-size: 1.1rem;
    font-weight: 500;
}

.performance-text {
    margin: 0;
    padding: 1rem 2rem;
    background: rgba(245, 124, 0, 0.1);
    border-radius: 12px;
    border-left: 4px solid #f57c00;
}

.btn-cta {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    color: white;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.btn-cta:hover:not(:disabled) {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(245, 124, 0, 0.4);
    color: white;
}

.btn-cta:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
}

.btn-outline-primary {
    border: 2px solid #f57c00;
    color: #f57c00;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.btn-outline-primary:hover {
    background: #f57c00;
    border-color: #f57c00;
    color: white;
    transform: translateY(-2px);
}

.results-card {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.stat-card {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 1.5rem 1rem;
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.stat-value {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.stat-label {
    font-size: 0.9rem;
    font-weight: 500;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.chart-header {
    padding-bottom: 1rem;
    border-bottom: 2px solid #f8f9fa;
}

.progress-stack {
    margin-top: 1rem;
}

.progress {
    background-color: #f8f9fa;
    border-radius: 10px;
    overflow: hidden;
}

.progress-bar {
    transition: width 0.6s ease;
}

.progress-legend {
    font-size: 0.875rem;
    margin-top: 0.5rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .result-header {
        padding: 2rem 1.5rem;
        margin-bottom: 1.5rem;
    }

    .result-title {
        font-size: 2rem;
    }

    .score-main {
        font-size: 2.5rem;
    }

    .percentage-value {
        font-size: 1.5rem;
    }

    .result-icon {
        font-size: 3rem;
    }

    .results-card {
        padding: 1.5rem;
    }

    .stat-card {
        padding: 1rem 0.5rem;
    }

    .stat-value {
        font-size: 1.5rem;
    }
}

@media (max-width: 576px) {
    .quiz-result-container {
        padding-top: 1rem;
    }

    .result-header {
        padding: 1.5rem 1rem;
    }

    .score-card {
        padding: 1.5rem;
    }

    .score-main {
        font-size: 2rem;
    }

    .performance-text {
        padding: 0.75rem 1rem;
        font-size: 1rem;
    }

    .result-actions .btn {
        width: 100%;
        margin-bottom: 1rem;
    }
}
</style>

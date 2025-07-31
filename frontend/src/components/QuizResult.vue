<template>
    <div class="quiz-result-container">
        <!-- Back to Dashboard Button -->
        <div class="container-fluid py-3">
            <div class="row">
                <div class="col-12">
                    <button @click="goToDashboard" class="btn btn-back d-flex align-items-center">
                        <i class="bi bi-arrow-left me-2"></i>
                        Back to Dashboard
                    </button>
                </div>
            </div>
        </div>

        <div class="container-fluid">
            <div class="row justify-content-center">
                <div class="col-lg-8 col-md-10">
                    <!-- Result Header -->
                    <div class="result-header text-center">
                        <div class="result-icon">
                            <i class="bi bi-check-circle"></i>
                        </div>
                        <h2 class="result-title mb-2">Quiz Completed!</h2>
                        <div class="quiz-info mb-4">
                            <h1 class="quiz-name">{{ result.quiz_title }}</h1>
                            <div class="chapter-name">{{ result.chapter }}</div>
                            <div class="course-info mt-2">
                                <span class="course-chip">{{ result.course }}</span>
                            </div>
                        </div>

                        <!-- Main Results Display -->
                        <div class="results-summary mt-5">
                            <div class="row g-4 align-items-center">
                                <!-- Marks Section (Left) -->
                                <div class="col-md-4">
                                    <div class="score-section">
                                        <div class="score-label">Score</div>
                                        <div class="score-value">
                                            <span class="score-obtained">{{ result.obtained_marks }}</span>
                                            <span class="score-separator">/</span>
                                            <span class="score-total">{{ result.total_marks }}</span>
                                        </div>
                                        <div class="score-subtitle">marks</div>
                                    </div>
                                </div>

                                <!-- Percentage Section (Center) -->
                                <div class="col-md-4">
                                    <div class="percentage-section">
                                        <div class="percentage-circle">
                                            <div class="percentage-value">{{ Math.round(result.percentage) }}%</div>
                                        </div>
                                        <div class="percentage-label">Percentage</div>
                                    </div>
                                </div>

                                <!-- Answered/Unanswered Section (Right) -->
                                <div class="col-md-4">
                                    <div class="answer-stats">
                                        <div class="answered-section">
                                            <div class="stat-label">Answered</div>
                                            <div class="stat-value">{{ result.correct_answers + result.incorrect_answers
                                                }}/{{ result.total_questions }}</div>
                                        </div>
                                        <div class="unanswered-section mt-2">
                                            <div class="stat-label-small">Unanswered</div>
                                            <div class="stat-value-small">{{ result.unanswered }}</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Action Buttons -->
                        <div class="result-actions mt-5">
                            <div class="d-flex flex-wrap justify-content-center gap-3">
                                <button @click="viewSubmission" class="btn btn-cta btn-lg px-5 py-3">
                                    <i class="bi bi-eye me-2"></i>
                                    View Submission
                                </button>

                                <button @click="downloadCertificate" class="btn btn-outline-orange btn-lg px-5 py-3"
                                    :disabled="certificateLoading">
                                    <i class="bi bi-download me-2"></i>
                                    <span v-if="certificateLoading">Generating...</span>
                                    <span v-else>Download Certificate</span>
                                </button>
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
        async downloadCertificate() {
            if (!this.result.submission_id) {
                alert('No submission ID found. Cannot download certificate.')
                return
            }

            this.certificateLoading = true

            try {
                const token = localStorage.getItem('authToken')
                const response = await axios.get(
                    `http://localhost:5000/api/user/submissions/${this.result.submission_id}/certificate`,
                    {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        },
                        responseType: 'blob'
                    }
                )

                // Create blob link to download
                const url = window.URL.createObjectURL(new Blob([response.data]))
                const link = document.createElement('a')
                link.href = url

                // Use quiz title for filename
                const filename = `${this.result.quiz_title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_certificate.pdf`
                link.setAttribute('download', filename)

                // Append to html link element page
                document.body.appendChild(link)

                // Start download
                link.click()

                // Clean up and remove the link
                link.parentNode.removeChild(link)
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
            // Navigate to the detailed submission view
            this.router.push(`/quiz/${this.result.quiz_id}/submission`)
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
    background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    padding-top: 2rem;
}

.result-header {
    background: white;
    border-radius: 20px;
    padding: 3rem 2rem;
    box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
    margin-bottom: 2rem;
}

.result-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    color: #f57c00;
}

.result-title {
    font-size: 1.8rem;
    color: #2c3e50;
}

.quiz-info {
    text-align: center;
}

.quiz-name {
    font-size: 2.2rem;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 0.5rem;
}

.chapter-name {
    font-size: 1.1rem;
    color: #2c3e50;
    font-weight: 500;
    margin-bottom: 0.5rem;
}

.course-info {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.course-chip {
    background: rgba(245, 124, 0, 0.1);
    color: #f57c00;
    border: 1px solid rgba(245, 124, 0, 0.2);
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-size: 0.9rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
}

.results-summary {
    margin: 2rem 0;
}

/* Score Section (Left) */
.score-section {
    text-align: center;
}

.score-label {
    font-size: 1rem;
    font-weight: 600;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
}

.score-value {
    font-size: 2.5rem;
    font-weight: 700;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.score-subtitle {
    font-size: 0.9rem;
    color: #6c757d;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 0.25rem;
}

.score-obtained {
    color: #f57c00;
}

.score-separator {
    color: #6c757d;
    margin: 0 0.3rem;
}

.score-total {
    color: #6c757d;
}

/* Percentage Section (Center) */
.percentage-section {
    text-align: center;
}

.percentage-circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
    box-shadow: 0 8px 25px rgba(245, 124, 0, 0.3);
}

.percentage-value {
    font-size: 2rem;
    font-weight: 700;
    color: white;
}

.percentage-label {
    font-size: 0.9rem;
    color: #6c757d;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 0.75rem;
}

/* Answer Stats Section (Right) */
.answer-stats {
    text-align: center;
}

.answered-section {
    margin-bottom: 0.5rem;
}

.stat-label {
    font-size: 1rem;
    font-weight: 600;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.25rem;
}

.stat-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #2c3e50;
}

.stat-label-small {
    font-size: 0.85rem;
    font-weight: 500;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.25rem;
}

.stat-value-small {
    font-size: 1.2rem;
    font-weight: 600;
    color: #f57c00;
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

.btn-outline-secondary {
    border: 2px solid #6c757d;
    color: #6c757d;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    background: transparent;
}

.btn-outline-secondary:hover {
    background: #6c757d;
    border-color: #6c757d;
    color: white;
    transform: translateY(-2px);
}

.btn-outline-orange {
    border: 2px solid #f57c00;
    color: #f57c00;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    background: transparent;
}

.btn-outline-orange:hover:not(:disabled) {
    background: #f57c00;
    border-color: #f57c00;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.btn-outline-orange:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
    border-color: #f57c00;
    color: #f57c00;
}

/* Responsive Design */
@media (max-width: 768px) {
    .result-header {
        padding: 2rem 1.5rem;
        margin-bottom: 1.5rem;
    }

    .result-title {
        font-size: 1.5rem;
    }

    .quiz-name {
        font-size: 1.8rem;
    }

    .chapter-name {
        font-size: 1rem;
    }

    .course-info {
        gap: 0.5rem;
    }

    .course-chip {
        font-size: 0.8rem;
        padding: 0.4rem 0.8rem;
    }

    .score-value {
        font-size: 2rem;
    }

    .percentage-circle {
        width: 100px;
        height: 100px;
    }

    .percentage-value {
        font-size: 1.5rem;
    }

    .result-icon {
        font-size: 3rem;
    }

    .results-summary .row {
        text-align: center;
    }

    .results-summary .col-md-4 {
        margin-bottom: 1.5rem;
    }
}

@media (max-width: 576px) {
    .quiz-result-container {
        padding-top: 1rem;
    }

    .result-header {
        padding: 1.5rem 1rem;
    }

    .quiz-name {
        font-size: 1.5rem;
    }

    .chapter-name {
        font-size: 0.9rem;
    }

    .course-info {
        flex-direction: column;
        gap: 0.5rem;
    }

    .score-value {
        font-size: 1.8rem;
    }

    .percentage-circle {
        width: 90px;
        height: 90px;
    }

    .percentage-value {
        font-size: 1.3rem;
    }

    .result-actions .btn {
        width: 100%;
        margin-bottom: 1rem;
        font-size: 1rem;
        padding: 0.75rem 1rem !important;
    }

    .stat-value {
        font-size: 1.5rem;
    }
}
</style>

<style scoped>
.btn-back {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    color: #6c757d;
    font-size: 14px;
}

.btn-back:hover {
    background-color: #f8f9fa;
    border-color: #6c757d;
    color: #495057;
}
</style>

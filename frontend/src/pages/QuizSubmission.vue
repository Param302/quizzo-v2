<template>
    <div class="quiz-submission-page">
        <!-- Submission Content -->
        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger mx-3 mt-3">
            {{ error }}
        </div>

        <!-- Submission Content -->
        <div v-else-if="submissionData" class="submission-content">
            <!-- Header Section -->
            <section class="submission-header py-4">
                <div class="container">
                    <div class="row align-items-center mb-3">
                        <div class="col-12 d-flex justify-content-between align-items-center">
                            <button @click="goToDashboard" class="btn btn-back d-flex align-items-center">
                                <i class="bi bi-arrow-left me-2"></i>
                                Back to Dashboard
                            </button>
                            <div class="flex-grow-1"></div>
                        </div>
                    </div>
                    <div class="row align-items-center">
                        <div class="col-lg-8">
                            <h1 class="display-6 fw-bold mb-2" style="color: #2c3e50;">{{ submissionData.quiz_title }}</h1>
                            <p class="lead fw-medium mb-2">{{ submissionData.chapter }}</p>
                            <div class="course-info">
                                <span class="course-chip">
                                    <i class="bi bi-book me-1"></i>
                                    {{ submissionData.course }}
                                </span>
                            </div>
                        </div>
                        <div class="col-lg-4 text-lg-end mt-3 mt-lg-0">
                            <div class="score-display">
                                <div class="score-main">
                                    <span class="score-obtained">{{ submissionData.obtained_marks }}</span>
                                    <span class="score-separator">/</span>
                                    <span class="score-total">{{ submissionData.total_marks }}</span>
                                </div>
                                <div class="score-percentage">
                                    {{ Math.round(submissionData.percentage) }}% Achieved
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Questions Section -->
            <section class="questions-section py-4">
                <div class="container">
                    <div class="row justify-content-center">
                        <div class="col-lg-10 col-xl-8">
                            <div v-for="(question, index) in submissionData.questions" :key="question.question_id" 
                                 class="question-card mb-4">
                                <!-- Question Header -->
                                <div class="question-header">
                                    <div class="question-meta">
                                        <span class="question-number">Q{{ index + 1 }}</span>
                                        <div class="question-badges">
                                            <span class="badge marks-badge">{{ question.marks }} marks</span>
                                            <span class="badge type-badge" :class="getTypeBadgeClass(question.question_type)">
                                                {{ getTypeLabel(question.question_type) }}
                                            </span>
                                            <span class="badge status-badge" :class="getStatusBadgeClass(question)">
                                                <i :class="getStatusIcon(question)" class="me-1"></i>
                                                {{ getStatusLabel(question) }}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <!-- Question Statement -->
                                <div class="question-statement" v-html="question.question_statement"></div>

                                <!-- MCQ/MSQ Options -->
                                <div v-if="question.question_type === 'MCQ' || question.question_type === 'MSQ'" 
                                     class="options-container">
                                    <div v-for="(option, optionIndex) in question.options" :key="optionIndex" 
                                         class="option-item" 
                                         :class="getOptionClass(option, optionIndex, question)">
                                        <div class="option-content">
                                            <span class="option-label">{{ String.fromCharCode(65 + optionIndex) }}.</span>
                                            <span class="option-text" v-html="option"></span>
                                        </div>
                                        <div class="option-indicators">
                                            <i v-if="isCorrectOption(optionIndex, question)" 
                                               class="bi bi-check-circle-fill text-success"></i>
                                        </div>
                                    </div>
                                </div>

                                <!-- NAT Answer -->
                                <div v-else-if="question.question_type === 'NAT'" class="nat-container">
                                    <div class="answer-row">
                                        <div class="answer-item">
                                            <label class="answer-label">Your Answer:</label>
                                            <div class="answer-value user-answer">
                                                {{ question.user_answer ? question.user_answer.join(', ') : 'Not answered' }}
                                            </div>
                                        </div>
                                        <div class="answer-item">
                                            <label class="answer-label">Correct Answer:</label>
                                            <div class="answer-value correct-answer">
                                                {{ question.correct_answer.join(', ') }}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Score Info -->
                                <div class="question-score">
                                    <span class="score-text">
                                        Marks Scored: 
                                        <strong class="score-highlight">{{ question.marks_obtained }}/{{ question.marks }}</strong>
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

export default {
    name: 'QuizSubmission',
    setup() {
        const route = useRoute()
        const router = useRouter()
        
        const submissionData = ref(null)
        const loading = ref(true)
        const error = ref(null)
        
        const quizId = computed(() => parseInt(route.params.quizId))

        const fetchSubmissionData = async () => {
            try {
                loading.value = true
                error.value = null

                const response = await axios.get(`/user/quiz/${quizId.value}/submission`)
                submissionData.value = response.data
            } catch (err) {
                console.error('Error fetching submission data:', err)
                error.value = err.response?.data?.message || 'Failed to load submission data'
            } finally {
                loading.value = false
            }
        }

        const goToDashboard = () => {
            router.push('/dashboard')
        }

        const getTypeBadgeClass = (type) => {
            return 'bg-orange'
        }

        const getTypeLabel = (type) => {
            switch (type) {
                case 'MCQ': return 'MCQ'
                case 'MSQ': return 'MSQ'
                case 'NAT': return 'NAT'
                default: return type
            }
        }

        const getStatusBadgeClass = (question) => {
            if (!question.is_answered) return 'bg-light text-dark'
            return question.is_correct ? 'bg-success' : 'bg-danger'
        }

        const getStatusIcon = (question) => {
            if (!question.is_answered) return 'bi bi-dash-circle'
            return question.is_correct ? 'bi bi-check-circle' : 'bi bi-x-circle'
        }

        const getStatusLabel = (question) => {
            if (!question.is_answered) return 'Unanswered'
            return question.is_correct ? 'Correct' : 'Incorrect'
        }

        const getOptionClass = (option, optionIndex, question) => {
            const classes = []
            
            if (isCorrectOption(optionIndex, question)) {
                classes.push('correct-option')
            }
            
            if (isSelectedOption(optionIndex, question)) {
                classes.push('selected-option')
            }
            
            return classes.join(' ')
        }

        const isCorrectOption = (optionIndex, question) => {
            return question.correct_answer && question.correct_answer.includes(optionIndex)
        }

        const isSelectedOption = (optionIndex, question) => {
            return question.user_answer && question.user_answer.includes(optionIndex)
        }

        onMounted(() => {
            fetchSubmissionData()
        })

        return {
            submissionData,
            loading,
            error,
            goToDashboard,
            getTypeBadgeClass,
            getTypeLabel,
            getStatusBadgeClass,
            getStatusIcon,
            getStatusLabel,
            getOptionClass,
            isCorrectOption,
            isSelectedOption
        }
    }
}
</script>

<style scoped>
.quiz-submission-page {
    min-height: 100vh;
    background: linear-gradient(135deg, rgba(245, 124, 0, 0.05) 0%, rgba(245, 124, 0, 0.02) 100%);
}

.btn-back {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(245, 124, 0, 0.2);
    color: #f57c00;
    border-radius: 12px;
    font-weight: 600;
    padding: 0.5rem 1rem;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.btn-back:hover {
    background: #f57c00;
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(245, 124, 0, 0.3);
}

.submission-header {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(245, 124, 0, 0.1);
    box-shadow: 0 4px 20px rgba(245, 124, 0, 0.1);
}

.text-primary {
    color: #f57c00 !important;
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

.score-display {
    text-align: center;
    background: rgba(245, 124, 0, 0.1);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid rgba(245, 124, 0, 0.2);
}

.score-main {
    font-size: 2rem;
    font-weight: 700;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    margin-bottom: 0.5rem;
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

.score-percentage {
    font-size: 1rem;
    font-weight: 600;
    color: #f57c00;
}

.question-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 20px rgba(245, 124, 0, 0.08);
    border: 1px solid rgba(245, 124, 0, 0.1);
    transition: all 0.3s ease;
}

.question-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(245, 124, 0, 0.12);
}

.question-header {
    border-bottom: 2px solid rgba(245, 124, 0, 0.1);
    padding-bottom: 1rem;
    margin-bottom: 1.5rem;
}

.question-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}

.question-number {
    font-size: 1.25rem;
    font-weight: 700;
    color: #f57c00;
    background: rgba(245, 124, 0, 0.1);
    padding: 0.5rem 1rem;
    border-radius: 10px;
    border: 1px solid rgba(245, 124, 0, 0.2);
}

.question-badges {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.marks-badge {
    background: rgba(40, 167, 69, 0.1) !important;
    color: #28a745 !important;
    border: 1px solid rgba(40, 167, 69, 0.2);
}

.type-badge.bg-orange {
    background: rgba(245, 124, 0, 0.1) !important;
    color: #f57c00 !important;
    border: 1px solid rgba(245, 124, 0, 0.2);
}

.type-badge.bg-info {
    background: rgba(23, 162, 184, 0.1) !important;
    color: #17a2b8 !important;
    border: 1px solid rgba(23, 162, 184, 0.2);
}

.type-badge.bg-warning {
    background: rgba(255, 193, 7, 0.1) !important;
    color: #ffc107 !important;
    border: 1px solid rgba(255, 193, 7, 0.2);
}

.type-badge.bg-secondary {
    background: rgba(108, 117, 125, 0.1) !important;
    color: #6c757d !important;
    border: 1px solid rgba(108, 117, 125, 0.2);
}

.status-badge.bg-success {
    background: rgba(40, 167, 69, 0.1) !important;
    color: #28a745 !important;
    border: 1px solid rgba(40, 167, 69, 0.2);
}

.status-badge.bg-danger {
    background: rgba(220, 53, 69, 0.1) !important;
    color: #dc3545 !important;
    border: 1px solid rgba(220, 53, 69, 0.2);
}

.status-badge.bg-light {
    background: rgba(248, 249, 250, 0.8) !important;
    color: #6c757d !important;
    border: 1px solid rgba(108, 117, 125, 0.2);
}

.question-statement {
    font-size: 1.1rem;
    line-height: 1.6;
    margin-bottom: 1.5rem;
    color: #2c3e50;
}

.options-container {
    margin-bottom: 1.5rem;
}

.option-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    margin-bottom: 0.5rem;
    border: 2px solid #e9ecef;
    border-radius: 12px;
    transition: all 0.3s ease;
    background: #f8f9fa;
}

.option-item.correct-option {
    border-color: #e9ecef;
    background: #f8f9fa;
}

.option-item.selected-option {
    border-color: #f57c00;
    background: rgba(245, 124, 0, 0.15);
    box-shadow: 0 2px 8px rgba(245, 124, 0, 0.2);
}

.option-item.correct-option.selected-option {
    border-color: #f57c00;
    background: rgba(245, 124, 0, 0.15);
    box-shadow: 0 2px 8px rgba(245, 124, 0, 0.2);
}

.option-content {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.option-label {
    font-weight: 600;
    color: #f57c00;
    min-width: 2rem;
}

.option-text {
    flex: 1;
}

.option-indicators {
    display: flex;
    gap: 0.5rem;
    font-size: 1.2rem;
}

.nat-container {
    margin-bottom: 1.5rem;
}

.answer-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

.answer-item {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 12px;
    border: 1px solid #e9ecef;
}

.answer-label {
    display: block;
    font-weight: 600;
    color: #6c757d;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.answer-value {
    font-size: 1.1rem;
    font-weight: 600;
    padding: 0.5rem;
    border-radius: 8px;
}

.user-answer {
    background: rgba(245, 124, 0, 0.1);
    color: #f57c00;
    border: 1px solid rgba(245, 124, 0, 0.2);
}

.correct-answer {
    background: rgba(40, 167, 69, 0.1);
    color: #28a745;
    border: 1px solid rgba(40, 167, 69, 0.2);
}

.question-score {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(245, 124, 0, 0.1);
}

.score-text {
    font-size: 1rem;
    color: #6c757d;
}

.score-highlight {
    color: #f57c00;
    font-size: 1.1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .question-meta {
        flex-direction: column;
        align-items: flex-start;
    }

    .answer-row {
        grid-template-columns: 1fr;
        gap: 1rem;
    }

    .score-display {
        margin-top: 2rem;
    }

    .question-card {
        padding: 1.5rem;
    }

    .option-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }

    .option-indicators {
        align-self: flex-end;
    }
}

@media (max-width: 576px) {
    .question-badges {
        width: 100%;
        justify-content: flex-start;
    }

    .score-main {
        font-size: 1.5rem;
    }

    .question-card {
        padding: 1rem;
        margin-bottom: 1rem;
    }
}
</style>

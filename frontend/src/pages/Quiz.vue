<template>
    <div class="quiz-page">
        <!-- Loading State -->
        <div v-if="loading" class="loading-container">
            <div class="text-center">
                <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;"></div>
                <p class="text-muted">Loading quiz...</p>
            </div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="error-container">
            <div class="container py-5">
                <div class="row justify-content-center">
                    <div class="col-lg-6 text-center">
                        <i class="bi bi-exclamation-triangle text-danger mb-3" style="font-size: 3rem;"></i>
                        <h3 class="text-danger mb-3">Error</h3>
                        <p class="text-muted mb-4">{{ error }}</p>
                        <button class="btn btn-primary" @click="$router.push('/dashboard')">
                            Go to Dashboard
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Quiz Results -->
        <QuizResult v-else-if="showResults" :result="quizResult" :quiz-data="quizData" />

        <!-- Quiz Interface -->
        <div v-else-if="quizData && questions.length > 0" class="quiz-container">
            <!-- Top Navigation Bar -->
            <div class="quiz-nav-bar">
                <div class="container px-4">
                    <div class="row align-items-center py-4">
                        <!-- Left Side: Quiz Title and Course Info -->
                        <div class="col-lg-8 col-md-7">
                            <div class="mb-2">
                                <div class="course-chip">
                                    <i class="bi bi-book me-1"></i>
                                    {{ quizData?.course || 'Course' }}
                                </div>
                            </div>
                            <div class="mb-2 px-2">
                                <span class="chapter-label">{{ quizData?.chapter || 'Chapter' }}</span>
                            </div>
                            <h1 class="quiz-main-title mb-0 px-2">{{ quizData?.title || 'Quiz' }}</h1>
                        </div>

                        <!-- Right Side: Timer -->
                        <div class="col-lg-4 col-md-5 text-end">
                            <QuizTimer v-if="quizData?.time_duration && quizStartTime"
                                :total-duration-minutes="totalDurationMinutes" :start-time="quizStartTime"
                                @time-up="handleTimeUp" />
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quiz Content -->
            <div class="quiz-main-content flex-fill py-4">
                <div class="container px-4">
                    <div class="row">
                        <div class="col-12">
                            <!-- Question Component -->
                            <QuizQuestion v-if="currentQuestionData" :question="currentQuestionData"
                                :question-number="currentQuestionIndex + 1" :total-questions="questions.length"
                                :answer="answers[currentQuestionData.id] || []" @answer-changed="handleAnswerChange"
                                min-height="75vh" />
                        </div>
                    </div>
                </div>
            </div>

            <!-- Fixed Bottom Navigation -->
            <div class="quiz-bottom-nav">
                <div class="container px-5">
                    <div class="row align-items-center justify-content-between py-3">
                        <div class="col-auto">
                            <button class="btn btn-nav btn-outline-secondary" @click="previousQuestion"
                                :disabled="currentQuestionIndex === 0 || submitting" title="Previous Question">
                                <i class="bi bi-chevron-left"></i>
                            </button>
                        </div>
                        <div class="col-auto">
                            <button class="btn btn-nav btn-primary" @click="nextQuestion" :disabled="submitting"
                                :title="currentQuestionIndex === questions.length - 1 ? 'Submit Quiz' : 'Next Question'">
                                <span v-if="submitting">
                                    <i class="bi bi-hourglass-split"></i>
                                </span>
                                <span v-else-if="currentQuestionIndex === questions.length - 1">
                                    <i class="bi bi-check-circle"></i>
                                </span>
                                <span v-else>
                                    <i class="bi bi-chevron-right"></i>
                                </span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Time Up Modal -->
        <QuizTimeUpModal :show="showTimeUpModal" :unanswered-questions="getUnansweredCount()" :submitting="submitting"
            @acknowledge="handleTimeUpAcknowledge" />

        <!-- Submission Confirmation Modal -->
        <QuizSubmissionModal :show="showSubmissionModal" :questions="questions" :answers="answers"
            @confirm="handleSubmissionConfirm" @cancel="handleSubmissionCancel" @go-to-question="handleGoToQuestion" />
    </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import { useToast } from '../utils/useToast'
import QuizQuestion from '../components/QuizQuestion.vue'
import QuizTimer from '../components/QuizTimer.vue'
import QuizTimeUpModal from '../components/QuizTimeUpModal.vue'
import QuizSubmissionModal from '../components/QuizSubmissionModal.vue'
import QuizResult from '../components/QuizResult.vue'

export default {
    name: 'QuizPage',
    components: {
        QuizQuestion,
        QuizTimer,
        QuizTimeUpModal,
        QuizSubmissionModal,
        QuizResult
    },
    setup() {
        const route = useRoute()
        const router = useRouter()
        const authStore = useAuthStore()
        const { showToast } = useToast()

        // State
        const loading = ref(true)
        const error = ref(null)
        const quizData = ref({
            title: '',
            course: '',
            chapter: '',
            time_duration: null
        })
        const questions = ref([])
        const currentQuestionIndex = ref(0)
        const answers = ref({})
        const quizStartTime = ref(null)
        const showTimeUpModal = ref(false)
        const showSubmissionModal = ref(false)
        const submitting = ref(false)
        const showResults = ref(false)
        const quizResult = ref(null)

        // Computed
        const quizId = computed(() => {
            const id = parseInt(route.params.id)
            console.log('Quiz ID from route:', route.params.id, 'parsed as:', id)
            return id
        })

        const currentQuestionData = computed(() => {
            return questions.value[currentQuestionIndex.value]
        })

        const totalDurationMinutes = computed(() => {
            if (!quizData.value?.time_duration) return 0
            const [hours, minutes] = quizData.value.time_duration.split(':').map(Number)
            return (hours * 60) + minutes
        })

        // Methods
        const fetchQuizData = async () => {
            try {
                loading.value = true
                error.value = null

                console.log('Fetching quiz data for quiz ID:', quizId.value)
                console.log('Axios base URL:', axios.defaults.baseURL)
                console.log('Axios headers:', axios.defaults.headers.common)

                const response = await axios.get(`/quiz/${quizId.value}/questions`)
                console.log('Quiz API response:', response.data)

                if (response.data && response.data.quiz) {
                    quizData.value = {
                        title: response.data.quiz.title || 'Quiz',
                        course: response.data.quiz.course || 'Course',
                        chapter: response.data.quiz.chapter || 'Chapter',
                        time_duration: response.data.quiz.time_duration || null,
                        ...response.data.quiz
                    }
                } else {
                    console.error('Invalid API response format:', response.data)
                    throw new Error('Invalid API response format')
                }

                if (response.data && response.data.questions) {
                    questions.value = response.data.questions
                } else {
                    questions.value = []
                }

                console.log('Processed quiz data:', quizData.value)
                console.log('Questions:', questions.value)

                // Initialize quiz start time only if we have valid data
                if (questions.value.length > 0) {
                    quizStartTime.value = new Date()

                    // Initialize answers object
                    questions.value.forEach(question => {
                        answers.value[question.id] = []
                    })
                } else {
                    throw new Error('No questions found for this quiz')
                }

            } catch (err) {
                console.error('Error fetching quiz data:', err)
                console.error('Error response:', err.response)

                if (err.response) {
                    // Server responded with error status
                    error.value = err.response.data?.message || `Server error: ${err.response.status}`
                } else if (err.request) {
                    // Request was made but no response received
                    error.value = 'No response from server. Please check your connection.'
                } else {
                    // Something else happened
                    error.value = err.message || 'Failed to load quiz'
                }
            } finally {
                loading.value = false
            }
        }

        const handleAnswerChange = ({ questionId, answer }) => {
            answers.value[questionId] = answer

            // Auto-submit the current question answer
            submitCurrentAnswer()
        }

        const submitCurrentAnswer = async () => {
            if (!currentQuestionData.value) return

            const questionId = currentQuestionData.value.id
            const answer = answers.value[questionId] || []

            try {
                // Submit individual question answer
                await axios.post(`/quiz/${quizId.value}/submit-answer`, {
                    question_id: questionId,
                    answer: answer
                })
            } catch (err) {
                console.error('Error submitting answer:', err)
                showToast('Failed to save answer', { variant: 'error' })
            }
        }

        const previousQuestion = () => {
            if (currentQuestionIndex.value > 0) {
                currentQuestionIndex.value--
            }
        }

        const nextQuestion = async () => {
            if (currentQuestionIndex.value < questions.value.length - 1) {
                currentQuestionIndex.value++
            } else {
                // Show submission confirmation modal
                showSubmissionModal.value = true
            }
        }

        const submitQuiz = async () => {
            try {
                submitting.value = true

                // Prepare answers in the expected format
                const formattedAnswers = Object.entries(answers.value).map(([questionId, answer]) => ({
                    question_id: parseInt(questionId),
                    answer: answer
                }))

                const response = await axios.post(`/quiz/${quizId.value}/submit`, {
                    answers: formattedAnswers
                })

                // Get quiz results
                const resultResponse = await axios.get(`/quiz/${quizId.value}/result`)
                quizResult.value = resultResponse.data

                showResults.value = true

            } catch (err) {
                console.error('Error submitting quiz:', err)
                error.value = err.response?.data?.message || 'Failed to submit quiz'
            } finally {
                submitting.value = false
            }
        }

        const handleTimeUp = () => {
            showTimeUpModal.value = true
        }

        const handleTimeUpAcknowledge = async () => {
            showTimeUpModal.value = false
            await submitQuiz()
        }

        const getUnansweredCount = () => {
            return questions.value.filter(question => {
                const answer = answers.value[question.id]
                return !answer || answer.length === 0
            }).length
        }

        const handleSubmissionConfirm = async () => {
            showSubmissionModal.value = false
            await submitQuiz()
        }

        const handleSubmissionCancel = () => {
            showSubmissionModal.value = false
        }

        const handleGoToQuestion = (questionIndex) => {
            showSubmissionModal.value = false
            currentQuestionIndex.value = questionIndex
        }

        // Prevent page refresh/close during quiz
        const handleBeforeUnload = (event) => {
            if (!showResults.value) {
                event.preventDefault()
                event.returnValue = 'Are you sure you want to leave? Your quiz progress will be lost.'
                return event.returnValue
            }
        }

        // Lifecycle
        onMounted(async () => {
            // Check if user is authenticated
            if (!authStore.isAuthenticated) {
                router.push('/login')
                return
            }

            await fetchQuizData()
            window.addEventListener('beforeunload', handleBeforeUnload)
        })

        onUnmounted(() => {
            window.removeEventListener('beforeunload', handleBeforeUnload)
        })

        return {
            loading,
            error,
            quizData,
            questions,
            currentQuestionIndex,
            currentQuestionData,
            answers,
            quizStartTime,
            totalDurationMinutes,
            showTimeUpModal,
            showSubmissionModal,
            submitting,
            showResults,
            quizResult,
            handleAnswerChange,
            previousQuestion,
            nextQuestion,
            handleTimeUp,
            handleTimeUpAcknowledge,
            handleSubmissionConfirm,
            handleSubmissionCancel,
            handleGoToQuestion,
            getUnansweredCount
        }
    }
}
</script>

<style scoped>
.quiz-page {
    min-height: 100vh;
    background: linear-gradient(135deg, rgba(245, 124, 0, 0.05) 0%, rgba(245, 124, 0, 0.02) 100%);
}

.quiz-container {
    min-height: 100vh;
    padding-bottom: 100px;
}

.quiz-nav-bar {
    background: white;
    border-bottom: 2px solid rgba(245, 124, 0, 0.1);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    position: sticky;
    top: 0;
    z-index: 100;
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

.quiz-main-title {
    color: #2c3e50;
    font-weight: 700;
    font-size: 2rem;
}

.chapter-label {
    color: #6c757d;
    font-size: 1rem;
}

.quiz-bottom-nav {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-top: 2px solid rgba(245, 124, 0, 0.1);
    box-shadow: 0 -2px 20px rgba(245, 124, 0, 0.1);
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 1000;
}

.btn-nav {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    font-size: 1.2rem;
    font-weight: 600;
    transition: all 0.3s ease;
    border: none;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.btn-nav.btn-outline-secondary {
    background: white;
    color: #6c757d;
    border: 2px solid #e9ecef;
}

.btn-nav.btn-outline-secondary:hover:not(:disabled) {
    background: #6c757d;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(108, 117, 125, 0.3);
}

.btn-nav.btn-outline-secondary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-nav.btn-primary {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.btn-nav.btn-primary:hover:not(:disabled) {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(245, 124, 0, 0.4);
}

.btn-nav.btn-primary:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

/* Responsive Design */
@media (max-width: 768px) {
    .quiz-nav-bar .row {
        text-align: center;
    }

    .quiz-main-title {
        font-size: 1.5rem;
    }
}

@media (max-width: 576px) {
    .course-chip {
        font-size: 0.8rem;
        padding: 0.4rem 0.8rem;
    }

    .chapter-label {
        font-size: 0.9rem;
    }

    .quiz-main-title {
        font-size: 1.25rem;
    }

    .btn-nav {
        width: 45px;
        height: 45px;
        font-size: 1.1rem;
    }
}
</style>

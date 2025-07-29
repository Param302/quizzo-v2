<template>
    <div class="quiz-page">
        <div class="container py-4">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Quiz: {{ quizTitle }}</h5>
                            <div class="d-flex align-items-center">
                                <i class="bi bi-clock me-2"></i>
                                <span class="fw-semibold">{{ timeRemaining }}</span>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <div class="progress">
                                    <div class="progress-bar" :style="{ width: progressPercentage + '%' }"></div>
                                </div>
                                <small class="text-muted">Question {{ currentQuestion }} of {{ totalQuestions }}</small>
                            </div>

                            <div class="quiz-content">
                                <h4 class="mb-4">What is the primary purpose of semantic HTML?</h4>

                                <div class="options">
                                    <div class="form-check mb-3">
                                        <input class="form-check-input" type="radio" name="answer" id="option1">
                                        <label class="form-check-label" for="option1">
                                            To make websites look better
                                        </label>
                                    </div>
                                    <div class="form-check mb-3">
                                        <input class="form-check-input" type="radio" name="answer" id="option2">
                                        <label class="form-check-label" for="option2">
                                            To provide meaning and structure to web content
                                        </label>
                                    </div>
                                    <div class="form-check mb-3">
                                        <input class="form-check-input" type="radio" name="answer" id="option3">
                                        <label class="form-check-label" for="option3">
                                            To make websites load faster
                                        </label>
                                    </div>
                                    <div class="form-check mb-3">
                                        <input class="form-check-input" type="radio" name="answer" id="option4">
                                        <label class="form-check-label" for="option4">
                                            To add animations and effects
                                        </label>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="card-footer d-flex justify-content-between">
                            <button class="btn btn-outline-secondary" :disabled="currentQuestion === 1">
                                Previous
                            </button>
                            <button class="btn btn-primary">
                                {{ currentQuestion === totalQuestions ? 'Submit Quiz' : 'Next Question' }}
                            </button>
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
const quizId = route.params.id

const quizTitle = ref('Web Development Fundamentals')
const currentQuestion = ref(3)
const totalQuestions = ref(20)
const timeRemaining = ref('12:45')

const progressPercentage = computed(() => {
    return (currentQuestion.value / totalQuestions.value) * 100
})
</script>

<style scoped>
.form-check-label {
    cursor: pointer;
    padding: 0.75rem 1rem;
    border: 1px solid #dee2e6;
    border-radius: 0.5rem;
    margin-left: -1.5rem;
    width: 100%;
    transition: all 0.2s ease;
}

.form-check-input:checked+.form-check-label {
    background-color: #f57c00;
    border-color: #f57c00;
    color: white;
}

.form-check-label:hover {
    background-color: #f8f9fa;
}

.progress-bar {
    background-color: #f57c00;
}
</style>

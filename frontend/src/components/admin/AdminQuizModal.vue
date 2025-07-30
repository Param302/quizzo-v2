<template>
    <div class="modal modal-backdrop" style="display: block;" v-if="show" @click.self="$emit('close')">
        <div class="modal-dialog modal-custom modal-dialog-centered modal-xl">
            <div class="modal-content quiz-modal" :class="{ 'slide-up': show, 'slide-down': !show }">
                <div class="modal-header border-0">
                    <div class="w-100 d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h4 class="modal-title fw-bold mb-2 quiz-title-orange">
                                {{ isAddMode ? 'Add New Quiz' : 'Edit Quiz' }}
                            </h4>
                            <p class="text-muted mb-0">
                                {{ isAddMode ? 'Create a new quiz with questions' : 'Modify quiz details and questions'
                                }}
                            </p>
                        </div>
                        <div class="d-flex gap-2 align-items-center">
                            <button class="btn btn-orange" @click="saveQuiz" :disabled="loading || !isFormValid">
                                <i v-if="loading" class="bi bi-hourglass-split me-2"></i>
                                <i v-else class="bi bi-floppy me-2"></i>
                                {{ loading ? 'Saving...' : 'Save' }}
                            </button>
                            <button type="button" class="btn-close-custom" @click="$emit('close')">
                                <i class="bi bi-x"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <div class="modal-body p-0">
                    <!-- Fixed Quiz Details Section -->
                    <div class="quiz-details-section">
                        <div class="p-3">
                            <!-- Quiz Details Form -->
                            <div class="row">
                                <div class="col-md-6">
                                    <!-- Quiz Name -->
                                    <div class="mb-3">
                                        <label for="quizName" class="form-label fw-semibold text-dark mb-2">Quiz
                                            Name</label>
                                        <div class="input-group-modern">
                                            <div class="input-wrapper">
                                                <i class="bi bi-question-circle input-icon"></i>
                                                <input id="quizName" v-model="formData.title" type="text"
                                                    class="form-input" placeholder="Enter quiz name..." required />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <!-- Quiz Type -->
                                    <div class="mb-4">
                                        <label class="form-label fw-semibold text-dark mb-2">Quiz Type</label>
                                        <div class="quiz-type-selector">
                                            <div class="form-check form-check-inline">
                                                <input class="form-check-input" type="radio" name="quizType"
                                                    id="generalQuiz" :value="false" v-model="formData.is_scheduled">
                                                <label class="form-check-label" for="generalQuiz">
                                                    <i class="bi bi-infinity me-2"></i>General (Always Available)
                                                </label>
                                            </div>
                                            <div class="form-check form-check-inline">
                                                <input class="form-check-input" type="radio" name="quizType"
                                                    id="scheduledQuiz" :value="true" v-model="formData.is_scheduled">
                                                <label class="form-check-label" for="scheduledQuiz">
                                                    <i class="bi bi-calendar-event me-2"></i>Scheduled Quiz
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Quiz Description -->
                            <div class="mb-3">
                                <label for="quizDescription" class="form-label fw-semibold text-dark mb-2">Quiz
                                    Description</label>
                                <div class="input-group-modern">
                                    <div class="input-wrapper">
                                        <i class="bi bi-textarea-t input-icon"></i>
                                        <textarea id="quizDescription" v-model="formData.remarks" class="form-input"
                                            rows="3" placeholder="Enter quiz description or instructions..."></textarea>
                                    </div>
                                </div>
                            </div>

                            <!-- Conditional Scheduled Quiz Settings -->
                            <div v-if="formData.is_scheduled" class="row mb-3">
                                <div class="col-md-6">
                                    <!-- Schedule Date and Time -->
                                    <div class="mb-3">
                                        <label for="quizDateTime" class="form-label fw-semibold text-dark mb-2">Schedule
                                            Date & Time</label>
                                        <div class="input-group-modern">
                                            <div class="input-wrapper">
                                                <i class="bi bi-calendar-event input-icon"></i>
                                                <input id="quizDateTime" v-model="formData.date_of_quiz"
                                                    type="datetime-local" class="form-input" required />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <!-- Time Duration for Scheduled Quiz -->
                                    <div class="mb-3">
                                        <label for="quizDuration" class="form-label fw-semibold text-dark mb-2">Duration
                                            (minutes)</label>
                                        <div class="input-group-modern">
                                            <div class="input-wrapper">
                                                <i class="bi bi-clock input-icon"></i>
                                                <input id="quizDuration" v-model="formData.time_duration" type="number"
                                                    class="form-input" placeholder="30" min="1" max="300" />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Duration for General Quiz -->
                            <div v-if="!formData.is_scheduled" class="mb-3">
                                <div class="row">
                                    <div class="col-md-6">
                                        <label for="generalQuizDuration"
                                            class="form-label fw-semibold text-dark mb-2">Duration (minutes)</label>
                                        <div class="input-group-modern">
                                            <div class="input-wrapper">
                                                <i class="bi bi-clock input-icon"></i>
                                                <input id="generalQuizDuration" v-model="formData.time_duration"
                                                    type="number" class="form-input" placeholder="30" min="1"
                                                    max="300" />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Fixed Questions Header -->
                    <div class="questions-header-section border-top">
                        <div class="p-3 pb-2">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="fw-bold mb-0 text-orange">
                                    <i class="bi bi-list-ul me-2"></i>
                                    Questions ({{ formData.questions.length }})
                                </h5>
                                <button class="btn btn-orange" @click="addQuestion">
                                    <i class="bi bi-plus-circle me-2"></i>
                                    Add Question
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Scrollable Questions Section -->
                    <div class="questions-content-section">
                        <!-- No Questions State -->
                        <div v-if="formData.questions.length === 0" class="empty-questions text-center py-4 mx-4">
                            <i class="bi bi-list-ul text-muted mb-3" style="font-size: 3rem;"></i>
                            <h6 class="text-muted mb-2">No questions yet</h6>
                            <p class="text-muted mb-3">Add questions to create your quiz</p>
                            <button class="btn btn-orange" @click="addQuestion">
                                <i class="bi bi-plus-circle me-2"></i>
                                Add First Question
                            </button>
                        </div>

                        <!-- Questions List -->
                        <div v-else class="questions-list px-4 pb-4">
                            <div v-for="(question, index) in formData.questions" :key="question.tempId || question.id"
                                class="question-item mb-4">
                                <div class="question-card">
                                    <div class="question-header d-flex justify-content-between align-items-center mb-3">
                                        <h6 class="fw-bold text-dark mb-0">Question {{ index + 1 }}</h6>
                                        <button class="btn btn-sm btn-danger" @click="confirmRemoveQuestion(index)"
                                            title="Delete Question">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>

                                    <div class="row">
                                        <div class="col-md-8">
                                            <!-- Question Statement -->
                                            <div class="mb-3">
                                                <label class="form-label fw-semibold text-dark mb-2">Question
                                                    Statement</label>
                                                <div class="input-group-modern">
                                                    <div class="input-wrapper">
                                                        <i class="bi bi-question-circle input-icon"></i>
                                                        <textarea v-model="question.question_statement"
                                                            class="form-input" rows="3"
                                                            placeholder="Enter your question..." required></textarea>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <!-- Marks -->
                                            <div class="mb-3">
                                                <label class="form-label fw-semibold text-dark mb-2">Marks</label>
                                                <div class="input-group-modern">
                                                    <div class="input-wrapper">
                                                        <i class="bi bi-star input-icon"></i>
                                                        <input v-model.number="question.marks" type="number" min="0.5"
                                                            step="0.5" class="form-input" placeholder="1.0" required>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Question Type -->
                                    <div class="mb-3">
                                        <label class="form-label fw-semibold text-dark mb-2">Question Type</label>
                                        <div class="question-type-selector d-flex gap-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="radio"
                                                    :name="`questionType_${index}`" :id="`mcq_${index}`" value="MCQ"
                                                    v-model="question.question_type"
                                                    @change="onQuestionTypeChange(index)">
                                                <label class="form-check-label" :for="`mcq_${index}`">
                                                    <i class="bi bi-ui-radios me-1"></i>MCQ (Single Choice)
                                                </label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="radio"
                                                    :name="`questionType_${index}`" :id="`msq_${index}`" value="MSQ"
                                                    v-model="question.question_type"
                                                    @change="onQuestionTypeChange(index)">
                                                <label class="form-check-label" :for="`msq_${index}`">
                                                    <i class="bi bi-ui-checks me-1"></i>MSQ (Multiple Choice)
                                                </label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="radio"
                                                    :name="`questionType_${index}`" :id="`nat_${index}`" value="NAT"
                                                    v-model="question.question_type"
                                                    @change="onQuestionTypeChange(index)">
                                                <label class="form-check-label" :for="`nat_${index}`">
                                                    <i class="bi bi-input-cursor-text me-1"></i>NAT (Numeric Answer)
                                                </label>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Options for MCQ/MSQ -->
                                    <div v-if="question.question_type === 'MCQ' || question.question_type === 'MSQ'"
                                        class="options-section">
                                        <div class="d-flex justify-content-between align-items-center mb-3">
                                            <label class="form-label fw-semibold text-dark mb-0">Options</label>
                                            <button class="btn btn-sm btn-outline-orange" @click="addOption(index)">
                                                <i class="bi bi-plus me-1"></i>Add Option
                                            </button>
                                        </div>

                                        <div v-for="(option, optIndex) in question.options" :key="optIndex"
                                            class="option-item mb-3">
                                            <div class="option-card">
                                                <div class="d-flex align-items-center">
                                                    <div class="option-selector me-3">
                                                        <div v-if="question.question_type === 'MCQ'" class="form-check">
                                                            <input class="form-check-input option-radio" type="radio"
                                                                :name="`correct_${index}`" :value="optIndex"
                                                                v-model.number="question.correct_answer[0]">
                                                            <label class="form-check-label option-label">
                                                                {{ String.fromCharCode(65 + optIndex) }}
                                                            </label>
                                                        </div>
                                                        <div v-else class="form-check">
                                                            <input class="form-check-input option-checkbox"
                                                                type="checkbox" :value="optIndex"
                                                                v-model="question.correct_answer">
                                                            <label class="form-check-label option-label">
                                                                {{ String.fromCharCode(65 + optIndex) }}
                                                            </label>
                                                        </div>
                                                    </div>
                                                    <div class="option-input-wrapper flex-grow-1 me-3">
                                                        <input v-model="option.text" type="text"
                                                            class="form-control option-input"
                                                            :placeholder="`Enter option ${String.fromCharCode(65 + optIndex)}...`"
                                                            required>
                                                    </div>
                                                    <button class="btn btn-sm btn-outline-danger option-delete-btn"
                                                        @click="removeOption(index, optIndex)"
                                                        :disabled="question.options.length <= 2" title="Delete Option">
                                                        <i class="bi bi-trash"></i>
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- NAT Answer -->
                                    <div v-if="question.question_type === 'NAT'" class="nat-section">
                                        <div class="mb-3">
                                            <label class="form-label fw-semibold text-dark mb-2">Correct Answer</label>
                                            <div class="input-group-modern">
                                                <div class="input-wrapper">
                                                    <i class="bi bi-123 input-icon"></i>
                                                    <input v-model="question.correct_answer[0]" type="number"
                                                        step="0.01" class="form-input"
                                                        placeholder="Enter numeric answer..." required>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Question Delete Confirmation Modal -->
    <DeleteConfirmationModal :show="showDeleteQuestionModal" title="Delete Question"
        message="You are about to permanently delete this question from the quiz." :itemDetails="questionToDelete"
        :loading="deletingQuestion" @close="closeDeleteQuestionModal" @confirm="deleteQuestion" />
</template>

<script>
import { ref, computed, watch } from 'vue'
import DeleteConfirmationModal from '@/components/DeleteConfirmationModal.vue'

export default {
    name: 'AdminQuizModal',
    components: {
        DeleteConfirmationModal
    },
    props: {
        quiz: {
            type: Object,
            required: true
        },
        show: {
            type: Boolean,
            default: false
        },
        loading: {
            type: Boolean,
            default: false
        },
        chapterId: {
            type: Number,
            required: true
        }
    },
    emits: ['close', 'save'],
    setup(props, { emit }) {
        const formData = ref({
            title: '',
            remarks: '',
            is_scheduled: false,
            date_of_quiz: '',
            time_duration: '',
            questions: []
        })

        const showDeleteQuestionModal = ref(false)
        const questionToDelete = ref(null)
        const questionIndexToDelete = ref(null)
        const deletingQuestion = ref(false)

        let nextTempId = 1

        const isAddMode = computed(() => {
            return !props.quiz.id
        })

        const isFormValid = computed(() => {
            return formData.value.title.trim().length > 0 &&
                formData.value.questions.length > 0 &&
                formData.value.questions.every(q =>
                    q.question_statement.trim().length > 0 &&
                    q.marks > 0 &&
                    q.question_type &&
                    (q.question_type === 'NAT' ?
                        q.correct_answer[0] !== '' && q.correct_answer[0] !== null :
                        q.options && q.options.length >= 2 && q.correct_answer.length > 0)
                )
        })

        // Helper functions for time duration conversion
        const convertHoursToMinutes = (timeString) => {
            if (!timeString) return ''
            const [hours, minutes] = timeString.split(':').map(Number)
            return (hours * 60 + minutes).toString()
        }

        const convertMinutesToHours = (minutes) => {
            if (!minutes) return ''
            const totalMinutes = parseInt(minutes)
            const hours = Math.floor(totalMinutes / 60)
            const mins = totalMinutes % 60
            return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`
        }

        const initializeForm = () => {
            if (props.quiz && props.quiz.id) {
                formData.value = {
                    title: props.quiz.title || '',
                    remarks: props.quiz.remarks || '',
                    is_scheduled: props.quiz.is_scheduled || false,
                    date_of_quiz: props.quiz.date_of_quiz ? formatDateTimeLocal(props.quiz.date_of_quiz) : '',
                    time_duration: convertHoursToMinutes(props.quiz.time_duration) || '',
                    questions: props.quiz.questions ? props.quiz.questions.map(q => ({
                        ...q,
                        // Ensure options have the correct structure
                        options: q.options ? q.options.map(opt =>
                            typeof opt === 'string' ? { text: opt } : opt
                        ) : [],
                        // Ensure correct_answer is properly formatted
                        correct_answer: Array.isArray(q.correct_answer) ? q.correct_answer : [q.correct_answer]
                    })) : []
                }
            } else {
                formData.value = {
                    title: '',
                    remarks: '',
                    is_scheduled: false,
                    date_of_quiz: '',
                    time_duration: '',
                    questions: []
                }
            }
        }

        const formatDateTimeLocal = (dateString) => {
            if (!dateString) return ''
            const date = new Date(dateString)
            const year = date.getFullYear()
            const month = String(date.getMonth() + 1).padStart(2, '0')
            const day = String(date.getDate()).padStart(2, '0')
            const hours = String(date.getHours()).padStart(2, '0')
            const minutes = String(date.getMinutes()).padStart(2, '0')
            return `${year}-${month}-${day}T${hours}:${minutes}`
        }

        const addQuestion = () => {
            formData.value.questions.push({
                tempId: nextTempId++,
                question_statement: '',
                question_type: 'MCQ',
                options: [
                    { text: '' },
                    { text: '' }
                ],
                correct_answer: [0],
                marks: 1.0
            })
        }

        const removeQuestion = (index) => {
            formData.value.questions.splice(index, 1)
        }

        const confirmRemoveQuestion = (index) => {
            const question = formData.value.questions[index]
            questionToDelete.value = {
                name: `Question ${index + 1}`,
                description: question.question_statement || 'No question statement provided'
            }
            questionIndexToDelete.value = index
            showDeleteQuestionModal.value = true
        }

        const closeDeleteQuestionModal = () => {
            showDeleteQuestionModal.value = false
            questionToDelete.value = null
            questionIndexToDelete.value = null
        }

        const deleteQuestion = () => {
            if (questionIndexToDelete.value !== null) {
                deletingQuestion.value = true

                setTimeout(() => {
                    removeQuestion(questionIndexToDelete.value)
                    closeDeleteQuestionModal()
                    deletingQuestion.value = false
                }, 300)
            }
        }

        const onQuestionTypeChange = (index) => {
            const question = formData.value.questions[index]
            if (question.question_type === 'NAT') {
                question.options = []
                question.correct_answer = ['']
            } else {
                question.options = [
                    { text: '' },
                    { text: '' }
                ]
                question.correct_answer = question.question_type === 'MCQ' ? [0] : []
            }
        }

        const addOption = (questionIndex) => {
            formData.value.questions[questionIndex].options.push({ text: '' })
        }

        const removeOption = (questionIndex, optionIndex) => {
            const question = formData.value.questions[questionIndex]
            question.options.splice(optionIndex, 1)

            // Update correct answers if affected
            if (question.question_type === 'MCQ') {
                if (question.correct_answer[0] >= optionIndex) {
                    question.correct_answer[0] = Math.max(0, question.correct_answer[0] - 1)
                }
            } else if (question.question_type === 'MSQ') {
                question.correct_answer = question.correct_answer
                    .filter(idx => idx !== optionIndex)
                    .map(idx => idx > optionIndex ? idx - 1 : idx)
            }
        }

        const saveQuiz = () => {
            if (!isFormValid.value) return

            const quizData = {
                title: formData.value.title.trim(),
                remarks: formData.value.remarks.trim(),
                is_scheduled: formData.value.is_scheduled,
                date_of_quiz: formData.value.is_scheduled ? formData.value.date_of_quiz : null,
                time_duration: formData.value.time_duration ? convertMinutesToHours(formData.value.time_duration) : null,
                questions: formData.value.questions.map(question => ({
                    id: question.id || null,
                    question_statement: question.question_statement.trim(),
                    question_type: question.question_type,
                    options: question.question_type === 'NAT' ? null : question.options.map(opt =>
                        typeof opt === 'string' ? opt : opt.text
                    ),
                    correct_answer: question.correct_answer,
                    marks: question.marks
                }))
            }

            emit('save', quizData)
        }

        // Watch for quiz changes to reinitialize form
        watch(() => props.quiz, () => {
            initializeForm()
        }, { immediate: true })

        return {
            formData,
            isAddMode,
            isFormValid,
            addQuestion,
            removeQuestion,
            confirmRemoveQuestion,
            showDeleteQuestionModal,
            questionToDelete,
            deletingQuestion,
            closeDeleteQuestionModal,
            deleteQuestion,
            onQuestionTypeChange,
            addOption,
            removeOption,
            saveQuiz
        }
    }
}
</script>

<style scoped>
@keyframes slideUp {
    from {
        transform: translateY(100%);
        opacity: 0;
    }

    to {
        transform: translateY(0);
        opacity: 1;
    }
}

@keyframes slideDown {
    from {
        transform: translateY(0);
        opacity: 1;
    }

    to {
        transform: translateY(100%);
        opacity: 0;
    }
}

.slide-up {
    animation: slideUp 0.3s ease-out;
}

.slide-down {
    animation: slideDown 0.3s ease-in;
}

.modal-backdrop {
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(5px);
}

.modal-custom {
    max-width: 1200px;
}

.modal-content {
    border-radius: 20px;
    border: none;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
    background: #ffffff;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
}

.modal-body {
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.quiz-details-section {
    flex-shrink: 0;
    background: #ffffff;
}

.questions-header-section {
    flex-shrink: 0;
    background: #ffffff;
    border-top: 1px solid rgba(245, 124, 0, 0.1);
}

.questions-content-section {
    flex: 1;
    overflow-y: auto;
    max-height: 500px;
}

.quiz-title-orange {
    color: #f57c00;
}

.text-orange {
    color: #f57c00;
}

.btn-orange {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    color: white;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    padding: 0.75rem 1.5rem;
}

.btn-orange:hover {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.4);
}

.btn-outline-orange {
    border: 2px solid #f57c00;
    color: #f57c00;
    background: transparent;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.btn-outline-orange:hover {
    background: #f57c00;
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.btn-close-custom {
    background: rgba(220, 53, 69, 0.1);
    border: 1px solid rgba(220, 53, 69, 0.2);
    color: #dc3545;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    transition: all 0.3s ease;
}

.btn-close-custom:hover {
    background: rgba(220, 53, 69, 0.2);
    transform: scale(1.1);
}

/* Auth-style Input Fields */
.input-group-modern {
    position: relative;
}

.input-wrapper {
    position: relative;
    display: flex;
    align-items: flex-start;
}

.form-input {
    width: 100%;
    padding: 0.875rem 1rem 0.875rem 3rem;
    border: none;
    background: rgba(245, 124, 0, 0.05);
    border-radius: 12px;
    font-size: 0.95rem;
    transition: all 0.3s ease;
    outline: none;
    resize: vertical;
}

.form-input:focus {
    background: rgba(245, 124, 0, 0.1);
    box-shadow: 0 0 0 3px rgba(245, 124, 0, 0.1);
    transform: translateY(-1px);
}

.form-input::placeholder {
    color: #adb5bd;
    font-weight: 400;
}

.input-icon {
    position: absolute;
    left: 1rem;
    top: 0.875rem;
    color: #f57c00;
    font-size: 1.1rem;
    z-index: 2;
}

/* Quiz Type Selector */
.quiz-type-selector {
    display: flex;
    gap: 1rem;
}

.form-check-input:checked {
    background-color: #f57c00;
    border-color: #f57c00;
}

.form-check-label {
    font-weight: 500;
    color: #495057;
}

/* Question Type Selector */
.question-type-selector .form-check-label {
    background: rgba(245, 124, 0, 0.05);
    border: 1px solid rgba(245, 124, 0, 0.2);
    padding: 0.5rem 1rem;
    border-radius: 8px;
    transition: all 0.3s ease;
    cursor: pointer;
}

.question-type-selector .form-check-input:checked+.form-check-label {
    background: rgba(245, 124, 0, 0.1);
    border-color: #f57c00;
    color: #f57c00;
}

/* Empty States */
.empty-questions {
    background: rgba(245, 124, 0, 0.05);
    border: 2px dashed rgba(245, 124, 0, 0.2);
    border-radius: 16px;
}

/* Question Cards */
.question-card {
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}

.question-card:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    border-color: rgba(245, 124, 0, 0.3);
}

/* Options */
.option-item {
    transition: all 0.3s ease;
}

.option-card {
    background: rgba(248, 249, 250, 0.8);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 12px;
    padding: 1rem;
    transition: all 0.3s ease;
}

.option-card:hover {
    background: rgba(245, 124, 0, 0.05);
    border-color: rgba(245, 124, 0, 0.2);
    box-shadow: 0 2px 8px rgba(245, 124, 0, 0.1);
}

.option-selector {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    background: rgba(245, 124, 0, 0.1);
    border-radius: 50%;
    position: relative;
}

.option-radio,
.option-checkbox {
    position: absolute;
    opacity: 0;
    width: 100%;
    height: 100%;
    cursor: pointer;
}

.option-radio:checked+.option-label,
.option-checkbox:checked+.option-label {
    background: #f57c00;
    color: white;
    transform: scale(1.1);
}

.option-label {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: rgba(255, 255, 255, 0.8);
    border: 2px solid rgba(245, 124, 0, 0.3);
    border-radius: 50%;
    font-weight: 700;
    font-size: 0.9rem;
    color: #f57c00;
    transition: all 0.3s ease;
    cursor: pointer;
    margin: 0;
}

.option-input-wrapper {
    position: relative;
}

.option-input {
    border: 2px solid rgba(245, 124, 0, 0.2);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.95rem;
    transition: all 0.3s ease;
    background: rgba(255, 255, 255, 0.9);
}

.option-input:focus {
    border-color: #f57c00;
    box-shadow: 0 0 0 3px rgba(245, 124, 0, 0.1);
    background: white;
    outline: none;
}

.option-delete-btn {
    border: 2px solid #dc3545;
    color: #dc3545;
    background: transparent;
    border-radius: 8px;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}

.option-delete-btn:hover:not(:disabled) {
    background: #dc3545;
    color: white;
    transform: scale(1.05);
}

.option-delete-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
    .modal-custom {
        max-width: 95%;
        margin: 1rem;
    }

    .quiz-type-selector {
        flex-direction: column;
        gap: 0.5rem;
    }

    .question-type-selector {
        flex-direction: column;
        gap: 0.5rem;
    }
}
</style>

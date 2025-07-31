<template>
    <div class="question-container" :style="{ minHeight: minHeight }">
        <div class="row justify-content-center">
            <div class="col-lg-10 col-xl-9">
                <div class="question-content">
                    <!-- Question Header -->
                    <div class="question-header mb-4">
                        <div class="row align-items-center">
                            <div class="col">
                                <h4 class="question-title mb-0">
                                    Question {{ questionNumber }} of {{ totalQuestions }}
                                </h4>
                            </div>
                            <div class="col-auto">
                                <div class="d-flex gap-2">
                                    <!-- Question Type Chip -->
                                    <div class="question-type-chip">
                                        <i class="bi bi-question-circle-fill me-1"></i>
                                        {{ question.question_type }}
                                    </div>
                                    <!-- Marks Chip -->
                                    <div class="marks-chip">
                                        <i class="bi bi-award me-1"></i>
                                        {{ question.marks }} mark{{ question.marks !== 1 ? 's' : '' }}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Question Statement -->
                    <div class="question-statement mb-4">
                        <p class="question-text">{{ question.question_statement }}</p>
                    </div>

                    <!-- Question Options -->
                    <div class="question-options">
                        <!-- MCQ Options -->
                        <div v-if="question.question_type === 'MCQ'" class="mcq-options">
                            <div v-for="(option, index) in question.options" :key="index" class="option-item mb-3"
                                @click="selectMCQOption(index)">
                                <div class="form-check option-card"
                                    :class="{ 'selected': selectedAnswer && selectedAnswer[0] === index }">
                                    <input class="form-check-input option-radio" type="radio"
                                        :name="`question_${question.id}`" :id="`option_${question.id}_${index}`"
                                        :value="index" v-model="selectedMCQOption" @change="updateAnswer">
                                    <label class="form-check-label option-label"
                                        :for="`option_${question.id}_${index}`">
                                        <span class="option-letter">{{ String.fromCharCode(65 + index) }}</span>
                                        <span class="option-text">{{ option }}</span>
                                    </label>
                                </div>
                            </div>
                        </div>

                        <!-- MSQ Options -->
                        <div v-else-if="question.question_type === 'MSQ'" class="msq-options">
                            <div v-for="(option, index) in question.options" :key="index" class="option-item mb-3"
                                @click="toggleMSQOption(index)">
                                <div class="form-check option-card"
                                    :class="{ 'selected': selectedAnswer && selectedAnswer.includes(index) }">
                                    <input class="form-check-input option-checkbox" type="checkbox"
                                        :id="`option_${question.id}_${index}`" :value="index"
                                        v-model="selectedMSQOptions" @change="updateAnswer">
                                    <label class="form-check-label option-label"
                                        :for="`option_${question.id}_${index}`">
                                        <span class="option-letter">{{ String.fromCharCode(65 + index) }}</span>
                                        <span class="option-text">{{ option }}</span>
                                    </label>
                                </div>
                            </div>
                        </div>

                        <!-- NAT Input -->
                        <div v-else-if="question.question_type === 'NAT'" class="nat-input">
                            <div class="nat-input-container">
                                <label class="form-label fw-semibold mb-3">Enter your numeric answer:</label>
                                <div class="input-group input-group-lg">
                                    <span class="input-group-text">
                                        <i class="bi bi-123"></i>
                                    </span>
                                    <input type="number" step="0.01" class="form-control nat-input-field"
                                        placeholder="Enter numeric value..." v-model="natValue" @input="updateAnswer">
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
export default {
    name: 'QuizQuestion',
    props: {
        question: {
            type: Object,
            required: true
        },
        questionNumber: {
            type: Number,
            required: true
        },
        totalQuestions: {
            type: Number,
            required: true
        },
        answer: {
            type: Array,
            default: () => []
        },
        minHeight: {
            type: String,
            default: '80vh'
        }
    },
    emits: ['answer-changed'],
    data() {
        return {
            selectedMCQOption: null,
            selectedMSQOptions: [],
            natValue: ''
        }
    },
    computed: {
        selectedAnswer() {
            return this.answer
        }
    },
    watch: {
        answer: {
            handler(newAnswer) {
                this.updateLocalAnswers(newAnswer)
            },
            immediate: true
        },
        question: {
            handler() {
                this.updateLocalAnswers(this.answer)
            },
            immediate: true
        }
    },
    methods: {
        updateLocalAnswers(answer) {
            if (this.question.question_type === 'MCQ') {
                this.selectedMCQOption = answer && answer.length > 0 ? answer[0] : null
            } else if (this.question.question_type === 'MSQ') {
                this.selectedMSQOptions = answer || []
            } else if (this.question.question_type === 'NAT') {
                this.natValue = answer && answer.length > 0 ? answer[0] : ''
            }
        },

        selectMCQOption(index) {
            this.selectedMCQOption = index
            this.updateAnswer()
        },

        toggleMSQOption(index) {
            const currentIndex = this.selectedMSQOptions.indexOf(index)
            if (currentIndex > -1) {
                this.selectedMSQOptions.splice(currentIndex, 1)
            } else {
                this.selectedMSQOptions.push(index)
            }
            this.updateAnswer()
        },

        updateAnswer() {
            let answer = []

            if (this.question.question_type === 'MCQ') {
                if (this.selectedMCQOption !== null) {
                    answer = [this.selectedMCQOption]
                }
            } else if (this.question.question_type === 'MSQ') {
                answer = [...this.selectedMSQOptions].sort((a, b) => a - b)
            } else if (this.question.question_type === 'NAT') {
                if (this.natValue !== '' && this.natValue !== null) {
                    answer = [parseFloat(this.natValue)]
                }
            }

            this.$emit('answer-changed', {
                questionId: this.question.id,
                answer: answer
            })
        }
    }
}
</script>

<style scoped>
.question-container {
    display: flex;
    flex-direction: column;
}

.question-content {
    flex: 1;
    padding: 2rem;
    background: white;
    border: 2px solid rgba(245, 124, 0, 0.1);
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.question-header {
    border-bottom: 2px solid rgba(245, 124, 0, 0.1);
    padding-bottom: 1rem;
}

.question-title {
    color: #2c3e50;
    font-weight: 700;
    font-size: 1.5rem;
}

.question-type-chip {
    background: rgba(245, 124, 0, 0.1);
    color: #f57c00;
    border: 1px solid rgba(245, 124, 0, 0.2);
    padding: 0.25rem 0.6rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
}

.marks-chip {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    color: white;
    padding: 0.4rem 0.8rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.8rem;
    display: inline-flex;
    align-items: center;
}

.marks-badge {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-weight: 600;
    font-size: 0.9rem;
}

.question-statement {
    margin-top: 1.5rem;
}

.question-text {
    font-size: 1.2rem;
    line-height: 1.6;
    color: #2c3e50;
    margin: 0;
    font-weight: 500;
}

.option-item {
    cursor: pointer;
    transition: all 0.3s ease;
}

.option-card {
    background: white;
    border: 2px solid #e9ecef;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
}

.option-card:hover {
    background: rgba(245, 124, 0, 0.05);
    border-color: rgba(245, 124, 0, 0.3);
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.1);
}

.option-card.selected {
    background: rgba(245, 124, 0, 0.1);
    border-color: #f57c00;
    color: #e65100;
}

.option-card.selected .option-letter {
    background: #f57c00;
    color: white;
}

.form-check-input {
    display: none;
}

.option-label {
    display: flex;
    align-items: center;
    margin: 0;
    cursor: pointer;
    width: 100%;
}

.option-letter {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 35px;
    height: 35px;
    background: #e9ecef;
    border-radius: 50%;
    font-weight: 700;
    font-size: 0.9rem;
    margin-right: 1rem;
    flex-shrink: 0;
    transition: all 0.3s ease;
}

.option-text {
    flex: 1;
    font-size: 1rem;
    line-height: 1.5;
    color: #2c3e50;
}

/* NAT Input Styles */
.nat-input-container {
    max-width: 400px;
}

.nat-input-field {
    font-size: 1.2rem;
    padding: 0.75rem 1rem;
    border: 2px solid #e9ecef;
    border-radius: 12px;
    transition: all 0.3s ease;
}

.nat-input-field:focus {
    border-color: #f57c00;
    box-shadow: 0 0 0 0.2rem rgba(245, 124, 0, 0.25);
}

.input-group-text {
    background: #f8f9fa;
    border: 2px solid #e9ecef;
    border-right: none;
    color: #f57c00;
    font-size: 1.2rem;
}

.form-text {
    color: #6c757d;
    font-size: 0.875rem;
    margin-top: 0.5rem;
}

.question-footer {
    border-top: 1px solid #e9ecef;
    padding-top: 1rem;
}

.required-indicator {
    display: flex;
    align-items: center;
    font-size: 0.875rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .question-content {
        padding: 1.5rem;
    }

    .question-title {
        font-size: 1.25rem;
    }

    .question-text {
        font-size: 1.1rem;
    }

    .marks-badge {
        font-size: 0.8rem;
        padding: 0.4rem 0.8rem;
    }

    .option-card {
        padding: 0.875rem 1rem;
    }

    .option-letter {
        width: 30px;
        height: 30px;
        font-size: 0.8rem;
        margin-right: 0.75rem;
    }

    .option-text {
        font-size: 0.95rem;
    }
}

@media (max-width: 576px) {
    .question-content {
        padding: 1rem;
    }

    .question-title {
        font-size: 1.1rem;
    }

    .question-text {
        font-size: 1rem;
    }

    .option-label {
        flex-direction: row;
        align-items: flex-start;
    }

    .option-letter {
        margin-top: 0.2rem;
    }
}
</style>

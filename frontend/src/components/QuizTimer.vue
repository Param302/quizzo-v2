<template>
    <div class="quiz-timer-wrapper">
        <div class="quiz-timer" :class="{ 'danger': isTimeRunningOut, 'pulse': isTimeRunningOut }">
            <div class="timer-circle">
                <!-- Circular Progress Background -->
                <svg class="timer-svg" width="80" height="80" viewBox="0 0 80 80">
                    <circle cx="40" cy="40" r="35" stroke="#e9ecef" stroke-width="6" fill="none" />
                    <circle cx="40" cy="40" r="35" stroke="#f57c00" stroke-width="6" fill="none"
                        :stroke-dasharray="circumference" :stroke-dashoffset="progressOffset"
                        :class="{ 'danger-stroke': isTimeRunningOut }" class="progress-circle" />
                </svg>

                <!-- Timer Content -->
                <div class="timer-content">
                    <div class="timer-icon">
                        <i class="bi bi-clock" :class="{ 'text-danger': isTimeRunningOut }"></i>
                    </div>
                    <div class="timer-display">
                        <span class="time-text" :class="{ 'text-danger': isTimeRunningOut }">
                            {{ formatTime }}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'QuizTimer',
    props: {
        totalDurationMinutes: {
            type: Number,
            required: true
        },
        startTime: {
            type: Date,
            required: true
        }
    },
    emits: ['time-up'],
    data() {
        return {
            currentTime: new Date(),
            interval: null
        }
    },
    computed: {
        elapsedSeconds() {
            return Math.floor((this.currentTime - this.startTime) / 1000)
        },

        totalSeconds() {
            return this.totalDurationMinutes * 60
        },

        remainingSeconds() {
            return Math.max(0, this.totalSeconds - this.elapsedSeconds)
        },

        isTimeRunningOut() {
            return this.remainingSeconds <= 60 && this.remainingSeconds > 0
        },

        isTimeUp() {
            return this.remainingSeconds <= 0
        },

        formatTime() {
            const minutes = Math.floor(this.remainingSeconds / 60)
            const seconds = this.remainingSeconds % 60
            return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
        },

        // Circular progress calculations
        circumference() {
            return 2 * Math.PI * 35 // radius = 35
        },

        progressPercentage() {
            return (this.elapsedSeconds / this.totalSeconds) * 100
        },

        progressOffset() {
            const progress = Math.min(this.progressPercentage, 100)
            return this.circumference - (progress / 100) * this.circumference
        }
    },
    mounted() {
        this.startTimer()
    },
    beforeUnmount() {
        this.stopTimer()
    },
    watch: {
        isTimeUp(newVal) {
            if (newVal) {
                this.stopTimer()
                this.$emit('time-up')
            }
        }
    },
    methods: {
        startTimer() {
            this.interval = setInterval(() => {
                this.currentTime = new Date()
            }, 1000)
        },

        stopTimer() {
            if (this.interval) {
                clearInterval(this.interval)
                this.interval = null
            }
        }
    }
}
</script>

<style scoped>
.quiz-timer-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
}

.quiz-timer {
    position: relative;
    transition: all 0.3s ease;
}

.quiz-timer.danger {
    animation: pulse-danger 1s infinite;
}

.timer-circle {
    position: relative;
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.timer-svg {
    position: absolute;
    top: 0;
    left: 0;
    transform: rotate(-90deg);
}

.progress-circle {
    transition: stroke-dashoffset 0.5s ease, stroke 0.3s ease;
    stroke-linecap: round;
}

.progress-circle.danger-stroke {
    stroke: #dc3545;
}

.timer-content {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    z-index: 1;
}

.timer-icon {
    font-size: 0.9rem;
    color: #6c757d;
    margin-bottom: 2px;
}

.timer-display {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.time-text {
    font-size: 0.75rem;
    font-weight: 700;
    color: #2c3e50;
    line-height: 1;
}

.time-text.text-danger {
    color: #dc3545 !important;
}

@keyframes pulse-danger {
    0% {
        transform: scale(1);
        filter: drop-shadow(0 0 0 rgba(220, 53, 69, 0));
    }

    50% {
        transform: scale(1.05);
        filter: drop-shadow(0 0 8px rgba(220, 53, 69, 0.6));
    }

    100% {
        transform: scale(1);
        filter: drop-shadow(0 0 0 rgba(220, 53, 69, 0));
    }
}

/* Responsive Design */
@media (max-width: 768px) {
    .timer-circle {
        width: 70px;
        height: 70px;
    }

    .timer-svg {
        width: 70px;
        height: 70px;
    }

    .time-text {
        font-size: 0.7rem;
    }

    .timer-icon {
        font-size: 0.8rem;
    }
}

@media (max-width: 576px) {
    .timer-circle {
        width: 60px;
        height: 60px;
    }

    .timer-svg {
        width: 60px;
        height: 60px;
    }

    .time-text {
        font-size: 0.65rem;
    }

    .timer-icon {
        font-size: 0.75rem;
    }
}
</style>

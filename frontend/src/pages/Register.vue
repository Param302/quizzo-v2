<template>
    <div class="mb-3">
        <router-link to="/" class="btn-auth-back">
            <i class="bi bi-arrow-left me-2"></i>
            Back to Home
        </router-link>
    </div>

    <div class="auth-header mb-3 text-center">
        <div class="auth-title-wrapper mb-2">
            <i class="bi bi-person-plus auth-title-icon me-2"></i>
            <h1 class="auth-title">Create Account</h1>
        </div>
        <p class="auth-subtitle">Join the Quizzo community and start learning</p>
    </div>

    <form @submit.prevent="handleRegister" class="auth-form">
        <div class="input-group-modern mb-3">
            <div class="input-wrapper">
                <i class="bi bi-person input-icon"></i>
                <input id="name" v-model="form.name" type="text" class="form-input" placeholder="Full name" required
                    :disabled="authStore.loading" />
            </div>
        </div>

        <div class="input-group-modern mb-3">
            <div class="input-wrapper">
                <i class="bi bi-envelope input-icon"></i>
                <input id="email" v-model="form.email" type="email" class="form-input" placeholder="Email address"
                    required :disabled="authStore.loading" />
            </div>
        </div>

        <div class="input-group-modern mb-3">
            <div class="input-wrapper">
                <i class="bi bi-at input-icon"></i>
                <input id="username" v-model="form.username" type="text" class="form-input" placeholder="Username"
                    required :disabled="authStore.loading" />
            </div>
        </div>

        <div class="input-group-modern mb-2">
            <div class="input-wrapper">
                <i class="bi bi-lock input-icon"></i>
                <input id="password" v-model="form.password" :type="showPassword ? 'text' : 'password'"
                    class="form-input" placeholder="Password" required :disabled="authStore.loading" />
                <button type="button" class="password-toggle" @click="showPassword = !showPassword"
                    :disabled="authStore.loading">
                    <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                </button>
            </div>
        </div>

        <div v-if="form.password" class="password-strength mb-3">
            <div class="strength-meter">
                <div class="strength-fill" :class="strengthClass" :style="{ width: strengthPercentage + '%' }"></div>
            </div>
            <small class="strength-text" :class="strengthTextClass">
                {{ strengthText }}
            </small>
        </div>

        <div class="input-group-modern mb-3">
            <div class="input-wrapper">
                <i class="bi bi-lock-fill input-icon"></i>
                <input id="confirmPassword" v-model="form.confirmPassword"
                    :type="showConfirmPassword ? 'text' : 'password'" class="form-input"
                    :class="{ 'is-invalid': form.confirmPassword && !isPasswordMatch }" placeholder="Confirm password"
                    required :disabled="authStore.loading" />
                <button type="button" class="password-toggle" @click="showConfirmPassword = !showConfirmPassword"
                    :disabled="authStore.loading">
                    <i :class="showConfirmPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                </button>
            </div>
            <div v-if="form.confirmPassword && !isPasswordMatch" class="invalid-feedback">
                Passwords don't match
            </div>
        </div>

        <button type="submit" class="btn-auth-primary w-100 mb-3" :disabled="authStore.loading || !isFormValid">
            <span v-if="authStore.loading" class="spinner me-2"></span>
            <i v-else class="bi bi-person-plus me-2"></i>
            {{ authStore.loading ? 'Creating account...' : 'Create Account' }}
        </button>
    </form>

    <div class="auth-divider mb-3">
        <span>Already have an account?</span>
    </div>

    <router-link to="/login" class="btn-auth-secondary w-100">
        <i class="bi bi-arrow-right me-2"></i>
        Sign in to your account
    </router-link>
</template>

<script setup>
import { reactive, ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/utils/useToast'

const router = useRouter()
const authStore = useAuthStore()
const { showSuccess, showError } = useToast()

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const passwordStrength = ref(0)

const form = reactive({
    name: '',
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
})

// Watch password changes to update strength
watch(() => form.password, (newPassword) => {
    validatePassword()
})

const isPasswordMatch = computed(() => {
    return form.password === form.confirmPassword
})

const strengthPercentage = computed(() => {
    return (passwordStrength.value / 4) * 100
})

const strengthClass = computed(() => {
    const classes = ['strength-weak', 'strength-weak', 'strength-fair', 'strength-good', 'strength-strong']
    return classes[passwordStrength.value] || 'strength-weak'
})

const strengthText = computed(() => {
    const texts = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong']
    return texts[passwordStrength.value] || 'Very Weak'
})

const strengthTextClass = computed(() => {
    const classes = ['text-danger', 'text-danger', 'text-warning', 'text-success', 'text-success']
    return classes[passwordStrength.value] || 'text-danger'
})

const isFormValid = computed(() => {
    return form.name.trim() &&
        form.email.trim() &&
        form.username.trim() &&
        form.password &&
        isPasswordMatch.value &&
        passwordStrength.value >= 2
})

const validatePassword = () => {
    const password = form.password
    let strength = 0

    if (password.length >= 6) strength++
    if (password.match(/[a-z]/)) strength++
    if (password.match(/[A-Z]/)) strength++
    if (password.match(/[0-9]/)) strength++
    if (password.match(/[^a-zA-Z0-9]/)) strength++

    passwordStrength.value = Math.min(strength, 4)
}

const handleRegister = async () => {
    if (!isFormValid.value) return

    try {
        await authStore.register({
            name: form.name,
            email: form.email,
            username: form.username,
            password: form.password
        })

        if (!authStore.error) {
            showSuccess('Account created successfully! Welcome to Quizzo.')
            router.push('/dashboard')
        } else {
            showError(authStore.error)
        }
    } catch (error) {
        console.error('Registration failed:', error)
        showError('Registration failed. Please try again.')
    }
}
</script>

<style scoped></style>

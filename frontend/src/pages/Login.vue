<template>
    <div class="mb-3">
        <router-link to="/" class="btn-auth-back">
            <i class="bi bi-arrow-left me-2"></i>
            Back to Home
        </router-link>
    </div>

    <div class="auth-header mb-4 text-center">
        <div class="auth-title-wrapper mb-2">
            <i class="bi bi-box-arrow-in-right auth-title-icon me-2"></i>
            <h1 class="auth-title">Welcome Back</h1>
        </div>
        <p class="auth-subtitle">Continue your learning journey with Quizzo</p>
    </div>

    <form @submit.prevent="handleLogin" class="auth-form">
        <div class="input-group-modern mb-3">
            <div class="input-wrapper">
                <i class="bi bi-envelope input-icon"></i>
                <input id="email" v-model="form.email" type="email" class="form-input" placeholder="Email address"
                    required :disabled="authStore.loading" />
            </div>
        </div>

        <div class="input-group-modern mb-3">
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

        <button type="submit" class="btn-auth-primary w-100 mb-4" :disabled="authStore.loading">
            <span v-if="authStore.loading" class="spinner me-2"></span>
            <i v-else class="bi bi-arrow-right me-2"></i>
            {{ authStore.loading ? 'Signing in...' : 'Sign In' }}
        </button>
    </form>

    <div class="auth-divider mb-3">
        <span>New to Quizzo?</span>
    </div>

    <router-link to="/register" class="btn-auth-secondary w-100">
        <i class="bi bi-person-plus me-2"></i>
        Create your account
    </router-link>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/utils/useToast'

const router = useRouter()
const authStore = useAuthStore()
const { showSuccess, showError } = useToast()

const showPassword = ref(false)
const form = reactive({
    email: '',
    password: ''
})

const handleLogin = async () => {
    authStore.clearError()
    const result = await authStore.login({
        email: form.email,
        password: form.password
    })
    if (result.success) {
        showSuccess('Login successful! Welcome back.')
        if (authStore.isAdmin) {
            router.push('/admin')
        } else {
            router.push('/dashboard')
        }
    } else {
        showError(result.error || 'Login failed')
    }
}
</script>

<style scoped></style>

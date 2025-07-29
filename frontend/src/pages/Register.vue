<template>
  <div class="register-page animate-fade-in">
    <div class="welcome-header mb-4 text-center animate-slide-up">
      <div class="welcome-icon mb-3">
        <i class="bi bi-person-plus text-gradient"></i>
      </div>
      <h2 class="fw-bold mb-2">Join Quizzo</h2>
      <p class="text-muted">Create your account and start learning today</p>
    </div>

    <!-- Error Alert -->
    <div v-if="authStore.error" class="alert alert-danger animate-shake" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ authStore.error }}
    </div>

    <!-- Registration Form -->
    <form @submit.prevent="handleRegister" class="register-form animate-slide-up" style="animation-delay: 0.2s;">
      <div class="form-floating mb-3">
        <input
          id="name"
          v-model="form.name"
          type="text"
          class="form-control form-control-modern"
          placeholder="Enter your full name"
          required
          :disabled="authStore.loading"
        />
        <label for="name">
          <i class="bi bi-person me-2"></i>
          Full Name
        </label>
      </div>

      <div class="form-floating mb-3">
        <input
          id="username"
          v-model="form.username"
          type="text"
          class="form-control form-control-modern"
          placeholder="Choose a username"
          required
          :disabled="authStore.loading"
          @input="validateUsername"
        />
        <label for="username">
          <i class="bi bi-at me-2"></i>
          Username
        </label>
        <div class="form-text mt-2">
          <i class="bi bi-info-circle me-1"></i>
          This will be your unique identifier on Quizzo
        </div>
      </div>

      <div class="form-floating mb-3">
        <input
          id="email"
          v-model="form.email"
          type="email"
          class="form-control form-control-modern"
          placeholder="Enter your email"
          required
          :disabled="authStore.loading"
        />
        <label for="email">
          <i class="bi bi-envelope me-2"></i>
          Email Address
        </label>
      </div>

      <div class="form-floating mb-3">
        <div class="input-group">
          <input
            id="password"
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            class="form-control form-control-modern"
            placeholder="Create a password"
            required
            minlength="6"
            :disabled="authStore.loading"
            @input="validatePassword"
          />
          <button
            type="button"
            class="btn btn-outline-secondary password-toggle"
            @click="showPassword = !showPassword"
            :disabled="authStore.loading"
            tabindex="-1"
          >
            <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
          </button>
        </div>
        <label for="password">
          <i class="bi bi-lock me-2"></i>
          Password
        </label>
        <div class="password-strength mt-2">
          <div class="password-strength-bar">
            <div class="strength-segment" :class="{ active: passwordStrength >= 1 }"></div>
            <div class="strength-segment" :class="{ active: passwordStrength >= 2 }"></div>
            <div class="strength-segment" :class="{ active: passwordStrength >= 3 }"></div>
            <div class="strength-segment" :class="{ active: passwordStrength >= 4 }"></div>
          </div>
          <small class="text-muted">{{ passwordStrengthText }}</small>
        </div>
      </div>

      <div class="form-floating mb-3">
        <input
          id="confirmPassword"
          v-model="form.confirmPassword"
          type="password"
          class="form-control form-control-modern"
          placeholder="Confirm your password"
          required
          :disabled="authStore.loading"
          :class="{ 'is-invalid': form.confirmPassword && form.password !== form.confirmPassword }"
        />
        <label for="confirmPassword">
          <i class="bi bi-shield-check me-2"></i>
          Confirm Password
        </label>
        <div v-if="form.confirmPassword && form.password !== form.confirmPassword" class="invalid-feedback">
          <i class="bi bi-x-circle me-1"></i>
          Passwords do not match
        </div>
      </div>

      <div class="terms-section mb-4">
        <div class="form-check">
          <input
            id="terms"
            v-model="form.acceptTerms"
            type="checkbox"
            class="form-check-input"
            required
            :disabled="authStore.loading"
          />
          <label for="terms" class="form-check-label">
            I agree to the 
            <a href="#" class="text-decoration-none link-primary">Terms of Service</a> 
            and 
            <a href="#" class="text-decoration-none link-primary">Privacy Policy</a>
          </label>
        </div>
      </div>

      <button
        type="submit"
        class="btn btn-primary w-100 btn-modern mb-4"
        :disabled="authStore.loading || form.password !== form.confirmPassword || !form.acceptTerms || passwordStrength < 2"
      >
        <span v-if="authStore.loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
        <i v-else class="bi bi-rocket-takeoff me-2"></i>
        {{ authStore.loading ? 'Creating Account...' : 'Create Account' }}
      </button>
    </form>

    <!-- Divider -->
    <div class="divider-section mb-4 animate-fade-in" style="animation-delay: 0.4s;">
      <div class="divider">
        <span class="divider-text">Already have an account?</span>
      </div>
    </div>

    <!-- Login Link -->
    <router-link to="/login" class="btn btn-outline-primary w-100 btn-modern animate-slide-up" style="animation-delay: 0.6s;">
      <i class="bi bi-box-arrow-in-right me-2"></i>
      Sign In Instead
    </router-link>

    <!-- Benefits -->
    <div class="benefits-section mt-4 animate-fade-in" style="animation-delay: 0.8s;">
      <div class="row g-2">
        <div class="col-12">
          <div class="benefit-item">
            <i class="bi bi-check-circle-fill text-success me-2"></i>
            <span class="text-muted">Free forever with no hidden fees</span>
          </div>
        </div>
        <div class="col-12">
          <div class="benefit-item">
            <i class="bi bi-check-circle-fill text-success me-2"></i>
            <span class="text-muted">Access to 100+ interactive quizzes</span>
          </div>
        </div>
        <div class="col-12">
          <div class="benefit-item">
            <i class="bi bi-check-circle-fill text-success me-2"></i>
            <span class="text-muted">Personal progress tracking & analytics</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const showPassword = ref(false)
const passwordStrength = ref(0)

const form = reactive({
  name: '',
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  acceptTerms: false
})

const passwordStrengthText = computed(() => {
  const texts = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong']
  return texts[passwordStrength.value] || 'Very Weak'
})

const validateUsername = () => {
  // Add username validation logic here
  const username = form.username
  if (username.length < 3) {
    // Show validation feedback
  }
}

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
  if (form.password !== form.confirmPassword) {
    return
  }

  authStore.clearError()
  
  const result = await authStore.register({
    name: form.name,
    username: form.username,
    email: form.email,
    password: form.password
  })

  if (result.success) {
    router.push('/dashboard')
  }
}
</script>

<style scoped>
.register-page {
  max-width: 420px;
  margin: 0 auto;
}

.welcome-header {
  padding: 1rem 0;
}

.welcome-icon i {
  font-size: 3rem;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.form-floating {
  position: relative;
}

.form-floating > label {
  font-weight: 500;
  color: var(--text-secondary);
  background: transparent;
  padding: 0 0.5rem;
}

.form-control-modern {
  border: 2px solid var(--border);
  border-radius: 16px;
  padding: 1rem 1rem;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: var(--bg-subtle);
  height: 58px;
}

.form-control-modern:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 4px var(--primary-100);
  background: white;
  transform: translateY(-1px);
}

.form-control-modern.is-invalid {
  border-color: #dc3545;
}

.form-control-modern.is-invalid:focus {
  box-shadow: 0 0 0 4px rgba(220, 53, 69, 0.25);
}

.input-group .form-control-modern {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  border-right: none;
}

.password-toggle {
  border: 2px solid var(--border);
  border-left: none;
  border-top-right-radius: 16px;
  border-bottom-right-radius: 16px;
  background: var(--bg-subtle);
  transition: all 0.3s ease;
}

.password-toggle:hover {
  background: var(--primary-50);
  color: var(--primary);
}

.form-control-modern:focus + .password-toggle {
  border-color: var(--primary);
  background: white;
}

.password-strength {
  margin-top: 0.5rem;
}

.password-strength-bar {
  display: flex;
  gap: 4px;
  margin-bottom: 0.25rem;
}

.strength-segment {
  height: 4px;
  flex: 1;
  background: #e5e7eb;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.strength-segment.active {
  background: var(--primary);
}

.strength-segment:nth-child(1).active {
  background: #dc2626; /* Red */
}

.strength-segment:nth-child(2).active {
  background: #f59e0b; /* Orange */
}

.strength-segment:nth-child(3).active {
  background: #eab308; /* Yellow */
}

.strength-segment:nth-child(4).active {
  background: #22c55e; /* Green */
}

.btn-modern {
  padding: 1rem 2rem;
  font-weight: 600;
  border-radius: 16px;
  font-size: 1.1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.terms-section {
  background: var(--bg-subtle);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid var(--border);
}

.divider {
  position: relative;
  text-align: center;
  margin: 1.5rem 0;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--border);
}

.divider-text {
  background: white;
  padding: 0 1rem;
  color: var(--text-muted);
  font-size: 0.9rem;
  font-weight: 500;
}

.benefit-item {
  display: flex;
  align-items: center;
  padding: 0.5rem 0;
  font-size: 0.9rem;
}

.alert {
  border: none;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  font-weight: 500;
}

.alert-danger {
  background: #fef2f2;
  color: #dc2626;
  border-left: 4px solid #dc2626;
}

.invalid-feedback {
  display: block;
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  font-weight: 500;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.animate-shake {
  animation: shake 0.5s ease-in-out;
}

/* Form validation styles */
.form-check-input:focus {
  box-shadow: 0 0 0 4px var(--primary-100);
}

.form-check-input:checked {
  background-color: var(--primary);
  border-color: var(--primary);
}

.link-primary {
  color: var(--primary) !important;
  font-weight: 500;
}

.link-primary:hover {
  color: var(--primary-dark) !important;
}

/* Loading spinner */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 2px;
}

/* Responsive adjustments */
@media (max-width: 576px) {
  .register-page {
    padding: 0 1rem;
  }
  
  .welcome-icon i {
    font-size: 2.5rem;
  }
  
  .btn-modern {
    font-size: 1rem;
    padding: 0.875rem 1.5rem;
  }
}
</style>

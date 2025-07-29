<template>
  <div class="login-page animate-fade-in">
    <div class="welcome-header mb-4 text-center animate-slide-up">
      <div class="welcome-icon mb-3">
        <i class="bi bi-box-arrow-in-right text-gradient"></i>
      </div>
      <h2 class="fw-bold mb-2">Welcome Back</h2>
      <p class="text-muted">Sign in to continue your learning journey</p>
    </div>

    <!-- Error Alert -->
    <div v-if="authStore.error" class="alert alert-danger animate-shake" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ authStore.error }}
    </div>

    <!-- Login Form -->
    <form @submit.prevent="handleLogin" class="login-form animate-slide-up" style="animation-delay: 0.2s;">
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
            placeholder="Enter your password"
            required
            :disabled="authStore.loading"
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
      </div>

      <div class="d-flex justify-content-between align-items-center mb-4">
        <div class="form-check">
          <input
            id="remember"
            v-model="form.remember"
            type="checkbox"
            class="form-check-input"
            :disabled="authStore.loading"
          />
          <label for="remember" class="form-check-label text-muted">
            Remember me
          </label>
        </div>
        <a href="#" class="text-decoration-none forgot-link">
          Forgot password?
        </a>
      </div>

      <button
        type="submit"
        class="btn btn-primary w-100 btn-modern mb-4"
        :disabled="authStore.loading"
      >
        <span v-if="authStore.loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
        <i v-else class="bi bi-arrow-right-circle me-2"></i>
        {{ authStore.loading ? 'Signing In...' : 'Sign In' }}
      </button>
    </form>

    <!-- Divider -->
    <div class="divider-section mb-4 animate-fade-in" style="animation-delay: 0.4s;">
      <div class="divider">
        <span class="divider-text">New to Quizzo?</span>
      </div>
    </div>

    <!-- Register Link -->
    <router-link to="/register" class="btn btn-outline-primary w-100 btn-modern animate-slide-up" style="animation-delay: 0.6s;">
      <i class="bi bi-person-plus me-2"></i>
      Create Your Account
    </router-link>

    <!-- Quick Features -->
    <div class="quick-features mt-4 animate-fade-in" style="animation-delay: 0.8s;">
      <div class="row g-2 text-center">
        <div class="col-4">
          <div class="feature-mini">
            <i class="bi bi-shield-check text-success"></i>
            <small class="text-muted d-block">Secure</small>
          </div>
        </div>
        <div class="col-4">
          <div class="feature-mini">
            <i class="bi bi-lightning-charge text-warning"></i>
            <small class="text-muted d-block">Fast</small>
          </div>
        </div>
        <div class="col-4">
          <div class="feature-mini">
            <i class="bi bi-heart-fill text-danger"></i>
            <small class="text-muted d-block">Loved</small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const showPassword = ref(false)
const form = reactive({
  email: '',
  password: '',
  remember: false
})

const handleLogin = async () => {
  authStore.clearError()
  
  const result = await authStore.login({
    email: form.email,
    password: form.password,
    remember: form.remember
  })

  if (result.success) {
    // Redirect based on user role
    if (authStore.isAdmin) {
      router.push('/admin')
    } else {
      router.push('/dashboard')
    }
  }
}
</script>

<style scoped>
.login-page {
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

.btn-modern {
  padding: 1rem 2rem;
  font-weight: 600;
  border-radius: 16px;
  font-size: 1.1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.forgot-link {
  color: var(--primary);
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.forgot-link:hover {
  color: var(--primary-dark);
  text-decoration: underline !important;
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

.feature-mini {
  padding: 0.5rem;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.feature-mini:hover {
  background: var(--bg-subtle);
  transform: translateY(-2px);
}

.feature-mini i {
  font-size: 1.25rem;
  margin-bottom: 0.25rem;
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

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.animate-shake {
  animation: shake 0.5s ease-in-out;
}

/* Loading spinner */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 2px;
}

/* Focus styles */
.form-check-input:focus {
  box-shadow: 0 0 0 4px var(--primary-100);
}

.form-check-input:checked {
  background-color: var(--primary);
  border-color: var(--primary);
}

/* Responsive adjustments */
@media (max-width: 576px) {
  .login-page {
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

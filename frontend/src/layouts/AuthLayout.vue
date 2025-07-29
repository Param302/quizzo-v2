<template>
  <div class="auth-layout">
    <div class="container-fluid h-100">
      <div class="row h-100">
        <div class="col-lg-5 col-md-4 auth-branding d-none d-md-flex align-items-center justify-content-center">
          <div class="text-center">
            <h1 class="display-3 fw-bold mb-3">Quizzo</h1>
            <p class="lead fs-4 fw-medium fst-italic">
              Challenge your knowledge with interactive quizzes!
            </p>
          </div>
        </div>

        <div class="col-lg-7 col-md-8 d-flex align-items-center justify-content-center auth-form-container">
          <div class="auth-form-wrapper w-100">
            <div class="text-center mb-4 d-md-none">
              <h2 class="fw-bold mobile-branding">Quizzo</h2>
            </div>

            <Transition name="fade" mode="out-in">
              <router-view />
            </Transition>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  height: 100vh;
  overflow: hidden;
}

.auth-branding {
  background: linear-gradient(135deg, #f57c00 0%, #e65100 100%);
  color: white;
}

.auth-form-wrapper {
  max-width: 450px;
  padding: 0;
  background: transparent;
  border: none;
  box-shadow: none;
}

.auth-form-container {
  background: transparent;
  border: none;
  box-shadow: none;
}

.mobile-branding {
  color: #f57c00;
  background: transparent;
  font-size: 2.5rem;
}

:deep(.auth-title-wrapper) {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

:deep(.auth-title-icon) {
  color: #f57c00;
  font-size: 1.75rem;
  font-weight: 900;
}

:deep(.auth-title) {
  font-size: 1.75rem;
  font-weight: 700;
  color: #f57c00;
  margin: 0;
  display: inline;
}

:deep(.auth-subtitle) {
  color: #6c757d;
  font-size: 0.95rem;
  margin: 0;
}

:deep(.auth-form) {
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
  margin: 0;
}

:deep(.btn-auth-back) {
  display: inline-flex;
  align-items: center;
  color: #6c757d;
  text-decoration: none;
  font-size: 0.9rem;
  padding: 0.5rem 0;
  transition: color 0.3s ease;
}

:deep(.btn-auth-back:hover) {
  color: #f57c00;
  text-decoration: none;
}

:deep(.input-group-modern) {
  position: relative;
}

:deep(.input-wrapper) {
  position: relative;
  display: flex;
  align-items: center;
}

:deep(.form-input) {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 3rem;
  border: none;
  background: rgba(245, 124, 0, 0.05);
  border-radius: 12px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  outline: none;
}

:deep(.form-input:focus) {
  background: rgba(245, 124, 0, 0.1);
  box-shadow: 0 0 0 3px rgba(245, 124, 0, 0.1);
  transform: translateY(-1px);
}

:deep(.form-input::placeholder) {
  color: #adb5bd;
  font-weight: 400;
}

:deep(.input-icon) {
  position: absolute;
  left: 1rem;
  color: #f57c00;
  font-size: 1.1rem;
  z-index: 2;
}

:deep(.password-toggle) {
  position: absolute;
  right: 1rem;
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: color 0.3s ease;
  z-index: 2;
}

:deep(.password-toggle:hover) {
  color: #f57c00;
}

:deep(.form-options) {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.checkbox-wrapper) {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

:deep(.checkbox-wrapper input[type="checkbox"]) {
  position: absolute;
  opacity: 0;
  cursor: pointer;
}

:deep(.checkmark) {
  width: 18px;
  height: 18px;
  background: rgba(245, 124, 0, 0.1);
  border-radius: 4px;
  margin-right: 0.5rem;
  position: relative;
  transition: all 0.3s ease;
}

:deep(.checkbox-wrapper input:checked + .checkmark) {
  background: linear-gradient(135deg, #f57c00, #e65100);
}

:deep(.checkbox-wrapper input:checked + .checkmark::after) {
  content: "✓";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

:deep(.checkbox-label) {
  font-size: 0.9rem;
  color: #6c757d;
}

:deep(.forgot-link) {
  color: #f57c00;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

:deep(.forgot-link:hover) {
  color: #e65100;
  text-decoration: underline;
}

:deep(.password-strength) {
  margin-top: 0.5rem;
}

:deep(.strength-meter) {
  height: 4px;
  background: #e9ecef;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.25rem;
}

:deep(.strength-fill) {
  height: 100%;
  transition: all 0.3s ease;
  border-radius: 2px;
}

:deep(.strength-weak) {
  background: #dc3545;
}

:deep(.strength-fair) {
  background: #fd7e14;
}

:deep(.strength-good) {
  background: #ffc107;
}

:deep(.strength-strong) {
  background: #28a745;
}

:deep(.strength-text) {
  font-size: 0.8rem;
  font-weight: 500;
}

:deep(.text-danger) {
  color: #dc3545;
}

:deep(.text-warning) {
  color: #fd7e14;
}

:deep(.text-info) {
  color: #ffc107;
}

:deep(.text-success) {
  color: #28a745;
}

:deep(.btn-auth-primary) {
  background: linear-gradient(135deg, #f57c00, #e65100);
  border: none;
  padding: 0.875rem 1.5rem;
  border-radius: 12px;
  color: white;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.btn-auth-primary:hover:not(:disabled)) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 124, 0, 0.3);
}

:deep(.btn-auth-primary:disabled) {
  opacity: 0.7;
  cursor: not-allowed;
}

:deep(.btn-auth-secondary) {
  background: rgba(245, 124, 0, 0.1);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  color: #f57c00;
  font-weight: 600;
  font-size: 0.95rem;
  text-decoration: none;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.btn-auth-secondary:hover) {
  background: rgba(245, 124, 0, 0.15);
  color: #e65100;
  text-decoration: none;
  transform: translateY(-1px);
}

:deep(.auth-divider) {
  position: relative;
  text-align: center;
  margin: 1.5rem 0;
  z-index: 1;
}

:deep(.auth-divider::before) {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #e9ecef;
  z-index: 0;
}

:deep(.auth-divider span) {
  background: white;
  padding: 0.5rem;
  color: var(--bs-secondary);
  font-size: 0.9rem;
  position: relative;
  z-index: 2;
}

:deep(.spinner) {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

:deep(.is-invalid) {
  background: rgba(220, 53, 69, 0.05);
}

:deep(.invalid-feedback) {
  color: #dc3545;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

@media (max-width: 767.98px) {
  .auth-form-wrapper {
    padding: 0;
    background: transparent;
    border: none;
    box-shadow: none;
  }
}
</style>

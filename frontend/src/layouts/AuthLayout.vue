<template>
  <div class="auth-layout">
    <div class="container-fluid h-100">
      <div class="row h-100">
        <!-- Left side - Branding -->
        <div class="col-md-6 auth-branding d-none d-md-flex">
          <div class="text-center">
            <h1 class="display-3 fw-bold mb-4">Quizzo</h1>
            <p class="lead fs-4">
              Challenge your knowledge with interactive quizzes
            </p>
            <div class="mt-5">
              <div class="d-flex justify-content-center gap-4">
                <div class="text-center">
                  <div class="display-6 fw-bold">500+</div>
                  <small>Active Users</small>
                </div>
                <div class="text-center">
                  <div class="display-6 fw-bold">100+</div>
                  <small>Quizzes</small>
                </div>
                <div class="text-center">
                  <div class="display-6 fw-bold">50+</div>
                  <small>Categories</small>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Right side - Form -->
        <div class="col-md-6 d-flex align-items-center justify-content-center bg-light">
          <div class="auth-form w-100" style="max-width: 400px;">
            <!-- Mobile branding -->
            <div class="text-center mb-4 d-md-none">
              <h2 class="fw-bold text-primary">Quizzo</h2>
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
// No additional logic needed for this layout
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
}

.auth-branding {
  background: linear-gradient(135deg, #f57c00 0%, #e65100 100%);
  color: white;
}

.auth-form {
  padding: 2rem;
}

@media (max-width: 767.98px) {
  .auth-form {
    padding: 1.5rem;
  }
}
</style>

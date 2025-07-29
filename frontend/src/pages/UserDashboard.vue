<template>
  <div class="dashboard">
    <div class="container py-4">
      <div class="row">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 class="fw-bold">Welcome back, {{ authStore.userName }}!</h1>
              <p class="text-muted mb-0">Ready to test your knowledge today?</p>
            </div>
            <div>
              <button class="btn btn-primary">
                <i class="bi bi-plus-circle me-2"></i>
                Take Quiz
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="row g-4 mb-4">
        <div class="col-md-3">
          <div class="card">
            <div class="card-body text-center">
              <i class="bi bi-trophy-fill text-warning fs-2 mb-2"></i>
              <h4 class="fw-bold">12</h4>
              <small class="text-muted">Quizzes Completed</small>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card">
            <div class="card-body text-center">
              <i class="bi bi-graph-up text-success fs-2 mb-2"></i>
              <h4 class="fw-bold">85%</h4>
              <small class="text-muted">Average Score</small>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card">
            <div class="card-body text-center">
              <i class="bi bi-clock-fill text-warning fs-2 mb-2"></i>
              <h4 class="fw-bold">2h 30m</h4>
              <small class="text-muted">Time Spent</small>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card">
            <div class="card-body text-center">
              <i class="bi bi-award-fill text-info fs-2 mb-2"></i>
              <h4 class="fw-bold">#15</h4>
              <small class="text-muted">Global Rank</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Quizzes -->
      <div class="row">
        <div class="col-lg-8">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">Available Quizzes</h5>
            </div>
            <div class="card-body">
              <div class="list-group list-group-flush">
                <div class="list-group-item d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="mb-1">JavaScript Fundamentals</h6>
                    <small class="text-muted">20 questions • 15 minutes</small>
                  </div>
                  <button class="btn btn-sm btn-primary">Start</button>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="mb-1">Python Basics</h6>
                    <small class="text-muted">15 questions • 12 minutes</small>
                  </div>
                  <button class="btn btn-sm btn-primary">Start</button>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="mb-1">Web Development</h6>
                    <small class="text-muted">25 questions • 20 minutes</small>
                  </div>
                  <button class="btn btn-sm btn-primary">Start</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-lg-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">Recent Activity</h5>
            </div>
            <div class="card-body">
              <div class="d-flex align-items-center mb-3">
                <div class="rounded-circle bg-success text-white d-flex align-items-center justify-content-center me-3" 
                     style="width: 40px; height: 40px;">
                  <i class="bi bi-check"></i>
                </div>
                <div>
                  <div class="fw-semibold">React Quiz</div>
                  <small class="text-muted">Scored 90% • 2 hours ago</small>
                </div>
              </div>
              <div class="d-flex align-items-center mb-3">
                <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-3" 
                     style="width: 40px; height: 40px;">
                  <i class="bi bi-trophy"></i>
                </div>
                <div>
                  <div class="fw-semibold">Achievement Unlocked</div>
                  <small class="text-muted">Quiz Master • Yesterday</small>
                </div>
              </div>
              <div class="d-flex align-items-center">
                <div class="rounded-circle bg-warning text-white d-flex align-items-center justify-content-center me-3" 
                     style="width: 40px; height: 40px;">
                  <i class="bi bi-star"></i>
                </div>
                <div>
                  <div class="fw-semibold">New Level</div>
                  <small class="text-muted">Reached Level 5 • 2 days ago</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<style scoped>
.card {
  transition: transform 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
}
</style>

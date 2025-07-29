<template>
    <div class="admin-dashboard">
        <div class="container py-4">
            <div class="row">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <div>
                            <h1 class="fw-bold">Admin Dashboard</h1>
                            <p class="text-muted mb-0">Welcome back, {{ authStore.userName }}</p>
                        </div>
                        <div>
                            <button class="btn btn-primary">
                                <i class="bi bi-plus-circle me-2"></i>
                                Create Quiz
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Overview Stats -->
            <div class="row g-4 mb-4">
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <i class="bi bi-people-fill fs-2 mb-2"></i>
                            <h4 class="fw-bold">1,234</h4>
                            <small>Total Users</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <i class="bi bi-question-circle-fill fs-2 mb-2"></i>
                            <h4 class="fw-bold">89</h4>
                            <small>Total Quizzes</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-warning text-white">
                        <div class="card-body text-center">
                            <i class="bi bi-clipboard-check-fill fs-2 mb-2"></i>
                            <h4 class="fw-bold">5,678</h4>
                            <small>Quiz Attempts</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <i class="bi bi-graph-up fs-2 mb-2"></i>
                            <h4 class="fw-bold">82%</h4>
                            <small>Avg Score</small>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <!-- Recent Activity -->
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Recent Activity</h5>
                            <router-link to="/admin/users" class="btn btn-sm btn-outline-primary">
                                View All Users
                            </router-link>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>User</th>
                                            <th>Action</th>
                                            <th>Quiz</th>
                                            <th>Score</th>
                                            <th>Time</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>
                                                <div class="d-flex align-items-center">
                                                    <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-2"
                                                        style="width: 30px; height: 30px; font-size: 12px;">
                                                        JD
                                                    </div>
                                                    John Doe
                                                </div>
                                            </td>
                                            <td><span class="badge bg-success">Completed</span></td>
                                            <td>JavaScript Basics</td>
                                            <td>92%</td>
                                            <td>2 min ago</td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <div class="d-flex align-items-center">
                                                    <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-2"
                                                        style="width: 30px; height: 30px; font-size: 12px;">
                                                        AS
                                                    </div>
                                                    Alice Smith
                                                </div>
                                            </td>
                                            <td><span class="badge bg-info">Started</span></td>
                                            <td>Python Fundamentals</td>
                                            <td>-</td>
                                            <td>5 min ago</td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <div class="d-flex align-items-center">
                                                    <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-2"
                                                        style="width: 30px; height: 30px; font-size: 12px;">
                                                        BJ
                                                    </div>
                                                    Bob Johnson
                                                </div>
                                            </td>
                                            <td><span class="badge bg-success">Completed</span></td>
                                            <td>Web Development</td>
                                            <td>78%</td>
                                            <td>10 min ago</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="col-lg-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Quick Actions</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-grid gap-2">
                                <router-link to="/admin/users" class="btn btn-outline-primary">
                                    <i class="bi bi-people me-2"></i>
                                    Manage Users
                                </router-link>
                                <router-link to="/admin/quizzes" class="btn btn-outline-primary">
                                    <i class="bi bi-question-circle me-2"></i>
                                    Manage Quizzes
                                </router-link>
                                <button class="btn btn-outline-primary">
                                    <i class="bi bi-graph-up me-2"></i>
                                    View Reports
                                </button>
                                <button class="btn btn-outline-primary">
                                    <i class="bi bi-gear me-2"></i>
                                    System Settings
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="card mt-4">
                        <div class="card-header">
                            <h5 class="mb-0">System Status</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <small>Server Status</small>
                                <span class="badge bg-success">Online</span>
                            </div>
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <small>Database</small>
                                <span class="badge bg-success">Connected</span>
                            </div>
                            <div class="d-flex justify-content-between align-items-center">
                                <small>Cache</small>
                                <span class="badge bg-success">Active</span>
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

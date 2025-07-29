<template>
    <div class="admin-users">
        <div class="container py-4">
            <div class="row">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <div>
                            <h1 class="fw-bold">Manage Users</h1>
                            <p class="text-muted mb-0">View and manage all registered users</p>
                        </div>
                        <div>
                            <button class="btn btn-primary">
                                <i class="bi bi-person-plus me-2"></i>
                                Add User
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Filters and Search -->
            <div class="row mb-4">
                <div class="col-md-4">
                    <input type="text" class="form-control" placeholder="Search users...">
                </div>
                <div class="col-md-3">
                    <select class="form-select">
                        <option value="">All Roles</option>
                        <option value="admin">Admin</option>
                        <option value="user">User</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <select class="form-select">
                        <option value="">All Status</option>
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <button class="btn btn-outline-secondary w-100">
                        <i class="bi bi-funnel me-2"></i>
                        Filter
                    </button>
                </div>
            </div>

            <!-- Users Table -->
            <div class="card">
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>User</th>
                                    <th>Role</th>
                                    <th>Status</th>
                                    <th>Join Date</th>
                                    <th>Quizzes</th>
                                    <th>Avg Score</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>
                                        <div class="d-flex align-items-center">
                                            <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-3"
                                                style="width: 40px; height: 40px;">
                                                JD
                                            </div>
                                            <div>
                                                <div class="fw-semibold">John Doe</div>
                                                <small class="text-muted">john.doe@example.com</small>
                                            </div>
                                        </div>
                                    </td>
                                    <td><span class="badge bg-primary">User</span></td>
                                    <td><span class="badge bg-success">Active</span></td>
                                    <td>Jan 15, 2024</td>
                                    <td>45</td>
                                    <td>87%</td>
                                    <td>
                                        <div class="btn-group btn-group-sm">
                                            <button class="btn btn-outline-primary">
                                                <i class="bi bi-eye"></i>
                                            </button>
                                            <button class="btn btn-outline-warning">
                                                <i class="bi bi-pencil"></i>
                                            </button>
                                            <button class="btn btn-outline-danger">
                                                <i class="bi bi-trash"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <div class="d-flex align-items-center">
                                            <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-3"
                                                style="width: 40px; height: 40px;">
                                                AS
                                            </div>
                                            <div>
                                                <div class="fw-semibold">Alice Smith</div>
                                                <small class="text-muted">alice.smith@example.com</small>
                                            </div>
                                        </div>
                                    </td>
                                    <td><span class="badge bg-danger">Admin</span></td>
                                    <td><span class="badge bg-success">Active</span></td>
                                    <td>Dec 8, 2023</td>
                                    <td>23</td>
                                    <td>92%</td>
                                    <td>
                                        <div class="btn-group btn-group-sm">
                                            <button class="btn btn-outline-primary">
                                                <i class="bi bi-eye"></i>
                                            </button>
                                            <button class="btn btn-outline-warning">
                                                <i class="bi bi-pencil"></i>
                                            </button>
                                            <button class="btn btn-outline-danger">
                                                <i class="bi bi-trash"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <div class="d-flex align-items-center">
                                            <div class="rounded-circle bg-secondary text-white d-flex align-items-center justify-content-center me-3"
                                                style="width: 40px; height: 40px;">
                                                BJ
                                            </div>
                                            <div>
                                                <div class="fw-semibold">Bob Johnson</div>
                                                <small class="text-muted">bob.johnson@example.com</small>
                                            </div>
                                        </div>
                                    </td>
                                    <td><span class="badge bg-primary">User</span></td>
                                    <td><span class="badge bg-secondary">Inactive</span></td>
                                    <td>Feb 22, 2024</td>
                                    <td>12</td>
                                    <td>76%</td>
                                    <td>
                                        <div class="btn-group btn-group-sm">
                                            <button class="btn btn-outline-primary">
                                                <i class="bi bi-eye"></i>
                                            </button>
                                            <button class="btn btn-outline-warning">
                                                <i class="bi bi-pencil"></i>
                                            </button>
                                            <button class="btn btn-outline-danger">
                                                <i class="bi bi-trash"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Pagination -->
            <nav class="mt-4" aria-label="Users pagination">
                <ul class="pagination justify-content-center">
                    <li class="page-item disabled">
                        <a class="page-link" href="#" tabindex="-1">Previous</a>
                    </li>
                    <li class="page-item active">
                        <a class="page-link" href="#">1</a>
                    </li>
                    <li class="page-item">
                        <a class="page-link" href="#">2</a>
                    </li>
                    <li class="page-item">
                        <a class="page-link" href="#">3</a>
                    </li>
                    <li class="page-item">
                        <a class="page-link" href="#">Next</a>
                    </li>
                </ul>
            </nav>
        </div>
    </div>
</template>

<script setup>
// User management logic would go here
</script>

<style scoped>
.table th {
    border-top: none;
    font-weight: 600;
}

.btn-group-sm .btn {
    padding: 0.25rem 0.5rem;
}
</style>

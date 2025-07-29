<template>
    <div class="admin-quizzes">
        <div class="container py-4">
            <div class="row">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <div>
                            <h1 class="fw-bold">Manage Quizzes</h1>
                            <p class="text-muted mb-0">Create, edit, and manage all quizzes</p>
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

            <!-- Filters and Search -->
            <div class="row mb-4">
                <div class="col-md-4">
                    <input type="text" class="form-control" placeholder="Search quizzes...">
                </div>
                <div class="col-md-3">
                    <select class="form-select">
                        <option value="">All Categories</option>
                        <option value="javascript">JavaScript</option>
                        <option value="python">Python</option>
                        <option value="web">Web Development</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <select class="form-select">
                        <option value="">All Status</option>
                        <option value="published">Published</option>
                        <option value="draft">Draft</option>
                        <option value="archived">Archived</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <button class="btn btn-outline-secondary w-100">
                        <i class="bi bi-funnel me-2"></i>
                        Filter
                    </button>
                </div>
            </div>

            <!-- Quizzes Grid -->
            <div class="row g-4">
                <div class="col-lg-4 col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-3">
                                <span class="badge bg-success">Published</span>
                                <div class="dropdown">
                                    <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="dropdown">
                                        <i class="bi bi-three-dots"></i>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li><a class="dropdown-item" href="#"><i class="bi bi-eye me-2"></i>View</a>
                                        </li>
                                        <li><a class="dropdown-item" href="#"><i class="bi bi-pencil me-2"></i>Edit</a>
                                        </li>
                                        <li><a class="dropdown-item" href="#"><i
                                                    class="bi bi-files me-2"></i>Duplicate</a></li>
                                        <li>
                                            <hr class="dropdown-divider">
                                        </li>
                                        <li><a class="dropdown-item text-danger" href="#"><i
                                                    class="bi bi-trash me-2"></i>Delete</a></li>
                                    </ul>
                                </div>
                            </div>

                            <h5 class="card-title">JavaScript Fundamentals</h5>
                            <p class="card-text text-muted">Test your knowledge of basic JavaScript concepts including
                                variables, functions, and control structures.</p>

                            <div class="row g-2 text-center mb-3">
                                <div class="col-4">
                                    <small class="text-muted">Questions</small>
                                    <div class="fw-semibold">20</div>
                                </div>
                                <div class="col-4">
                                    <small class="text-muted">Duration</small>
                                    <div class="fw-semibold">15 min</div>
                                </div>
                                <div class="col-4">
                                    <small class="text-muted">Attempts</small>
                                    <div class="fw-semibold">234</div>
                                </div>
                            </div>

                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-muted">Created: Jan 15, 2024</small>
                                <button class="btn btn-sm btn-primary">Edit Quiz</button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-lg-4 col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-3">
                                <span class="badge bg-warning">Draft</span>
                                <div class="dropdown">
                                    <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="dropdown">
                                        <i class="bi bi-three-dots"></i>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li><a class="dropdown-item" href="#"><i class="bi bi-eye me-2"></i>Preview</a>
                                        </li>
                                        <li><a class="dropdown-item" href="#"><i class="bi bi-pencil me-2"></i>Edit</a>
                                        </li>
                                        <li><a class="dropdown-item" href="#"><i
                                                    class="bi bi-check-circle me-2"></i>Publish</a></li>
                                        <li>
                                            <hr class="dropdown-divider">
                                        </li>
                                        <li><a class="dropdown-item text-danger" href="#"><i
                                                    class="bi bi-trash me-2"></i>Delete</a></li>
                                    </ul>
                                </div>
                            </div>

                            <h5 class="card-title">Python Advanced Topics</h5>
                            <p class="card-text text-muted">Advanced Python concepts including decorators, generators,
                                and context managers.</p>

                            <div class="row g-2 text-center mb-3">
                                <div class="col-4">
                                    <small class="text-muted">Questions</small>
                                    <div class="fw-semibold">15</div>
                                </div>
                                <div class="col-4">
                                    <small class="text-muted">Duration</small>
                                    <div class="fw-semibold">20 min</div>
                                </div>
                                <div class="col-4">
                                    <small class="text-muted">Attempts</small>
                                    <div class="fw-semibold">0</div>
                                </div>
                            </div>

                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-muted">Created: Jul 28, 2024</small>
                                <button class="btn btn-sm btn-outline-primary">Continue Editing</button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-lg-4 col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-3">
                                <span class="badge bg-success">Published</span>
                                <div class="dropdown">
                                    <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="dropdown">
                                        <i class="bi bi-three-dots"></i>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li><a class="dropdown-item" href="#"><i class="bi bi-eye me-2"></i>View</a>
                                        </li>
                                        <li><a class="dropdown-item" href="#"><i class="bi bi-pencil me-2"></i>Edit</a>
                                        </li>
                                        <li><a class="dropdown-item" href="#"><i
                                                    class="bi bi-files me-2"></i>Duplicate</a></li>
                                        <li>
                                            <hr class="dropdown-divider">
                                        </li>
                                        <li><a class="dropdown-item text-danger" href="#"><i
                                                    class="bi bi-trash me-2"></i>Delete</a></li>
                                    </ul>
                                </div>
                            </div>

                            <h5 class="card-title">Web Development Basics</h5>
                            <p class="card-text text-muted">HTML, CSS, and basic JavaScript for web development
                                beginners.</p>

                            <div class="row g-2 text-center mb-3">
                                <div class="col-4">
                                    <small class="text-muted">Questions</small>
                                    <div class="fw-semibold">25</div>
                                </div>
                                <div class="col-4">
                                    <small class="text-muted">Duration</small>
                                    <div class="fw-semibold">18 min</div>
                                </div>
                                <div class="col-4">
                                    <small class="text-muted">Attempts</small>
                                    <div class="fw-semibold">456</div>
                                </div>
                            </div>

                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-muted">Created: Dec 10, 2023</small>
                                <button class="btn btn-sm btn-primary">Edit Quiz</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Pagination -->
            <nav class="mt-4" aria-label="Quizzes pagination">
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
// Quiz management logic would go here
</script>

<style scoped>
.card {
    transition: transform 0.2s ease;
}

.card:hover {
    transform: translateY(-2px);
}

.dropdown-toggle::after {
    display: none;
}
</style>

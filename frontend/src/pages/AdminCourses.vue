<template>
    <div class="admin-courses-page">
        <!-- Header Section -->
        <section class="courses-header py-4 bg-blur">
            <div class="container">
                <div class="row">
                    <div class="col-12">
                        <!-- Back to Dashboard Link -->
                        <div class="mb-3">
                            <router-link to="/admin" class="btn-back-link">
                                <i class="bi bi-arrow-left me-2"></i>
                                Back to Dashboard
                            </router-link>
                        </div>

                        <!-- Header Content -->
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <h1 class="display-6 fw-bold mb-2 text-orange">Course Management</h1>
                                <p class="lead fw-medium mb-0">Manage courses, chapters, and content structure</p>
                            </div>
                            <div class="col-md-4 text-md-end mt-3 mt-md-0">
                                <div class="course-count-badge mb-3">
                                    <i class="bi bi-book me-2"></i>
                                    <span class="fw-bold">{{ courses.length }}</span>
                                    <span> Course{{ courses.length !== 1 ? 's' : '' }}</span>
                                </div>
                                <div class="text-center text-md-end">
                                    <button class="btn btn-orange" @click="showAddCourseModal = true">
                                        <i class="bi bi-plus-circle me-2"></i>
                                        Add New Course
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Search Section -->
        <section class="search-section py-5">
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-lg-8 text-center">
                        <!-- Search Bar -->
                        <div class="search-container mx-auto">
                            <div class="search-wrapper position-relative">
                                <i class="bi bi-search search-icon"></i>
                                <input type="text" class="form-control search-input"
                                    placeholder="Search courses by name..." v-model="searchQuery" @input="handleSearch">
                                <button v-if="searchQuery" class="btn search-clear-btn" type="button"
                                    @click="clearSearch">
                                    <i class="bi bi-x-lg"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Courses Grid Section -->
        <section class="courses-grid-section pb-5">
            <div class="container">
                <!-- Loading State -->
                <div v-if="loading" class="loading-section">
                    <div class="text-center py-5">
                        <div class="spinner-border text-orange mb-3" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <h5 class="text-muted">Loading courses...</h5>
                    </div>
                </div>

                <!-- No Results -->
                <div v-else-if="courses.length === 0" class="no-results-section">
                    <div class="text-center py-5">
                        <i class="bi bi-book text-muted mb-3" style="font-size: 4rem;"></i>
                        <h4 class="text-muted mb-2">
                            {{ searchQuery ? 'No courses found' : 'No courses yet' }}
                        </h4>
                        <p class="text-muted">
                            {{ searchQuery ? 'Try adjusting your search criteria' : 
                            'Create your first course to get started' }}
                        </p>
                        <button v-if="searchQuery" class="btn btn-orange mt-3" @click="clearSearch">
                            <i class="bi bi-arrow-counterclockwise me-2"></i>
                            Clear Search
                        </button>
                        <button v-else class="btn btn-orange mt-3" @click="showAddCourseModal = true">
                            <i class="bi bi-plus-circle me-2"></i>
                            Add New Course
                        </button>
                    </div>
                </div>

                <!-- Courses Grid -->
                <div v-else>
                    <!-- Courses Cards Grid -->
                    <div class="row g-4">
                        <div v-for="course in courses" :key="course.id" class="col-xl-4 col-lg-4 col-md-6">
                            <AdminCourseCard :course="course" :deleting="deletingCourseId === course.id"
                                :loading="loading" @edit-course="editCourse" @delete-course="confirmDeleteCourse" />
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Course Edit Modal -->
        <AdminCourseModal v-if="selectedCourse" :course="selectedCourse" :show="showCourseModal" :loading="modalLoading"
            @close="closeCourseModal" @save="saveCourse" />

        <!-- Add Course Modal -->
        <AdminCourseModal v-if="showAddCourseModal" :course="newCourse" :show="showAddCourseModal"
            :loading="modalLoading" @close="closeAddCourseModal" @save="addCourse" />

        <!-- Delete Confirmation Modal -->
        <DeleteConfirmationModal :show="showDeleteModal" title="Delete Course"
            message="You are about to permanently delete this course. This will remove all associated chapters, quizzes, and questions."
            :itemDetails="courseToDelete" :loading="deletingCourseId" @close="showDeleteModal = false"
            @confirm="deleteCourse" />

        <!-- Toast Notifications -->
        <Toast v-if="toast.show" :message="toast.message" :variant="toast.type" @close="toast.show = false" />
    </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import AdminCourseCard from '@/components/admin/AdminCourseCard.vue'
import AdminCourseModal from '@/components/admin/AdminCourseModal.vue'
import DeleteConfirmationModal from '@/components/DeleteConfirmationModal.vue'
import Toast from '@/components/Toast.vue'
import axios from 'axios'

export default {
    name: 'AdminCourses',
    components: {
        AdminCourseCard,
        AdminCourseModal,
        DeleteConfirmationModal,
        Toast
    },
    setup() {
        const courses = ref([])
        const loading = ref(false)
        const modalLoading = ref(false)
        const searchQuery = ref('')
        const deletingCourseId = ref(null)
        const showDeleteModal = ref(false)
        const courseToDelete = ref(null)
        const showCourseModal = ref(false)
        const showAddCourseModal = ref(false)
        const selectedCourse = ref(null)

        const newCourse = ref({
            name: '',
            description: '',
            chapters: []
        })

        const toast = ref({
            show: false,
            message: '',
            type: 'success'
        })

        let searchTimeout = null

        const loadCourses = async (search = '') => {
            loading.value = true
            try {
                const params = {
                    detailed: 'true'
                }

                if (search.trim()) {
                    params.search = search.trim()
                }

                const response = await axios.get('/admin/courses', { params })
                courses.value = response.data.courses
            } catch (error) {
                console.error('Error loading courses:', error)
                showToast('Failed to load courses', 'error')
            } finally {
                loading.value = false
            }
        }

        const handleSearch = () => {
            if (searchTimeout) {
                clearTimeout(searchTimeout)
            }

            searchTimeout = setTimeout(() => {
                loadCourses(searchQuery.value)
            }, 500)
        }

        const clearSearch = () => {
            searchQuery.value = ''
            loadCourses('')
        }

        const editCourse = async (courseId) => {
            try {
                modalLoading.value = true
                const response = await axios.get(`/admin/courses/${courseId}`)
                selectedCourse.value = response.data.course
                showCourseModal.value = true
            } catch (error) {
                console.error('Error loading course:', error)
                showToast('Failed to load course details', 'error')
            } finally {
                modalLoading.value = false
            }
        }

        const closeCourseModal = () => {
            selectedCourse.value = null
            showCourseModal.value = false
        }

        const closeAddCourseModal = () => {
            showAddCourseModal.value = false
            newCourse.value = {
                name: '',
                description: '',
                chapters: []
            }
        }

        const addCourse = async (courseData) => {
            try {
                modalLoading.value = true
                const response = await axios.post('/admin/courses', courseData)
                showToast(response.data.message, 'success')
                closeAddCourseModal()
                loadCourses(searchQuery.value)
            } catch (error) {
                console.error('Error adding course:', error)
                showToast(error.response?.data?.message || 'Failed to add course', 'error')
            } finally {
                modalLoading.value = false
            }
        }

        const saveCourse = async (courseData) => {
            try {
                modalLoading.value = true
                const response = await axios.put(`/admin/courses/${selectedCourse.value.id}`, courseData)
                showToast(response.data.message, 'success')
                closeCourseModal()
                loadCourses(searchQuery.value)
            } catch (error) {
                console.error('Error updating course:', error)
                showToast(error.response?.data?.message || 'Failed to update course', 'error')
            } finally {
                modalLoading.value = false
            }
        }

        const confirmDeleteCourse = async (courseId) => {
            const course = courses.value.find(c => c.id === courseId)
            if (!course) return

            courseToDelete.value = course
            showDeleteModal.value = true
        }

        const deleteCourse = async () => {
            if (!courseToDelete.value) return

            deletingCourseId.value = courseToDelete.value.id
            try {
                const response = await axios.delete(`/admin/courses/${courseToDelete.value.id}`)

                // Remove course from local array
                courses.value = courses.value.filter(course => course.id !== courseToDelete.value.id)

                showToast(response.data.message, 'success')
                showDeleteModal.value = false
                courseToDelete.value = null
            } catch (error) {
                console.error('Error deleting course:', error)
                showToast(error.response?.data?.message || 'Failed to delete course', 'error')
            } finally {
                deletingCourseId.value = null
            }
        }

        const showToast = (message, type = 'success') => {
            toast.value = { show: true, message, type }
            setTimeout(() => {
                toast.value.show = false
            }, 5000)
        }

        onMounted(() => {
            loadCourses()
        })

        return {
            courses,
            loading,
            modalLoading,
            searchQuery,
            deletingCourseId,
            showDeleteModal,
            courseToDelete,
            showCourseModal,
            showAddCourseModal,
            selectedCourse,
            newCourse,
            toast,
            loadCourses,
            handleSearch,
            clearSearch,
            editCourse,
            closeCourseModal,
            closeAddCourseModal,
            addCourse,
            saveCourse,
            confirmDeleteCourse,
            deleteCourse,
            showToast
        }
    }
}
</script>

<style scoped>
.admin-courses-page {
    min-height: 100vh;
    background: linear-gradient(135deg, rgba(245, 124, 0, 0.05) 0%, rgba(245, 124, 0, 0.02) 100%);
}

.courses-header {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(245, 124, 0, 0.1);
}

.btn-back-link {
    color: #f57c00;
    text-decoration: none;
    font-weight: 600;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    transition: all 0.3s ease;
    background: rgba(245, 124, 0, 0.1);
    border: 1px solid rgba(245, 124, 0, 0.2);
    display: inline-block;
}

.btn-back-link:hover {
    background: rgba(245, 124, 0, 0.15);
    color: #e65100;
    text-decoration: none;
    transform: translateX(-2px);
}

.text-orange {
    color: #f57c00;
}

.course-count-badge {
    background: linear-gradient(135deg, rgba(245, 124, 0, 0.1) 0%, rgba(245, 124, 0, 0.05) 100%);
    border: 2px solid rgba(245, 124, 0, 0.2);
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    color: #f57c00;
    font-size: 1.1rem;
    display: inline-flex;
    align-items: center;
    transition: all 0.3s ease;
}

.course-count-badge:hover {
    background: linear-gradient(135deg, rgba(245, 124, 0, 0.15) 0%, rgba(245, 124, 0, 0.08) 100%);
    border-color: rgba(245, 124, 0, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.2);
}

.btn-outline-orange {
    border: 2px solid #f57c00;
    color: #f57c00;
    background: transparent;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.btn-outline-orange:hover {
    background: #f57c00;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.btn-orange {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border: none;
    color: white;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    padding: 0.75rem 1.5rem;
}

.btn-orange:hover {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.4);
}

.search-container {
    max-width: 600px;
}

.search-wrapper {
    position: relative;
}

.search-icon {
    position: absolute;
    left: 1.5rem;
    top: 50%;
    transform: translateY(-50%);
    color: #f57c00;
    font-size: 1.2rem;
    z-index: 2;
}

.search-input {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border: 2px solid rgba(245, 124, 0, 0.2);
    border-radius: 50px;
    padding: 1.2rem 4.5rem 1.2rem 4rem;
    font-size: 1.1rem;
    transition: all 0.3s ease;
    box-shadow: 0 8px 32px rgba(245, 124, 0, 0.1);
}

.search-input:focus {
    border-color: #f57c00;
    box-shadow: 0 0 0 0.25rem rgba(245, 124, 0, 0.15), 0 12px 40px rgba(245, 124, 0, 0.2);
    background: rgba(255, 255, 255, 1);
    outline: none;
}

.search-input::placeholder {
    color: rgba(117, 117, 117, 0.8);
}

.search-clear-btn {
    position: absolute;
    right: 0.5rem;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: #6c757d;
    padding: 0.5rem;
    border-radius: 50%;
    transition: all 0.3s ease;
    z-index: 3;
}

.search-clear-btn:hover {
    background: rgba(220, 53, 69, 0.1);
    color: #dc3545;
}

.loading-section,
.no-results-section {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    margin: 2rem 0;
}

.bg-blur {
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(10px);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .courses-header .display-6 {
        font-size: 1.75rem;
    }

    .search-container {
        max-width: 100%;
    }

    .search-input {
        font-size: 1rem;
        padding: 1rem 3.5rem 1rem 3.5rem;
    }

    .search-icon {
        left: 1.2rem;
        font-size: 1rem;
    }

    .btn-back-link {
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
    }

    .course-count-badge {
        font-size: 1rem;
        padding: 0.6rem 1.2rem;
    }

    .search-section .row {
        flex-direction: column;
    }
}

@media (max-width: 576px) {
    .search-input {
        font-size: 1rem;
        padding: 0.75rem 3rem 0.75rem 3rem;
    }

    .search-icon {
        left: 1rem;
        font-size: 0.9rem;
    }

    .modal-dialog {
        margin: 0.5rem;
    }
}
</style>

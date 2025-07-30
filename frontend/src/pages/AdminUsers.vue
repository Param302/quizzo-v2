<template>
    <div class="admin-users-page">
        <!-- Header Section -->
        <section class="users-header py-4 bg-blur">
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
                                <h1 class="display-6 fw-bold mb-2 text-orange">User Management</h1>
                                <p class="lead fw-medium mb-0">Manage and monitor all registered users</p>
                            </div>
                            <div class="col-md-4 text-md-end mt-3 mt-md-0">
                                <div class="total-users-badge">
                                    <span class="badge users-count-badge">
                                        <i class="bi bi-people-fill me-2"></i>
                                        Total Users: {{ totalUsers }}
                                    </span>
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
                        <div class="search-container mx-auto mb-4">
                            <div class="search-wrapper position-relative">
                                <i class="bi bi-search search-icon"></i>
                                <input type="text" class="form-control search-input"
                                    placeholder="Search users by name, username, or email..." v-model="searchQuery"
                                    @input="handleSearch">
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

        <!-- Users Grid Section -->
        <section class="users-grid-section pb-5">
            <div class="container">
                <!-- Loading State -->
                <div v-if="loading" class="loading-section">
                    <div class="text-center py-5">
                        <div class="spinner-border text-orange mb-3" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <h5 class="text-muted">Loading users...</h5>
                    </div>
                </div>

                <!-- No Results -->
                <div v-else-if="users.length === 0" class="no-results-section">
                    <div class="text-center py-5">
                        <i class="bi bi-people text-muted mb-3" style="font-size: 4rem;"></i>
                        <h4 class="text-muted mb-2">
                            {{ searchQuery ? 'No users found' : 'No users yet' }}
                        </h4>
                        <p class="text-muted">
                            {{ searchQuery ? 'Try adjusting your search criteria' : 'Users will appear here once they register' }}
                        </p>
                        <button v-if="searchQuery" class="btn btn-orange mt-3" @click="clearSearch">
                            <i class="bi bi-arrow-counterclockwise me-2"></i>
                            Clear Search
                        </button>
                    </div>
                </div>

                <!-- Users Grid -->
                <div v-else>
                    <!-- Users Cards Grid -->
                    <div class="row g-4">
                        <div v-for="user in users" :key="user.id" class="col-xl-4 col-lg-4 col-md-6">
                            <UserManagementCard :user="user" :deleting="deletingUserId === user.id" :loading="loading"
                                @delete-user="confirmDeleteUser" />
                        </div>
                    </div>

                    <!-- Pagination -->
                    <div v-if="pagination.total_pages > 1" class="pagination-section mt-5">
                        <nav aria-label="Users pagination">
                            <ul class="pagination justify-content-center">
                                <li class="page-item" :class="{ disabled: !pagination.has_prev }">
                                    <button class="page-link" @click="loadPage(pagination.current_page - 1)"
                                        :disabled="!pagination.has_prev">
                                        <i class="bi bi-chevron-left"></i>
                                    </button>
                                </li>

                                <li v-for="page in visiblePages" :key="page" class="page-item"
                                    :class="{ active: page === pagination.current_page }">
                                    <button class="page-link" @click="loadPage(page)">{{ page }}</button>
                                </li>

                                <li class="page-item" :class="{ disabled: !pagination.has_next }">
                                    <button class="page-link" @click="loadPage(pagination.current_page + 1)"
                                        :disabled="!pagination.has_next">
                                        <i class="bi bi-chevron-right"></i>
                                    </button>
                                </li>
                            </ul>
                        </nav>
                    </div>
                </div>
            </div>
        </section>

        <!-- Delete Confirmation Modal -->
        <DeleteConfirmationModal :show="showDeleteModal" title="Delete User Account"
            message="You are about to permanently delete this user account. This will remove all associated data including quiz attempts, subscriptions, and account information."
            :itemDetails="userToDelete"
            :loading="deletingUserId" @close="showDeleteModal = false" @confirm="deleteUser" />

        <!-- Toast Notifications -->
        <Toast v-if="toast.show" :message="toast.message" :variant="toast.type" @close="toast.show = false" />
    </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import UserManagementCard from '@/components/admin/UserManagementCard.vue'
import DeleteConfirmationModal from '@/components/DeleteConfirmationModal.vue'
import Toast from '@/components/Toast.vue'
import axios from 'axios'

export default {
    name: 'AdminUsers',
    components: {
        UserManagementCard,
        DeleteConfirmationModal,
        Toast
    },
    setup() {
        const users = ref([])
        const loading = ref(false)
        const searchQuery = ref('')
        const totalUsers = ref(0)
        const deletingUserId = ref(null)
        const showDeleteModal = ref(false)
        const userToDelete = ref(null)

        const pagination = ref({
            current_page: 1,
            per_page: 20,
            has_next: false,
            has_prev: false,
            total_pages: 1
        })

        const toast = ref({
            show: false,
            message: '',
            type: 'success'
        })

        let searchTimeout = null

        const visiblePages = computed(() => {
            const current = pagination.value.current_page
            const total = pagination.value.total_pages
            const pages = []

            let start = Math.max(1, current - 2)
            let end = Math.min(total, start + 4)

            if (end - start < 4) {
                start = Math.max(1, end - 4)
            }

            for (let i = start; i <= end; i++) {
                pages.push(i)
            }

            return pages
        })

        const loadUsers = async (page = 1, search = '') => {
            loading.value = true
            try {
                const params = {
                    page: page,
                    per_page: pagination.value.per_page
                }

                if (search.trim()) {
                    params.search = search.trim()
                }

                const response = await axios.get('/admin/users', { params })
                const data = response.data

                users.value = data.users
                totalUsers.value = data.total_users

                pagination.value = {
                    current_page: data.page,
                    per_page: data.per_page,
                    has_next: data.has_next,
                    has_prev: data.has_prev,
                    total_pages: Math.ceil(data.total_users / data.per_page)
                }
            } catch (error) {
                console.error('Error loading users:', error)
                showToast('Failed to load users', 'error')
            } finally {
                loading.value = false
            }
        }

        const handleSearch = () => {
            if (searchTimeout) {
                clearTimeout(searchTimeout)
            }

            searchTimeout = setTimeout(() => {
                pagination.value.current_page = 1
                loadUsers(1, searchQuery.value)
            }, 500)
        }

        const clearSearch = () => {
            searchQuery.value = ''
            pagination.value.current_page = 1
            loadUsers(1, '')
        }

        const loadPage = (page) => {
            if (page >= 1 && page <= pagination.value.total_pages) {
                loadUsers(page, searchQuery.value)
            }
        }

        const confirmDeleteUser = async (userId) => {
            const user = users.value.find(u => u.id === userId)
            if (!user) return

            userToDelete.value = user
            showDeleteModal.value = true
        }

        const deleteUser = async () => {
            if (!userToDelete.value) return

            deletingUserId.value = userToDelete.value.id
            try {
                const response = await axios.delete('/admin/users', {
                    data: { user_id: userToDelete.value.id }
                })

                // Remove user from local array
                users.value = users.value.filter(user => user.id !== userToDelete.value.id)
                totalUsers.value--

                showToast(response.data.message, 'success')
                showDeleteModal.value = false
                userToDelete.value = null

                // Reload if current page is empty
                if (users.value.length === 0 && pagination.value.current_page > 1) {
                    loadUsers(pagination.value.current_page - 1, searchQuery.value)
                }
            } catch (error) {
                console.error('Error deleting user:', error)
                showToast(error.response?.data?.message || 'Failed to delete user', 'error')
            } finally {
                deletingUserId.value = null
            }
        }

        const showToast = (message, type = 'success') => {
            toast.value = { show: true, message, type }
            setTimeout(() => {
                toast.value.show = false
            }, 5000)
        }

        onMounted(() => {
            loadUsers()
        })

        return {
            users,
            loading,
            searchQuery,
            totalUsers,
            deletingUserId,
            showDeleteModal,
            userToDelete,
            pagination,
            visiblePages,
            toast,
            loadUsers,
            handleSearch,
            clearSearch,
            loadPage,
            confirmDeleteUser,
            deleteUser,
            showToast
        }
    }
}
</script>

<style scoped>
.admin-users-page {
    min-height: 100vh;
    background: linear-gradient(135deg, rgba(245, 124, 0, 0.05) 0%, rgba(245, 124, 0, 0.02) 100%);
}

.users-header {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(245, 124, 0, 0.1);
}

.text-orange {
    color: #f57c00;
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
}

.btn-orange:hover {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.4);
}

.users-count-badge {
    background: rgba(245, 124, 0, 0.1);
    color: #f57c00;
    border: 1px solid rgba(245, 124, 0, 0.2);
    padding: 0.75rem 1.5rem;
    border-radius: 25px;
    font-size: 1rem;
    font-weight: 600;
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

.avatar-circle {
    width: 50px;
    height: 50px;
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.4rem;
}

.user-delete-info {
    background: rgba(220, 53, 69, 0.05);
    border: 1px solid rgba(220, 53, 69, 0.1);
    border-radius: 12px;
    padding: 1rem;
}

.modal-backdrop {
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(5px);
}

.modal-content {
    border-radius: 20px;
    border: none;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
    background: #ffffff;
}

.pagination .page-link {
    border: 1px solid rgba(245, 124, 0, 0.2);
    color: #f57c00;
    border-radius: 8px;
    margin: 0 2px;
    font-weight: 600;
}

.pagination .page-item.active .page-link {
    background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
    border-color: #f57c00;
}

.pagination .page-link:hover {
    background: rgba(245, 124, 0, 0.1);
    border-color: #f57c00;
}

.bg-blur {
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(10px);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .users-header .display-6 {
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

    .users-count-badge {
        font-size: 0.9rem;
        padding: 0.5rem 1rem;
    }

    .btn-back-link {
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
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

    .users-count-badge {
        font-size: 0.8rem;
        padding: 0.4rem 0.8rem;
    }
}
</style>
<template>
    <nav class="navbar navbar-expand-lg fixed-top bg-transparent border-bottom modern-navbar">
        <div class="container">
            <router-link to="/" class="navbar-brand fw-bold fs-2 animated-brand">
                <span class="brand-text">Quizzo</span>
            </router-link>

            <button class="navbar-toggler custom-toggler" type="button" data-bs-toggle="collapse"
                data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false"
                aria-label="Toggle navigation">
                <span></span>
                <span></span>
                <span></span>
            </button>

            <!-- Navigation -->
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto align-items-lg-center">
                    <li class="nav-item me-2" v-if="!authStore.isAuthenticated">
                        <router-link to="/register" class="btn btn-outline-secondary rounded-pill px-4">
                            Sign Up
                        </router-link>
                    </li>
                    <li class="nav-item" v-if="!authStore.isAuthenticated">
                        <router-link to="/login" class="btn btn-primary rounded-pill px-4">
                            Dashboard
                        </router-link>
                    </li>

                    <!-- Admin Navigation -->
                    <template v-if="authStore.isAuthenticated && authStore.isAdmin">
                        <li class="nav-item">
                            <router-link to="/admin" class="btn btn-primary rounded-pill px-4">
                                Admin Dashboard
                            </router-link>
                        </li>
                    </template>

                    <!-- Regular User Navigation -->
                    <li class="nav-item" v-else-if="authStore.isAuthenticated">
                        <router-link to="/dashboard" class="btn btn-primary rounded-pill px-4">
                            Dashboard
                        </router-link>
                    </li>

                    <li v-if="authStore.isAuthenticated" class="nav-item dropdown d-none d-lg-block ms-3">
                        <a class="nav-link user-avatar" href="#" role="button" data-bs-toggle="dropdown">
                            <div class="avatar-circle">
                                {{ userInitials }}
                            </div>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end custom-dropdown">
                            <!-- Profile only for regular users -->
                            <li v-if="!authStore.isAdmin">
                                <router-link :to="`/u/@${authStore.user?.username || ''}`" class="dropdown-item">
                                    <i class="bi bi-person me-2"></i>
                                    Profile
                                </router-link>
                            </li>
                            <!-- Admin specific items -->
                            <li v-if="authStore.isAdmin">
                                <router-link to="/admin/manage/course" class="dropdown-item">
                                    <i class="bi bi-book me-2"></i>
                                    Manage Courses
                                </router-link>
                            </li>
                            <li v-if="authStore.isAdmin">
                                <router-link to="/admin/manage/users" class="dropdown-item">
                                    <i class="bi bi-people me-2"></i>
                                    Manage Users
                                </router-link>
                            </li>
                            <li>
                                <hr class="dropdown-divider" />
                            </li>
                            <li>
                                <button @click="handleLogout" class="dropdown-item text-danger" type="button">
                                    <i class="bi bi-box-arrow-right me-2"></i>
                                    Logout
                                </button>
                            </li>
                        </ul>
                    </li>

                    <li v-if="authStore.isAuthenticated" class="nav-item d-lg-none w-100">
                        <div class="mobile-user-info">
                            <div class="d-flex align-items-center mb-2">
                                <div class="avatar-circle me-2">
                                    {{ userInitials }}
                                </div>
                                <span class="text-white">{{ authStore.userName }}</span>
                            </div>
                            <div class="mobile-menu-items">
                                <!-- Profile only for regular users -->
                                <router-link v-if="!authStore.isAdmin" :to="`/u/@${authStore.user?.username || ''}`"
                                    class="mobile-menu-item">
                                    <i class="bi bi-person me-2"></i>
                                    Profile
                                </router-link>
                                <!-- Admin specific items -->
                                <router-link v-if="authStore.isAdmin" to="/admin/manage/course"
                                    class="mobile-menu-item">
                                    <i class="bi bi-book me-2"></i>
                                    Manage Courses
                                </router-link>
                                <router-link v-if="authStore.isAdmin" to="/admin/manage/users" class="mobile-menu-item">
                                    <i class="bi bi-people me-2"></i>
                                    Manage Users
                                </router-link>
                                <button @click="handleLogout"
                                    class="mobile-menu-item text-danger border-0 bg-transparent" type="button">
                                    <i class="bi bi-box-arrow-right me-2"></i>
                                    Logout
                                </button>
                            </div>
                        </div>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const userInitials = computed(() => {
    const name = authStore.userName
    if (!name) return 'U'
    const parts = name.split(' ')
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase()
    }
    return name[0].toUpperCase()
})

const handleLogout = async () => {
    await authStore.logout()
    router.push('/')
}

// Handle navbar scroll effect
const handleScroll = () => {
    const navbarElement = document.querySelector('.modern-navbar')
    if (navbarElement) {
        if (window.scrollY > 50) {
            navbarElement.classList.add('scrolled')
        } else {
            navbarElement.classList.remove('scrolled')
        }
    }
}

onMounted(() => {
    window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* Modern Transparent Navbar */
.modern-navbar {
    background-color: transparent;
    backdrop-filter: blur(5px);
    -webkit-backdrop-filter: blur(5px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    padding: 1rem 0;
    transition: background-color 0.3s, box-shadow 0.3s;
    z-index: 1050;
}

.modern-navbar.scrolled {
    background-color: rgba(255, 255, 255, 0.95);
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

/* Animated Brand */
.animated-brand {
    color: var(--primary);
    transition: color 0.3s, transform 0.3s;
    text-shadow: none;
    text-decoration: none;
}

.animated-brand:hover {
    color: var(--primary-dark);
    transform: scale(1.02);
}

.brand-text {
    position: relative;
    display: inline-block;
}

/* Custom Toggler */
.custom-toggler {
    border: none;
    padding: 4px 8px;
    background: transparent;
    width: 30px;
    height: 24px;
    box-shadow: none;
}

.custom-toggler span {
    display: block;
    width: 22px;
    height: 2px;
    background: var(--primary);
    margin: 4px 0;
    transition: transform 0.3s, opacity 0.3s;
    border-radius: 2px;
}

.custom-toggler:not(.collapsed) span:nth-child(1) {
    transform: rotate(45deg) translate(5px, 5px);
}

.custom-toggler:not(.collapsed) span:nth-child(2) {
    opacity: 0;
}

.custom-toggler:not(.collapsed) span:nth-child(3) {
    transform: rotate(-45deg) translate(7px, -6px);
}

/* Button Styles */
.btn-outline-secondary {
    border: 2px solid rgba(255, 255, 255, 0.3);
    color: rgba(255, 255, 255, 0.9);
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    font-weight: 600;
    transition: background 0.3s, color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
    position: relative;
    overflow: hidden;
}

.btn-outline-secondary:hover {
    border-color: rgba(255, 255, 255, 0.5);
    background: rgba(255, 255, 255, 0.2);
    color: #fff;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    border: none;
    font-weight: 600;
    transition: background 0.3s, box-shadow 0.3s, transform 0.3s;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.btn-primary:hover {
    background: linear-gradient(135deg, var(--primary-dark) 0%, #d84315 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(245, 124, 0, 0.4);
}

.btn-primary::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s;
    pointer-events: none;
}

.btn-primary:hover::before {
    left: 100%;
}

/* Avatar Styles */
.nav-hover {
    color: rgba(255, 255, 255, 0.9);
    transition: all 0.3s ease;
    position: relative;
    padding: 0.75rem 1rem;
    border-radius: 25px;
}

.nav-hover:hover,
.nav-hover.active {
    color: #f57c00 !important;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
}

.nav-hover.active {
    background: rgba(245, 124, 0, 0.1);
    color: #f57c00 !important;
}

.user-avatar {
    text-decoration: none;
    transition: color 0.3s;
    padding: 0;
    border: none;
    background: transparent;
}

.user-avatar::after {
    display: none;
}

.avatar-circle {
    width: 40px;
    height: 40px;
    background: transparent;
    border: 2px solid #f57c00;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #f57c00;
    font-weight: 600;
    font-size: 14px;
    transition: all 0.3s ease;
    cursor: pointer;
}

.user-avatar:hover .avatar-circle {
    background: #f57c00;
    color: white;
    transform: scale(1.05);
}

/* Dropdown Styles */
.custom-dropdown {
    border: none;
    background: white;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    border-radius: 12px;
    margin-top: 0.5rem;
    padding: 0.75rem 0;
    min-width: 200px;
    transform: translateX(-10px);
}

.dropdown-item {
    color: #2c3e50;
    padding: 0.75rem 1.25rem;
    transition: all 0.2s ease;
    border-radius: 0;
    margin: 0;
    display: flex;
    align-items: center;
    font-size: 0.9rem;
    font-weight: 500;
}

.dropdown-item:hover {
    background: rgba(245, 124, 0, 0.1);
    color: #f57c00;
    transform: none;
}

.dropdown-item:active {
    background: rgba(245, 124, 0, 0.15);
    color: #f57c00;
}

.dropdown-item.text-danger {
    color: #dc3545;
}

.dropdown-item.text-danger:hover {
    background: rgba(220, 53, 69, 0.1);
    color: #dc3545;
}

.dropdown-divider {
    margin: 0.5rem 0;
    border-color: rgba(0, 0, 0, 0.1);
}

/* Mobile Styles */
.mobile-user-info {
    padding: 1rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    margin: 1rem 0;
    backdrop-filter: blur(10px);
}

.mobile-user-info .avatar-circle {
    width: 35px;
    height: 35px;
    font-size: 12px;
    background: transparent;
    border: 2px solid #f57c00;
    color: #f57c00;
}

.mobile-menu-items {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.mobile-menu-item {
    color: rgba(255, 255, 255, 0.9);
    text-decoration: none;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    width: 100%;
    text-align: left;
    font-size: 0.9rem;
    font-weight: 500;
}

.mobile-menu-item:hover {
    background: rgba(245, 124, 0, 0.2);
    color: #fff;
    transform: translateX(5px);
}

.mobile-menu-item.text-danger {
    color: #ff6b6b;
}

.mobile-menu-item.text-danger:hover {
    background: rgba(255, 107, 107, 0.2);
    color: #ff6b6b;
}

/* Responsive Design */
@media (max-width: 1199.98px) {
    .custom-dropdown {
        transform: translateX(-20px);
        min-width: 180px;
    }
}

@media (max-width: 991.98px) {
    .navbar-collapse {
        background: rgba(0, 0, 0, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 12px;
        margin-top: 1rem;
        padding: 1.5rem;
        border: 1px solid rgba(245, 124, 0, 0.2);
    }

    .animated-brand {
        font-size: 1.75rem;
    }

    .btn-outline-secondary,
    .btn-primary {
        width: 100%;
        margin: 0.25rem 0;
        padding: 0.75rem 1.5rem;
    }

    .nav-item {
        margin: 0.25rem 0;
    }
}

@media (max-width: 767.98px) {
    .animated-brand {
        font-size: 1.5rem;
    }

    .modern-navbar {
        padding: 0.75rem 0;
    }

    .mobile-user-info {
        margin: 0.75rem 0;
        padding: 0.75rem;
    }

    .mobile-menu-item {
        padding: 0.6rem 0.75rem;
        font-size: 0.85rem;
    }

    .custom-toggler {
        width: 28px;
        height: 22px;
    }
}

/* Admin Navigation Styles */
.nav-link {
    color: rgba(255, 255, 255, 0.9);
    transition: color 0.3s ease;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    position: relative;
}

.nav-link:hover {
    color: var(--primary);
    background: rgba(255, 255, 255, 0.1);
}

.nav-link.router-link-active {
    color: var(--primary) !important;
    background: rgba(255, 255, 255, 0.15);
}

.modern-navbar.scrolled .nav-link {
    color: rgba(108, 117, 125, 0.9);
}

.modern-navbar.scrolled .nav-link:hover {
    color: var(--primary);
    background: rgba(245, 124, 0, 0.1);
}

.modern-navbar.scrolled .nav-link.router-link-active {
    color: var(--primary) !important;
    background: rgba(245, 124, 0, 0.15);
}

@media (max-width: 991.98px) {
    .custom-toggler span {
        width: 20px;
        height: 2px;
        margin: 3px 0;
    }
}

@media (max-width: 575.98px) {
    .animated-brand {
        font-size: 1.3rem;
    }

    .modern-navbar {
        padding: 0.6rem 0;
    }

    .navbar-collapse {
        padding: 1rem;
        margin-top: 0.75rem;
    }

    .mobile-user-info {
        padding: 0.6rem;
        margin: 0.5rem 0;
    }

    .mobile-user-info .avatar-circle {
        width: 32px;
        height: 32px;
        font-size: 11px;
    }

    .btn-outline-secondary,
    .btn-primary {
        padding: 0.6rem 1.25rem;
        font-size: 0.9rem;
    }

    :global(body) {
        padding-top: 65px;
    }
}
</style>